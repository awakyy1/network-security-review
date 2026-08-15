"""Evaluate frozen behavior rules on labeled CTU-13 bidirectional text flows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
import tracemalloc
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from .behavior_detector import BehaviorDetector, DetectorThresholds
from .ctu13_acquire import load_manifest, sha256_file
from .telemetry import TelemetryEvent

EXPECTED_COLUMNS = [
    "StartTime",
    "Dur",
    "Proto",
    "SrcAddr",
    "Sport",
    "Dir",
    "DstAddr",
    "Dport",
    "State",
    "sTos",
    "dTos",
    "TotPkts",
    "TotBytes",
    "SrcBytes",
    "Label",
]
CAPTURE_TIMEZONE = timezone(timedelta(hours=2), name="CEST")
MAX_FLOW_FILE_BYTES = 100 * 1024 * 1024
MAX_FLOW_ROWS = 2_000_000
EXTERNALLY_EVALUABLE_RULES = {"BEH-001", "BEH-002", "BEH-003"}


@dataclass
class ParseCounters:
    total_rows: int = 0
    scored_rows: int = 0
    positive_rows: int = 0
    negative_rows: int = 0
    excluded_background_or_to: int = 0
    excluded_unsupported_protocol: int = 0
    excluded_missing_destination_port: int = 0
    excluded_mixed_truth_windows: int = 0


@dataclass
class UnitBuilder:
    truth_values: set[str] = field(default_factory=set)
    events: list[TelemetryEvent] = field(default_factory=list)


@dataclass(frozen=True)
class LabeledWindow:
    host: str
    window_start: datetime
    truth: str
    events: tuple[TelemetryEvent, ...]


def _parse_timestamp(
    value: str,
    row_number: int,
    *,
    capture_timezone: timezone = CAPTURE_TIMEZONE,
    patterns: tuple[str, ...] = ("%Y/%m/%d %H:%M:%S.%f", "%Y/%m/%d %H:%M:%S"),
) -> datetime:
    for pattern in patterns:
        try:
            return datetime.strptime(value.strip(), pattern).replace(tzinfo=capture_timezone)
        except ValueError:
            pass
    raise ValueError(f"Invalid CTU-13 StartTime on row {row_number}: {value!r}")


def _non_negative_integer(value: str, field_name: str, row_number: int) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise ValueError(f"Invalid CTU-13 {field_name} on row {row_number}: {value!r}") from error
    if parsed < 0:
        raise ValueError(f"Negative CTU-13 {field_name} on row {row_number}")
    return parsed


def _decimal_port(value: str) -> int | None:
    value = value.strip()
    if not value.isdecimal():
        return None
    port = int(value)
    return port if 1 <= port <= 65_535 else None


def _truth(label: str) -> str | None:
    normalized = label.strip()
    if normalized.startswith("flow="):
        normalized = normalized[5:]
    if normalized.startswith("From-Botnet"):
        return "botnet-origin"
    if normalized.startswith("From-Normal"):
        return "normal-origin"
    return None


def _anonymous_address(namespace: str, scenario: int, role: str, address: str) -> str:
    digest = hashlib.sha256(f"{namespace}:{scenario}:{role}:{address}".encode()).hexdigest()[:16]
    return f"{namespace}-s{scenario:02d}-{role}-{digest}"


def _window_start(timestamp: datetime, window_seconds: int) -> datetime:
    epoch = int(timestamp.timestamp())
    return datetime.fromtimestamp(epoch - (epoch % window_seconds), tz=timestamp.tzinfo)


def _emit_units(
    builders: dict[str, UnitBuilder],
    window_start: datetime,
    counters: ParseCounters,
) -> Iterator[LabeledWindow]:
    for host in sorted(builders):
        builder = builders[host]
        if len(builder.truth_values) > 1:
            counters.excluded_mixed_truth_windows += 1
            continue
        if not builder.truth_values or not builder.events:
            continue
        yield LabeledWindow(
            host=host,
            window_start=window_start,
            truth=next(iter(builder.truth_values)),
            events=tuple(builder.events),
        )


def iter_labeled_windows(
    path: str | Path,
    *,
    scenario: int,
    window_seconds: int,
    counters: ParseCounters,
    maximum_file_bytes: int = MAX_FLOW_FILE_BYTES,
    maximum_rows: int = MAX_FLOW_ROWS,
    timestamp_patterns: tuple[str, ...] = ("%Y/%m/%d %H:%M:%S.%f", "%Y/%m/%d %H:%M:%S"),
    capture_timezone: timezone = CAPTURE_TIMEZONE,
    address_namespace: str = "ctu13",
    event_prefix: str = "CTU",
    telemetry_source: str = "ctu13-binetflow",
) -> Iterator[LabeledWindow]:
    """Stream clean From-Botnet/From-Normal source-host windows without exposing labels to the detector."""
    source = Path(path)
    size = source.stat().st_size
    if not 1 <= size <= maximum_file_bytes:
        raise ValueError(f"Flow file is empty or exceeds the {maximum_file_bytes}-byte research bound")
    if not 60 <= window_seconds <= 3600:
        raise ValueError("CTU-13 window must be between 60 and 3600 seconds")

    current_window: datetime | None = None
    builders: dict[str, UnitBuilder] = defaultdict(UnitBuilder)
    previous_timestamp: datetime | None = None
    with source.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError("CTU-13 binetflow header does not match the frozen 15-column schema")
        for row_number, row in enumerate(reader, start=2):
            counters.total_rows += 1
            if counters.total_rows > maximum_rows:
                raise ValueError(f"Flow input exceeds {maximum_rows} rows")
            timestamp = _parse_timestamp(
                row["StartTime"],
                row_number,
                capture_timezone=capture_timezone,
                patterns=timestamp_patterns,
            )
            if previous_timestamp is not None and timestamp < previous_timestamp:
                raise ValueError(f"CTU-13 rows are not time-ordered at row {row_number}")
            previous_timestamp = timestamp
            bucket = _window_start(timestamp, window_seconds)
            if current_window is None:
                current_window = bucket
            elif bucket > current_window:
                yield from _emit_units(builders, current_window, counters)
                builders = defaultdict(UnitBuilder)
                current_window = bucket

            truth = _truth(row["Label"])
            if truth is None:
                counters.excluded_background_or_to += 1
                continue
            protocol = row["Proto"].strip().lower()
            if protocol not in {"tcp", "udp"}:
                counters.excluded_unsupported_protocol += 1
                continue
            destination_port = _decimal_port(row["Dport"])
            if destination_port is None:
                counters.excluded_missing_destination_port += 1
                continue
            total_bytes = _non_negative_integer(row["TotBytes"], "TotBytes", row_number)
            source_bytes = _non_negative_integer(row["SrcBytes"], "SrcBytes", row_number)
            if source_bytes > total_bytes:
                raise ValueError(f"CTU-13 SrcBytes exceeds TotBytes on row {row_number}")

            host = _anonymous_address(address_namespace, scenario, "src", row["SrcAddr"].strip())
            event = TelemetryEvent.from_mapping(
                {
                    "event_id": f"{event_prefix}{scenario:02d}-{row_number:08d}",
                    "timestamp": timestamp.isoformat(),
                    "host": host,
                    "event_type": "network_connection",
                    "source": telemetry_source,
                    "process": "network-flow-no-process-context",
                    "destination_ip": _anonymous_address(address_namespace, scenario, "dst", row["DstAddr"].strip()),
                    "destination_port": destination_port,
                    "protocol": protocol,
                    "bytes_sent": source_bytes,
                    "bytes_received": total_bytes - source_bytes,
                }
            )
            builder = builders[host]
            builder.truth_values.add(truth)
            builder.events.append(event)
            counters.scored_rows += 1
            if truth == "botnet-origin":
                counters.positive_rows += 1
            else:
                counters.negative_rows += 1

    if current_window is not None:
        yield from _emit_units(builders, current_window, counters)


def _safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _wilson(successes: int, total: int, z: float = 1.959963984540054) -> list[float] | None:
    if total == 0:
        return None
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return [round(max(0.0, center - margin), 6), round(min(1.0, center + margin), 6)]


def binary_metrics(tp: int, fp: int, fn: int, tn: int) -> dict[str, Any]:
    precision = _safe_divide(tp, tp + fp)
    recall = _safe_divide(tp, tp + fn)
    specificity = _safe_divide(tn, tn + fp)
    mcc_denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": round(precision, 6),
        "precision_wilson_95": _wilson(tp, tp + fp),
        "recall": round(recall, 6),
        "recall_wilson_95": _wilson(tp, tp + fn),
        "specificity": round(specificity, 6),
        "specificity_wilson_95": _wilson(tn, tn + fp),
        "f1": round(_safe_divide(2 * precision * recall, precision + recall), 6),
        "balanced_accuracy": round((recall + specificity) / 2, 6),
        "matthews_correlation_coefficient": round((tp * tn - fp * fn) / mcc_denominator, 6) if mcc_denominator else 0.0,
    }


def evaluate_binetflow(
    path: str | Path,
    *,
    scenario: int,
    family: str,
    role: str,
    window_seconds: int,
    thresholds: DetectorThresholds | None = None,
) -> dict[str, Any]:
    counters = ParseCounters()
    detector = BehaviorDetector(thresholds=thresholds)
    confusion = Counter()
    rule_findings = {rule: Counter() for rule in sorted(EXTERNALLY_EVALUABLE_RULES)}
    units = []

    tracemalloc.start()
    started = time.perf_counter()
    try:
        for unit in iter_labeled_windows(
            path,
            scenario=scenario,
            window_seconds=window_seconds,
            counters=counters,
        ):
            findings = [
                item for item in detector.analyze(list(unit.events)) if item.rule_id in EXTERNALLY_EVALUABLE_RULES
            ]
            predicted = bool(findings)
            positive = unit.truth == "botnet-origin"
            if positive and predicted:
                confusion["tp"] += 1
            elif positive:
                confusion["fn"] += 1
            elif predicted:
                confusion["fp"] += 1
            else:
                confusion["tn"] += 1
            truth_key = "botnet_origin" if positive else "normal_origin"
            for finding in findings:
                rule_findings[finding.rule_id][truth_key] += 1
            units.append(
                {
                    "host": unit.host,
                    "window_start": unit.window_start.isoformat(),
                    "truth": unit.truth,
                    "event_count": len(unit.events),
                    "predicted_review": predicted,
                    "rule_ids": sorted({item.rule_id for item in findings}),
                    "finding_ids": [item.finding_id for item in findings],
                }
            )
    finally:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    source = Path(path)
    metrics = binary_metrics(confusion["tp"], confusion["fp"], confusion["fn"], confusion["tn"])
    return {
        "scenario": scenario,
        "family": family,
        "role": role,
        "source": {
            "filename": source.name,
            "bytes": source.stat().st_size,
            "sha256": sha256_file(source),
        },
        "window_seconds": window_seconds,
        "detector_thresholds": asdict(detector.thresholds),
        "unit": "anonymized source host by non-overlapping start-time window",
        "metrics": metrics,
        "response_simulation": {
            "automatic_actions_executed": 0,
            "review_candidates": confusion["tp"] + confusion["fp"],
            "review_candidates_on_botnet_origin": confusion["tp"],
            "review_candidates_on_normal_origin": confusion["fp"],
            "missed_botnet_origin_windows": confusion["fn"],
            "counterfactual_unnecessary_action_rate_if_every_alert_were_blocked": round(
                _safe_divide(confusion["fp"], confusion["tp"] + confusion["fp"]), 6
            ),
            "interpretation": (
                "The observed false-positive share makes automatic blocking unsafe; the implemented system "
                "produces review candidates only and requires independent confirmation before containment."
            ),
        },
        "rule_finding_counts": {rule: dict(counts) for rule, counts in rule_findings.items()},
        "parse_counts": vars(counters),
        "runtime": {"elapsed_ms": elapsed_ms, "peak_traced_memory_bytes": peak_bytes},
        "units": units,
    }


def run_external_validation(
    manifest_path: str | Path,
    data_directory: str | Path,
    output_directory: str | Path,
) -> dict[str, Any]:
    manifest_file = Path(manifest_path).resolve()
    manifest = load_manifest(manifest_file)
    data_root = Path(data_directory).resolve()
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    threshold_mapping = manifest.get("detector_thresholds")
    thresholds = DetectorThresholds(**threshold_mapping) if threshold_mapping is not None else DetectorThresholds()
    sources = []
    for source in manifest["sources"]:
        path = data_root / source["filename"]
        if not path.is_file():
            raise ValueError(f"Missing frozen CTU-13 file: {path}")
        if source["sha256"] is None:
            raise ValueError("Freeze downloaded CTU-13 SHA-256 values in the manifest before evaluation")
        if sha256_file(path).lower() != source["sha256"].lower():
            raise ValueError(f"CTU-13 SHA-256 mismatch for {source['filename']}")
        sources.append(
            evaluate_binetflow(
                path,
                scenario=source["scenario"],
                family=source["family"],
                role=source["role"],
                window_seconds=manifest["window_seconds"],
                thresholds=thresholds,
            )
        )
    result = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": manifest_file.name,
        "manifest_sha256": sha256_file(manifest_file),
        "scope": {
            "claim": "binary review-trigger performance on clean CTU-13 From-Botnet/From-Normal source windows",
            "not_claimed": [
                "malware-family classification",
                "real-time prevention effectiveness",
                "per-technique ground-truth accuracy",
                "BEH-004 validation",
            ],
            "excluded_labels": manifest["label_policy"]["excluded_prefixes"],
        },
        "sources": sources,
    }
    (output / "ctu13-validation.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "ctu13-validation.md").write_text(_markdown_report(result), encoding="utf-8")
    return result


def _markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# CTU-13 external flow validation",
        "",
        "> Only labeled bidirectional text flows are processed. No malware, executable or packet capture is acquired.",
        "",
        "| Role | Scenario | Family | Units | TP | FP | FN | TN | Precision | Recall | F1 | Specificity | MCC |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for source in result["sources"]:
        metrics = source["metrics"]
        unit_count = sum(metrics[key] for key in ("true_positive", "false_positive", "false_negative", "true_negative"))
        lines.append(
            f"| {source['role']} | {source['scenario']} | {source['family']} | {unit_count} | "
            f"{metrics['true_positive']} | {metrics['false_positive']} | {metrics['false_negative']} | "
            f"{metrics['true_negative']} | {metrics['precision']:.3f} | {metrics['recall']:.3f} | "
            f"{metrics['f1']:.3f} | {metrics['specificity']:.3f} | "
            f"{metrics['matthews_correlation_coefficient']:.3f} |"
        )
    lines.extend(
        [
            "",
            "`Background` and `To-*` flows are excluded from binary scoring. A positive unit contains only",
            "traffic labeled `From-Botnet`; a negative unit contains only traffic labeled `From-Normal`.",
            "The labels are never supplied to the detector. BEH-004 is not evaluated because NetFlow lacks",
            "endpoint file-creation evidence. Development and holdout metrics must remain separate.",
            "",
            "No automatic action is executed. If every alert had instead caused a block, the observed false",
            "positive share would also be the unnecessary-action rate; this counterfactual is reported in JSON",
            "to show why human confirmation and endpoint context are required.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=repository_root / "research" / "v2" / "ctu13_manifest.json")
    parser.add_argument("--data-dir", type=Path, default=repository_root / "data" / "ctu13")
    parser.add_argument("--output-dir", type=Path, default=repository_root / "output" / "ctu13")
    arguments = parser.parse_args(argv)
    try:
        result = run_external_validation(arguments.manifest, arguments.data_dir, arguments.output_dir)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for source in result["sources"]:
        metrics = source["metrics"]
        print(
            f"CTU-13 {source['role']} scenario {source['scenario']}: "
            f"TP={metrics['true_positive']} FP={metrics['false_positive']} "
            f"FN={metrics['false_negative']} TN={metrics['true_negative']} F1={metrics['f1']:.3f}"
        )
    print(f"Reports: {arguments.output_dir / 'ctu13-validation.md'}, {arguments.output_dir / 'ctu13-validation.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
