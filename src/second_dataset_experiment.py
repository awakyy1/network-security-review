"""Replay frozen behavior rules on the selected Botnet Group Activity flow file."""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter, defaultdict
from datetime import timezone
from pathlib import Path
from typing import Any

from .behavior_detector import BehaviorDetector, DetectorThresholds
from .ctu13_acquire import sha256_file
from .ctu13_experiment import EXTERNALLY_EVALUABLE_RULES, ParseCounters, binary_metrics, iter_labeled_windows


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read second-dataset manifest: {error}") from error
    if not isinstance(value, dict):
        raise ValueError("Second-dataset manifest must contain one JSON object")
    return value


def run_second_dataset(manifest_path: str | Path, output_directory: str | Path) -> dict[str, Any]:
    manifest_file = Path(manifest_path).resolve()
    manifest = _load_json(manifest_file)
    if manifest.get("status") != "frozen-before-detector-run":
        raise ValueError("Second-dataset manifest must be frozen before execution")

    selection = manifest["selection_record"]
    selection_file = manifest_file.parent / selection["filename"]
    if sha256_file(selection_file).lower() != selection["sha256"].lower():
        raise ValueError("Second-dataset selection-record SHA-256 mismatch")

    source_spec = manifest["source"]
    source = Path(source_spec["path"])
    if source.stat().st_size != source_spec["bytes"]:
        raise ValueError("Second-dataset byte count mismatch")
    if sha256_file(source).lower() != source_spec["sha256"].lower():
        raise ValueError("Second-dataset SHA-256 mismatch")

    profile = manifest["parser_profile"]
    thresholds = DetectorThresholds(**manifest["detector_thresholds"])
    detector = BehaviorDetector(thresholds=thresholds)
    counters = ParseCounters()
    confusion = Counter()
    combinations: dict[str, Counter[str]] = defaultdict(Counter)
    examples: dict[str, dict[str, Any]] = {}
    rule_findings = {rule: Counter() for rule in sorted(EXTERNALLY_EVALUABLE_RULES)}

    started = time.perf_counter()
    for unit in iter_labeled_windows(
        source,
        scenario=source_spec["scenario"],
        window_seconds=manifest["window_seconds"],
        counters=counters,
        maximum_file_bytes=profile["maximum_file_bytes"],
        maximum_rows=profile["maximum_rows"],
        timestamp_patterns=tuple(profile["timestamp_patterns"]),
        capture_timezone=timezone.utc,
        address_namespace=profile["address_namespace"],
        event_prefix=profile["event_prefix"],
        telemetry_source=profile["telemetry_source"],
    ):
        findings = [item for item in detector.analyze(list(unit.events)) if item.rule_id in EXTERNALLY_EVALUABLE_RULES]
        rule_ids = tuple(sorted({item.rule_id for item in findings}))
        combination = "+".join(rule_ids) if rule_ids else "none"
        positive = unit.truth == "botnet-origin"
        predicted = bool(findings)
        outcome = "tp" if positive and predicted else "fn" if positive else "fp" if predicted else "tn"
        confusion[outcome] += 1
        combinations[unit.truth][combination] += 1
        for finding in findings:
            rule_findings[finding.rule_id][unit.truth] += 1

        example_key = f"{unit.truth}|{combination}"
        if example_key not in examples:
            examples[example_key] = {
                "truth": unit.truth,
                "rule_combination": list(rule_ids),
                "host": unit.host,
                "window_start": unit.window_start.isoformat(),
                "event_count": len(unit.events),
                "finding_ids": [item.finding_id for item in findings],
                "evidence_ids": sorted({event_id for item in findings for event_id in item.evidence_ids}),
            }

    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    metrics = binary_metrics(confusion["tp"], confusion["fp"], confusion["fn"], confusion["tn"])
    result = {
        "schema_version": "1.0",
        "evidence_role": "implementation-transfer-not-independent-validation",
        "manifest": manifest_file.name,
        "manifest_sha256": sha256_file(manifest_file),
        "selection_record": selection,
        "source": source_spec,
        "window_seconds": manifest["window_seconds"],
        "detector_thresholds": manifest["detector_thresholds"],
        "metrics": metrics,
        "parse_counts": vars(counters),
        "rule_finding_counts": {rule: dict(counts) for rule, counts in rule_findings.items()},
        "rule_combination_counts_by_truth": {
            truth: dict(sorted(counts.items())) for truth, counts in sorted(combinations.items())
        },
        "deterministic_examples": [examples[key] for key in sorted(examples)],
        "runtime": {"elapsed_ms": elapsed_ms},
        "interpretation_boundary": (
            "The synthetic source derives bot-group behavior from CTU-13 patterns. These results test parser and "
            "detector transfer only and must not be pooled with CTU-13 or described as independent generalization."
        ),
        "automatic_actions_executed": 0,
    }
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    (output / "second-dataset-transfer.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output / "second-dataset-transfer.md").write_text(_markdown(result), encoding="utf-8")
    return result


def _markdown(result: dict[str, Any]) -> str:
    metrics = result["metrics"]
    units = sum(metrics[key] for key in ("true_positive", "false_positive", "false_negative", "true_negative"))
    return "\n".join(
        [
            "# Second-dataset implementation-transfer replay",
            "",
            "> Synthetic CTU-13-derived group activity; not independent external validation.",
            "",
            "| Units | TP | FP | FN | TN | Precision | Recall | F1 | Specificity | MCC |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            (
                f"| {units} | {metrics['true_positive']} | {metrics['false_positive']} | "
                f"{metrics['false_negative']} | {metrics['true_negative']} | {metrics['precision']:.3f} | "
                f"{metrics['recall']:.3f} | {metrics['f1']:.3f} | {metrics['specificity']:.3f} | "
                f"{metrics['matthews_correlation_coefficient']:.3f} |"
            ),
            "",
            result["interpretation_boundary"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        result = run_second_dataset(arguments.manifest, arguments.output_dir)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result["metrics"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
