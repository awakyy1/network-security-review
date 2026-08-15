"""Tune on the frozen CTU-13 development source and run the holdout once."""

from __future__ import annotations

import argparse
import itertools
import json
import shutil
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .behavior_detector import BehaviorDetector, DetectorThresholds
from .ctu13_acquire import sha256_file
from .ctu13_experiment import (
    EXTERNALLY_EVALUABLE_RULES,
    ParseCounters,
    binary_metrics,
    evaluate_binetflow,
    iter_labeled_windows,
)

GRID_FIELDS = (
    "beh_001_minimum_connections",
    "beh_001_maximum_interval_cv",
    "beh_001_minimum_mean_interval_seconds",
    "beh_001_maximum_mean_interval_seconds",
    "beh_002_minimum_distinct_endpoints",
    "beh_002_interval_seconds",
    "beh_003_minimum_bytes_sent",
    "beh_003_minimum_sent_received_ratio",
)
SCIENTIFIC_STATE_PATHS = (
    "src/behavior_detector.py",
    "src/ctu13_acquire.py",
    "src/ctu13_confirmatory.py",
    "src/ctu13_experiment.py",
    "src/telemetry.py",
    "requirements.txt",
    "requirements-dev.txt",
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _scientific_state(repository_root: Path) -> list[dict[str, Any]]:
    state = []
    for relative in SCIENTIFIC_STATE_PATHS:
        path = repository_root / relative
        if not path.is_file():
            raise ValueError(f"Missing scientific-state file: {path}")
        state.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return state


def _verify_scientific_state(repository_root: Path, expected: Iterable[dict[str, Any]]) -> None:
    observed = {item["path"]: item for item in _scientific_state(repository_root)}
    expected_by_path = {item["path"]: item for item in expected}
    if observed != expected_by_path:
        raise ValueError("Scientific source state changed after development freeze; holdout execution is prohibited")


def _load_source(
    *,
    selection_path: Path,
    acquisition_path: Path,
    data_directory: Path,
    role: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], Path]:
    selection = _read_json(selection_path)
    acquisition = _read_json(acquisition_path)
    if sha256_file(selection_path) != acquisition["selection_record_corrected_sha256"]:
        raise ValueError("Corrected selection record does not match the acquisition manifest")
    selected_sources = {source["role"]: source for source in selection["sources"]}
    acquired_sources = {source["role"]: source for source in acquisition["sources"]}
    if role not in selected_sources or role not in acquired_sources:
        raise ValueError(f"Missing unique {role} source")
    selected = selected_sources[role]
    acquired = acquired_sources[role]
    for field in ("scenario", "family", "role", "filename", "url", "content_length", "etag", "last_modified"):
        acquisition_field = "expected_bytes" if field == "content_length" else field
        if selected[field] != acquired[acquisition_field]:
            raise ValueError(f"Selection/acquisition mismatch for {role} field {field}")
    path = (data_directory / acquired["filename"]).resolve()
    if path.parent != data_directory.resolve() or not path.is_file():
        raise ValueError(f"Missing safely resolved {role} source: {path}")
    if path.stat().st_size != acquired["observed_bytes"] or sha256_file(path) != acquired["sha256"]:
        raise ValueError(f"Acquired {role} source failed size or SHA-256 verification")
    return selection, acquisition, acquired, path


def _grid_candidates(selection: dict[str, Any]) -> list[DetectorThresholds]:
    protocol = selection["threshold_selection"]
    grid = protocol["candidate_grid"]
    if tuple(grid) != GRID_FIELDS:
        raise ValueError("Candidate-grid fields or order differ from the frozen protocol")
    defaults = asdict(DetectorThresholds())
    candidates = []
    for values in itertools.product(*(grid[field] for field in GRID_FIELDS)):
        mapping = defaults | dict(zip(GRID_FIELDS, values))
        candidates.append(DetectorThresholds(**mapping))
    if len(candidates) != protocol["candidate_configurations"]:
        raise ValueError("Candidate-grid cardinality differs from the frozen protocol")
    return candidates


def _grid_distance(selection: dict[str, Any], thresholds: dict[str, Any]) -> int:
    protocol = selection["threshold_selection"]
    grid = protocol["candidate_grid"]
    reference = protocol["v1_0_reference"]
    return sum(abs(grid[field].index(thresholds[field]) - grid[field].index(reference[field])) for field in GRID_FIELDS)


def selection_sort_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    metrics = candidate["metrics"]
    thresholds = candidate["thresholds"]
    return (
        metrics["matthews_correlation_coefficient"],
        metrics["balanced_accuracy"],
        metrics["f1"],
        metrics["specificity"],
        -candidate["grid_distance_from_v1_0"],
        -candidate["alerted_units"],
        tuple(-float(thresholds[field]) for field in GRID_FIELDS),
    )


def _classification_counter(positive: bool, predicted: bool) -> str:
    if positive:
        return "tp" if predicted else "fn"
    return "fp" if predicted else "tn"


def _selected_units(
    path: Path,
    *,
    scenario: int,
    window_seconds: int,
    thresholds: DetectorThresholds,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    detector = BehaviorDetector(thresholds=thresholds)
    counters = ParseCounters()
    units = []
    rule_counts = {rule: Counter() for rule in sorted(EXTERNALLY_EVALUABLE_RULES)}
    for unit in iter_labeled_windows(path, scenario=scenario, window_seconds=window_seconds, counters=counters):
        findings = [
            finding for finding in detector.analyze(list(unit.events)) if finding.rule_id in EXTERNALLY_EVALUABLE_RULES
        ]
        truth_key = "botnet_origin" if unit.truth == "botnet-origin" else "normal_origin"
        for finding in findings:
            rule_counts[finding.rule_id][truth_key] += 1
        units.append(
            {
                "host": unit.host,
                "window_start": unit.window_start.isoformat(),
                "truth": unit.truth,
                "event_count": len(unit.events),
                "predicted_review": bool(findings),
                "rule_ids": sorted({finding.rule_id for finding in findings}),
                "finding_ids": [finding.finding_id for finding in findings],
                "evidence_ids": sorted({identifier for finding in findings for identifier in finding.evidence_ids}),
            }
        )
    return units, {rule: dict(counts) for rule, counts in rule_counts.items()}


def tune_development(
    *,
    repository_root: Path,
    selection_path: Path,
    acquisition_path: Path,
    data_directory: Path,
) -> dict[str, Any]:
    selection, acquisition, source, path = _load_source(
        selection_path=selection_path,
        acquisition_path=acquisition_path,
        data_directory=data_directory,
        role="development",
    )
    candidates = _grid_candidates(selection)
    detectors = [BehaviorDetector(thresholds=thresholds) for thresholds in candidates]
    confusion = [Counter() for _ in candidates]
    counters = ParseCounters()
    window_seconds = selection["primary_window_seconds"]
    for unit in iter_labeled_windows(
        path,
        scenario=source["scenario"],
        window_seconds=window_seconds,
        counters=counters,
    ):
        events = list(unit.events)
        positive = unit.truth == "botnet-origin"
        for index, detector in enumerate(detectors):
            predicted = any(finding.rule_id in EXTERNALLY_EVALUABLE_RULES for finding in detector.analyze(events))
            confusion[index][_classification_counter(positive, predicted)] += 1
    candidate_results = []
    for index, (thresholds, counts) in enumerate(zip(candidates, confusion)):
        mapping = asdict(thresholds)
        metrics = binary_metrics(counts["tp"], counts["fp"], counts["fn"], counts["tn"])
        candidate_results.append(
            {
                "candidate_index": index,
                "thresholds": mapping,
                "grid_distance_from_v1_0": _grid_distance(selection, mapping),
                "alerted_units": counts["tp"] + counts["fp"],
                "metrics": metrics,
            }
        )
    selected = max(candidate_results, key=selection_sort_key)
    selected_thresholds = DetectorThresholds(**selected["thresholds"])
    units, rule_counts = _selected_units(
        path,
        scenario=source["scenario"],
        window_seconds=window_seconds,
        thresholds=selected_thresholds,
    )
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_role": "development_only_threshold_selection",
        "selection_record": {"filename": selection_path.name, "sha256": sha256_file(selection_path)},
        "acquisition_record": {"filename": acquisition_path.name, "sha256": sha256_file(acquisition_path)},
        "holdout_accessed": False,
        "source": source | {"local_sha256": sha256_file(path)},
        "window_seconds": window_seconds,
        "selection_rule": selection["threshold_selection"],
        "parse_counts": vars(counters),
        "candidate_results": candidate_results,
        "selected": selected,
        "selected_rule_finding_counts": rule_counts,
        "selected_units": units,
        "scientific_state": _scientific_state(repository_root),
    }


def _development_markdown(result: dict[str, Any]) -> str:
    selected = result["selected"]
    metrics = selected["metrics"]
    return "\n".join(
        [
            "# V1.1 CTU-13 development-only threshold selection",
            "",
            "> The confirmatory holdout was not accessed by this command.",
            "",
            f"Candidates: {len(result['candidate_results'])}",
            f"Selected candidate: {selected['candidate_index']}",
            f"Units: {sum(metrics[key] for key in ('true_positive', 'false_positive', 'false_negative', 'true_negative'))}",
            f"TP/FP/FN/TN: {metrics['true_positive']}/{metrics['false_positive']}/{metrics['false_negative']}/{metrics['true_negative']}",
            f"F1: {metrics['f1']:.3f}",
            f"Specificity: {metrics['specificity']:.3f}",
            f"MCC: {metrics['matthews_correlation_coefficient']:.3f}",
            "",
            "## Selected thresholds",
            "",
            "```json",
            json.dumps(selected["thresholds"], indent=2),
            "```",
            "",
        ]
    )


def run_holdout(
    *,
    repository_root: Path,
    selection_path: Path,
    acquisition_path: Path,
    data_directory: Path,
    development_result_path: Path,
) -> dict[str, Any]:
    development = _read_json(development_result_path)
    if development.get("evidence_role") != "development_only_threshold_selection":
        raise ValueError("Development artifact has the wrong evidence role")
    _verify_scientific_state(repository_root, development["scientific_state"])
    selection, acquisition, source, path = _load_source(
        selection_path=selection_path,
        acquisition_path=acquisition_path,
        data_directory=data_directory,
        role="holdout",
    )
    if sha256_file(selection_path) != development["selection_record"]["sha256"]:
        raise ValueError("Selection record changed after development tuning")
    if sha256_file(acquisition_path) != development["acquisition_record"]["sha256"]:
        raise ValueError("Acquisition record changed after development tuning")
    thresholds = DetectorThresholds(**development["selected"]["thresholds"])
    evaluation = evaluate_binetflow(
        path,
        scenario=source["scenario"],
        family=source["family"],
        role="holdout",
        window_seconds=selection["primary_window_seconds"],
        thresholds=thresholds,
    )
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_role": "single_confirmatory_holdout_run",
        "selection_record": {"filename": selection_path.name, "sha256": sha256_file(selection_path)},
        "acquisition_record": {"filename": acquisition_path.name, "sha256": sha256_file(acquisition_path)},
        "development_result": {
            "filename": development_result_path.name,
            "sha256": sha256_file(development_result_path),
        },
        "selected_candidate_index": development["selected"]["candidate_index"],
        "scientific_state": _scientific_state(repository_root),
        "evaluation": evaluation,
    }


def _holdout_markdown(result: dict[str, Any]) -> str:
    evaluation = result["evaluation"]
    metrics = evaluation["metrics"]
    return "\n".join(
        [
            "# V1.1 CTU-13 single confirmatory holdout result",
            "",
            f"Family: {evaluation['family']}",
            f"Window: {evaluation['window_seconds']} seconds",
            f"Units: {sum(metrics[key] for key in ('true_positive', 'false_positive', 'false_negative', 'true_negative'))}",
            f"TP/FP/FN/TN: {metrics['true_positive']}/{metrics['false_positive']}/{metrics['false_negative']}/{metrics['true_negative']}",
            f"Precision: {metrics['precision']:.3f}",
            f"Recall: {metrics['recall']:.3f}",
            f"F1: {metrics['f1']:.3f}",
            f"Specificity: {metrics['specificity']:.3f}",
            f"MCC: {metrics['matthews_correlation_coefficient']:.3f}",
            "",
            "No automatic action was executed.",
            "",
        ]
    )


def _write_and_preserve(
    result: dict[str, Any],
    markdown: str,
    *,
    output_directory: Path,
    preserve_directory: Path,
    stem: str,
) -> None:
    if preserve_directory.exists() and any(preserve_directory.iterdir()):
        raise ValueError(f"Preservation directory must be absent or empty: {preserve_directory}")
    output_directory.mkdir(parents=True, exist_ok=True)
    json_path = output_directory / f"{stem}.json"
    markdown_path = output_directory / f"{stem}.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    preserve_directory.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for path in (json_path, markdown_path):
        destination = preserve_directory / path.name
        shutil.copyfile(path, destination)
        artifacts.append(
            {"filename": destination.name, "bytes": destination.stat().st_size, "sha256": sha256_file(destination)}
        )
    provenance = {
        "schema_version": "1.0",
        "preserved_at": datetime.now(timezone.utc).isoformat(),
        "evidence_role": result["evidence_role"],
        "artifacts": artifacts,
    }
    (preserve_directory / "provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--selection",
        type=Path,
        default=repository_root / "research" / "v1.1" / "ctu13-confirmatory-selection-2026-08-15-corrected.json",
    )
    common.add_argument(
        "--acquisition",
        type=Path,
        default=repository_root / "research" / "v1.1" / "ctu13-confirmatory-acquisition-2026-08-15.json",
    )
    common.add_argument("--data-dir", type=Path, default=repository_root / "data" / "ctu13-v1.1")
    tune_parser = subparsers.add_parser("tune-development", parents=[common])
    tune_parser.add_argument("--output-dir", type=Path, required=True)
    tune_parser.add_argument("--preserve-dir", type=Path, required=True)
    holdout_parser = subparsers.add_parser("run-holdout", parents=[common])
    holdout_parser.add_argument("--development-result", type=Path, required=True)
    holdout_parser.add_argument("--output-dir", type=Path, required=True)
    holdout_parser.add_argument("--preserve-dir", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "tune-development":
            result = tune_development(
                repository_root=repository_root,
                selection_path=arguments.selection.resolve(),
                acquisition_path=arguments.acquisition.resolve(),
                data_directory=arguments.data_dir.resolve(),
            )
            _write_and_preserve(
                result,
                _development_markdown(result),
                output_directory=arguments.output_dir.resolve(),
                preserve_directory=arguments.preserve_dir.resolve(),
                stem="development-tuning",
            )
        else:
            result = run_holdout(
                repository_root=repository_root,
                selection_path=arguments.selection.resolve(),
                acquisition_path=arguments.acquisition.resolve(),
                data_directory=arguments.data_dir.resolve(),
                development_result_path=arguments.development_result.resolve(),
            )
            _write_and_preserve(
                result,
                _holdout_markdown(result),
                output_directory=arguments.output_dir.resolve(),
                preserve_directory=arguments.preserve_dir.resolve(),
                stem="confirmatory-holdout",
            )
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(f"Evidence role: {result['evidence_role']}")
    print(f"Preserved: {arguments.preserve_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
