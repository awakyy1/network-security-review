"""Generate V1.1 CTU-13 window, rule-feature, and error diagnostics."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .behavior_detector import BehaviorDetector
from .ctu13_acquire import load_manifest, sha256_file
from .ctu13_experiment import (
    EXTERNALLY_EVALUABLE_RULES,
    ParseCounters,
    binary_metrics,
    iter_labeled_windows,
)
from .telemetry import TelemetryEvent

DEFAULT_WINDOW_SECONDS = (60, 300, 600)


def _sha256_record(path: Path, repository_root: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(repository_root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _scientific_state(repository_root: Path) -> dict[str, Any]:
    paths = [
        repository_root / "src" / "behavior_detector.py",
        repository_root / "src" / "ctu13_acquire.py",
        repository_root / "src" / "ctu13_analysis.py",
        repository_root / "src" / "ctu13_experiment.py",
        repository_root / "src" / "telemetry.py",
        repository_root / "requirements.txt",
        repository_root / "requirements-dev.txt",
    ]
    try:
        base_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError(f"Unable to identify repository base commit: {error}") from error
    return {
        "repository_base_commit": base_commit,
        "python_version": sys.version,
        "files": [_sha256_record(path, repository_root) for path in paths],
    }


def preserve_analysis(
    source_directory: str | Path,
    destination_directory: str | Path,
    repository_root: str | Path,
) -> dict[str, Any]:
    source = Path(source_directory).resolve()
    destination = Path(destination_directory).resolve()
    root = Path(repository_root).resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Preservation destination is not empty: {destination}")
    result_path = source / "ctu13-window-analysis.json"
    report_path = source / "ctu13-window-analysis.md"
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to load CTU-13 analysis for preservation: {error}") from error
    if not isinstance(result, dict) or result.get("analysis_role") != "development_and_historical_holdout_diagnostics":
        raise ValueError("Only a V1.1 retrospective CTU-13 diagnostic result can be preserved here")
    for record in result.get("scientific_state", {}).get("files", []):
        path = (root / record["path"]).resolve()
        if not path.is_file() or sha256_file(path) != record["sha256"]:
            raise ValueError(f"Scientific source state changed after execution: {record['path']}")

    destination.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for path in (result_path, report_path):
        if not path.is_file():
            raise ValueError(f"Missing analysis artifact: {path}")
        target = destination / path.name
        shutil.copyfile(path, target)
        digest = sha256_file(path)
        if sha256_file(target) != digest:
            raise ValueError(f"Hash mismatch after preserving {path.name}")
        artifacts.append({"filename": path.name, "bytes": path.stat().st_size, "sha256": digest})

    provenance = {
        "schema_version": "1.0",
        "preserved_at": datetime.now(timezone.utc).isoformat(),
        "evidence_role": "retrospective_diagnostic_not_confirmatory_holdout",
        "execution_source_state": "exact_file_hashes_embedded_and_reverified",
        "repository_base_commit": result["scientific_state"]["repository_base_commit"],
        "scientific_state_files": result["scientific_state"]["files"],
        "artifacts": artifacts,
    }
    (destination / "provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return provenance


def _quantile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def summarize_distribution(values: Iterable[float]) -> dict[str, float | int | None]:
    materialized = list(values)
    return {
        "count": len(materialized),
        "minimum": round(min(materialized), 6) if materialized else None,
        "q1": round(_quantile(materialized, 0.25), 6) if materialized else None,
        "median": round(_quantile(materialized, 0.5), 6) if materialized else None,
        "q3": round(_quantile(materialized, 0.75), 6) if materialized else None,
        "maximum": round(max(materialized), 6) if materialized else None,
    }


def _maximum_distinct_endpoints(events: list[TelemetryEvent], seconds: int = 60) -> int:
    groups: dict[tuple[str, str], list[TelemetryEvent]] = defaultdict(list)
    for event in events:
        if event.event_type == "network_connection":
            groups[(event.host, event.process)].append(event)
    maximum = 0
    for group in groups.values():
        ordered = sorted(group, key=lambda item: item.timestamp)
        endpoint_counts: Counter[tuple[str, int | None]] = Counter()
        right = 0
        for first in ordered:
            while right < len(ordered) and (ordered[right].timestamp - first.timestamp).total_seconds() <= seconds:
                endpoint = (
                    ordered[right].destination_ip or ordered[right].destination_domain,
                    ordered[right].destination_port,
                )
                endpoint_counts[endpoint] += 1
                right += 1
            maximum = max(maximum, len(endpoint_counts))
            first_endpoint = (first.destination_ip or first.destination_domain, first.destination_port)
            endpoint_counts[first_endpoint] -= 1
            if endpoint_counts[first_endpoint] == 0:
                del endpoint_counts[first_endpoint]
    return maximum


def _periodicity_diagnostics(events: list[TelemetryEvent]) -> dict[str, float | int | None]:
    groups: dict[tuple[str, str, str, int | None], list[TelemetryEvent]] = defaultdict(list)
    for event in events:
        if event.event_type != "network_connection":
            continue
        destination = event.destination_domain or event.destination_ip
        groups[(event.host, event.process, destination, event.destination_port)].append(event)

    maximum_connections = max((len(group) for group in groups.values()), default=0)
    eligible: list[tuple[float, float]] = []
    for group in groups.values():
        if len(group) < 6:
            continue
        ordered = sorted(group, key=lambda item: item.timestamp)
        intervals = [
            (current.timestamp - previous.timestamp).total_seconds() for previous, current in zip(ordered, ordered[1:])
        ]
        mean_interval = statistics.fmean(intervals)
        if not 5 <= mean_interval <= 900:
            continue
        coefficient = statistics.pstdev(intervals) / mean_interval if mean_interval else math.inf
        eligible.append((coefficient, mean_interval))

    if not eligible:
        return {
            "maximum_connections_to_one_endpoint": maximum_connections,
            "eligible_endpoint_groups": 0,
            "minimum_interval_cv": None,
            "mean_interval_at_minimum_cv_seconds": None,
        }
    coefficient, mean_interval = min(eligible)
    return {
        "maximum_connections_to_one_endpoint": maximum_connections,
        "eligible_endpoint_groups": len(eligible),
        "minimum_interval_cv": round(coefficient, 6),
        "mean_interval_at_minimum_cv_seconds": round(mean_interval, 6),
    }


def unit_rule_features(events: Iterable[TelemetryEvent]) -> dict[str, Any]:
    materialized = list(events)
    connections = [event for event in materialized if event.event_type == "network_connection"]
    ratios = [event.bytes_sent / max(event.bytes_received, 1) for event in connections]
    high_volume = [event for event in connections if event.bytes_sent >= 1_000_000]
    high_ratio = [event for event in connections if event.bytes_sent / max(event.bytes_received, 1) >= 10]
    return {
        "event_count": len(materialized),
        "maximum_distinct_endpoints_in_60_seconds": _maximum_distinct_endpoints(materialized),
        "periodicity": _periodicity_diagnostics(materialized),
        "maximum_bytes_sent_on_one_connection": max((event.bytes_sent for event in connections), default=0),
        "maximum_sent_received_ratio": round(max(ratios), 6) if ratios else 0.0,
        "connections_meeting_1mb_sent": len(high_volume),
        "connections_meeting_10_to_1_ratio": len(high_ratio),
        "connections_meeting_both_beh_003_thresholds": sum(
            event.bytes_sent >= 1_000_000 and event.bytes_sent / max(event.bytes_received, 1) >= 10
            for event in connections
        ),
        "maximum_ratio_among_1mb_connections": (
            round(max(event.bytes_sent / max(event.bytes_received, 1) for event in high_volume), 6)
            if high_volume
            else None
        ),
        "maximum_bytes_sent_among_10_to_1_connections": (
            max(event.bytes_sent for event in high_ratio) if high_ratio else None
        ),
    }


def _classification(truth: str, predicted: bool) -> str:
    if truth == "botnet-origin":
        return "true_positive" if predicted else "false_negative"
    return "false_positive" if predicted else "true_negative"


def _beh_001_diagnostics(units: list[dict[str, Any]], truth: str) -> dict[str, int]:
    matching = [unit for unit in units if unit["truth"] == truth]
    return {
        "units": len(matching),
        "below_six_connections_to_one_endpoint": sum(
            unit["features"]["periodicity"]["maximum_connections_to_one_endpoint"] < 6 for unit in matching
        ),
        "six_connections_but_no_eligible_mean_interval": sum(
            unit["features"]["periodicity"]["maximum_connections_to_one_endpoint"] >= 6
            and unit["features"]["periodicity"]["eligible_endpoint_groups"] == 0
            for unit in matching
        ),
        "eligible_mean_interval_but_cv_above_0_15": sum(
            unit["features"]["periodicity"]["minimum_interval_cv"] is not None
            and unit["features"]["periodicity"]["minimum_interval_cv"] > 0.15
            for unit in matching
        ),
        "meets_beh_001_thresholds": sum(
            unit["features"]["periodicity"]["minimum_interval_cv"] is not None
            and unit["features"]["periodicity"]["minimum_interval_cv"] <= 0.15
            for unit in matching
        ),
    }


def analyze_source(
    path: str | Path,
    *,
    scenario: int,
    family: str,
    role: str,
    window_seconds: int,
) -> dict[str, Any]:
    counters = ParseCounters()
    detector = BehaviorDetector()
    confusion: Counter[str] = Counter()
    distributions: dict[str, dict[str, list[float]]] = {
        truth: defaultdict(list) for truth in ("botnet-origin", "normal-origin")
    }
    examples: dict[str, dict[str, Any]] = {}
    units: list[dict[str, Any]] = []

    for unit in iter_labeled_windows(
        path,
        scenario=scenario,
        window_seconds=window_seconds,
        counters=counters,
    ):
        findings = [
            finding for finding in detector.analyze(list(unit.events)) if finding.rule_id in EXTERNALLY_EVALUABLE_RULES
        ]
        predicted = bool(findings)
        classification = _classification(unit.truth, predicted)
        confusion[classification] += 1
        features = unit_rule_features(unit.events)
        distributions[unit.truth]["maximum_distinct_endpoints_in_60_seconds"].append(
            features["maximum_distinct_endpoints_in_60_seconds"]
        )
        distributions[unit.truth]["maximum_bytes_sent_on_one_connection"].append(
            features["maximum_bytes_sent_on_one_connection"]
        )
        distributions[unit.truth]["maximum_sent_received_ratio"].append(features["maximum_sent_received_ratio"])
        minimum_cv = features["periodicity"]["minimum_interval_cv"]
        if minimum_cv is not None:
            distributions[unit.truth]["minimum_interval_cv"].append(minimum_cv)

        finding_evidence_ids = sorted({evidence_id for finding in findings for evidence_id in finding.evidence_ids})
        record = {
            "host": unit.host,
            "window_start": unit.window_start.isoformat(),
            "truth": unit.truth,
            "classification": classification,
            "predicted_review": predicted,
            "rule_ids": sorted({finding.rule_id for finding in findings}),
            "finding_ids": [finding.finding_id for finding in findings],
            "evidence_ids": finding_evidence_ids or [event.event_id for event in unit.events[:20]],
            "features": features,
        }
        units.append(record)
        if classification in {"true_positive", "false_positive", "false_negative"}:
            examples.setdefault(classification, record)

    metrics = binary_metrics(
        confusion["true_positive"],
        confusion["false_positive"],
        confusion["false_negative"],
        confusion["true_negative"],
    )
    summaries = {
        truth: {feature: summarize_distribution(values) for feature, values in truth_features.items()}
        for truth, truth_features in distributions.items()
    }
    beh_003 = {
        truth: {
            "units_meeting_1mb_sent": sum(
                unit["features"]["connections_meeting_1mb_sent"] > 0 for unit in units if unit["truth"] == truth
            ),
            "units_meeting_10_to_1_ratio": sum(
                unit["features"]["connections_meeting_10_to_1_ratio"] > 0 for unit in units if unit["truth"] == truth
            ),
            "units_meeting_both_thresholds": sum(
                unit["features"]["connections_meeting_both_beh_003_thresholds"] > 0
                for unit in units
                if unit["truth"] == truth
            ),
        }
        for truth in ("botnet-origin", "normal-origin")
    }
    beh_001 = {truth: _beh_001_diagnostics(units, truth) for truth in ("botnet-origin", "normal-origin")}
    return {
        "scenario": scenario,
        "family": family,
        "role": role,
        "window_seconds": window_seconds,
        "source": {
            "filename": Path(path).name,
            "bytes": Path(path).stat().st_size,
            "sha256": sha256_file(path),
        },
        "metrics": metrics,
        "parse_counts": vars(counters),
        "feature_distributions": summaries,
        "beh_001_threshold_diagnostics": beh_001,
        "beh_003_threshold_diagnostics": beh_003,
        "examples": examples,
        "units": units,
    }


def run_window_analysis(
    manifest_path: str | Path,
    data_directory: str | Path,
    output_directory: str | Path,
    *,
    window_seconds: tuple[int, ...] = DEFAULT_WINDOW_SECONDS,
) -> dict[str, Any]:
    manifest_file = Path(manifest_path).resolve()
    repository_root = Path(__file__).resolve().parent.parent
    manifest = load_manifest(manifest_file)
    data_root = Path(data_directory).resolve()
    output = Path(output_directory).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if not window_seconds or any(seconds < 60 or seconds > 3600 for seconds in window_seconds):
        raise ValueError("Window analysis requires values between 60 and 3600 seconds")

    analyses = []
    for source in manifest["sources"]:
        source_path = data_root / source["filename"]
        if not source_path.is_file():
            raise ValueError(f"Missing frozen CTU-13 file: {source_path}")
        if sha256_file(source_path).lower() != source["sha256"].lower():
            raise ValueError(f"CTU-13 SHA-256 mismatch for {source['filename']}")
        for seconds in window_seconds:
            analyses.append(
                analyze_source(
                    source_path,
                    scenario=source["scenario"],
                    family=source["family"],
                    role=source["role"],
                    window_seconds=seconds,
                )
            )

    result = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_role": "development_and_historical_holdout_diagnostics",
        "confirmatory_warning": (
            "The V1.0 holdout has already been inspected. Window and feature analyses are diagnostic and cannot "
            "turn it back into an untouched holdout."
        ),
        "manifest": manifest_file.name,
        "manifest_sha256": sha256_file(manifest_file),
        "scientific_state": _scientific_state(repository_root),
        "window_seconds": list(window_seconds),
        "analyses": analyses,
    }
    json_path = output / "ctu13-window-analysis.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "ctu13-window-analysis.md").write_text(_markdown_report(result), encoding="utf-8")
    return result


def _markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# V1.1 retrospective CTU-13 detector diagnostics",
        "",
        f"> {result['confirmatory_warning']}",
        "",
        "## Window-size metrics",
        "",
        "| Role | Family | Window (s) | Units | TP | FP | FN | TN | F1 | Specificity | MCC |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for analysis in result["analyses"]:
        metrics = analysis["metrics"]
        units = sum(metrics[key] for key in ("true_positive", "false_positive", "false_negative", "true_negative"))
        lines.append(
            f"| {analysis['role']} | {analysis['family']} | {analysis['window_seconds']} | {units} | "
            f"{metrics['true_positive']} | {metrics['false_positive']} | {metrics['false_negative']} | "
            f"{metrics['true_negative']} | {metrics['f1']:.3f} | {metrics['specificity']:.3f} | "
            f"{metrics['matthews_correlation_coefficient']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Five-minute rule diagnostics",
            "",
            "| Role | Truth | BEH-001 <6 | No eligible mean | CV >0.15 | BEH-001 match | BEH-003 >=1 MB | Ratio >=10 | Both |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for analysis in (item for item in result["analyses"] if item["window_seconds"] == 300):
        for truth in ("botnet-origin", "normal-origin"):
            beh_001 = analysis["beh_001_threshold_diagnostics"][truth]
            beh_003 = analysis["beh_003_threshold_diagnostics"][truth]
            lines.append(
                f"| {analysis['role']} | {truth} | {beh_001['below_six_connections_to_one_endpoint']} | "
                f"{beh_001['six_connections_but_no_eligible_mean_interval']} | "
                f"{beh_001['eligible_mean_interval_but_cv_above_0_15']} | "
                f"{beh_001['meets_beh_001_thresholds']} | {beh_003['units_meeting_1mb_sent']} | "
                f"{beh_003['units_meeting_10_to_1_ratio']} | {beh_003['units_meeting_both_thresholds']} |"
            )
    lines.extend(
        [
            "",
            "BEH-003 is diagnosed component by component; absence of a rule match is not treated as proof that",
            "the underlying behavior was absent. The adapter exposes source and reverse byte counts per flow,",
            "but NetFlow contains no process or file lineage.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=repository_root / "research" / "v2" / "ctu13_manifest.json")
    parser.add_argument("--data-dir", type=Path, default=repository_root / "data" / "ctu13")
    parser.add_argument("--output-dir", type=Path, default=repository_root / "output" / "v1.1-ctu13-analysis")
    parser.add_argument("--window-seconds", type=int, nargs="+", default=list(DEFAULT_WINDOW_SECONDS))
    parser.add_argument(
        "--preserve-dir",
        type=Path,
        help="Optional empty V1.1 evidence directory; refuses preservation if source hashes changed",
    )
    arguments = parser.parse_args(argv)
    try:
        result = run_window_analysis(
            arguments.manifest,
            arguments.data_dir,
            arguments.output_dir,
            window_seconds=tuple(arguments.window_seconds),
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Analyses: {len(result['analyses'])}")
    print(f"Output: {Path(arguments.output_dir) / 'ctu13-window-analysis.json'}")
    if arguments.preserve_dir is not None:
        provenance = preserve_analysis(arguments.output_dir, arguments.preserve_dir, repository_root)
        print(f"Preserved: {arguments.preserve_dir} ({len(provenance['artifacts'])} artifacts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
