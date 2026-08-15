"""Replay transparent response-policy counterfactuals without executing actions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


def _counts_from_units(units: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "positive": 0,
        "negative": 0,
        "positive_alerted": 0,
        "negative_alerted": 0,
        "positive_multi_rule": 0,
        "negative_multi_rule": 0,
    }
    for unit in units:
        positive = unit["truth"] == "botnet-origin"
        alerted = bool(unit["rule_ids"])
        multi_rule = len(set(unit["rule_ids"])) >= 2
        counts["positive" if positive else "negative"] += 1
        if alerted:
            counts["positive_alerted" if positive else "negative_alerted"] += 1
        if multi_rule:
            counts["positive_multi_rule" if positive else "negative_multi_rule"] += 1
    return counts


def _counts_from_combinations(combinations: dict[str, dict[str, int]]) -> dict[str, int]:
    units = []
    for truth, truth_counts in combinations.items():
        for combination, count in truth_counts.items():
            rule_ids = [] if combination == "none" else combination.split("+")
            units.extend({"truth": truth, "rule_ids": rule_ids} for _ in range(count))
    return _counts_from_units(units)


def evaluate_policies(counts: dict[str, int]) -> dict[str, Any]:
    alerts = counts["positive_alerted"] + counts["negative_alerted"]
    multi_actions = counts["positive_multi_rule"] + counts["negative_multi_rule"]
    missed_alerts = counts["positive"] - counts["positive_alerted"]
    missed_multi = counts["positive"] - counts["positive_multi_rule"]
    return {
        "automatic_block_on_alert": {
            "containment_actions": alerts,
            "normal_origin_actions": counts["negative_alerted"],
            "botnet_origin_actions": counts["positive_alerted"],
            "botnet_origin_without_action": missed_alerts,
            "rollback_required": True,
        },
        "automatic_block_after_two_rules": {
            "containment_actions": multi_actions,
            "normal_origin_actions": counts["negative_multi_rule"],
            "botnet_origin_actions": counts["positive_multi_rule"],
            "botnet_origin_without_action": missed_multi,
            "rollback_required": True,
        },
        "analyst_approval": {
            "proposals": alerts,
            "containment_actions": 0,
            "reason": "No analyst decisions are present in the preserved datasets.",
        },
        "evidence_collection_only": {
            "review_targets": alerts,
            "normal_origin_review_targets": counts["negative_alerted"],
            "botnet_origin_review_targets": counts["positive_alerted"],
            "containment_actions": 0,
        },
        "temporary_rate_limiting_after_approval": {
            "proposals": alerts,
            "containment_actions": 0,
            "reason": "Approval and network-impact evidence are absent.",
        },
        "increased_monitoring": {
            "monitoring_targets": alerts,
            "normal_origin_targets": counts["negative_alerted"],
            "botnet_origin_targets": counts["positive_alerted"],
            "containment_actions": 0,
        },
        "isolation_after_independent_confirmation": {
            "proposals": alerts,
            "containment_actions": 0,
            "reason": "No independent confirmation is present in the preserved datasets.",
        },
    }


def run_counterfactuals(repository_root: str | Path, output_directory: str | Path) -> dict[str, Any]:
    root = Path(repository_root)
    retrospective = json.loads(
        (
            root / "research/v1.1/results/ctu13-retrospective-window-analysis-2026-08-15/ctu13-window-analysis.json"
        ).read_text(encoding="utf-8")
    )
    historical = next(
        item for item in retrospective["analyses"] if item["role"] == "holdout" and item["window_seconds"] == 300
    )
    confirmatory = json.loads(
        (root / "research/v1.1/results/ctu13-confirmatory-holdout-2026-08-15/confirmatory-holdout.json").read_text(
            encoding="utf-8"
        )
    )["evaluation"]
    transfer = json.loads(
        (root / "research/v1.1/results/second-dataset-transfer-2026-08-15/second-dataset-transfer.json").read_text(
            encoding="utf-8"
        )
    )
    datasets = {
        "historical-nsis-ay": _counts_from_units(historical["units"]),
        "confirmatory-donbot": _counts_from_units(confirmatory["units"]),
        "synthetic-implementation-transfer": _counts_from_combinations(transfer["rule_combination_counts_by_truth"]),
    }
    result = {
        "schema_version": "1.0",
        "evidence_role": "offline-response-policy-counterfactual",
        "datasets": {
            name: {"unit_counts": counts, "policies": evaluate_policies(counts)} for name, counts in datasets.items()
        },
        "qualitative_cost_order": {
            "highest_direct_disruption": ["automatic_block_on_alert", "automatic_block_after_two_rules"],
            "bounded_but_not_measurable_without_approval": [
                "analyst_approval",
                "temporary_rate_limiting_after_approval",
                "isolation_after_independent_confirmation",
            ],
            "lowest_direct_disruption": ["evidence_collection_only", "increased_monitoring"],
        },
        "automatic_actions_executed": 0,
        "interpretation_boundary": (
            "Dataset labels approximate origin, not business impact. Counts do not estimate firewall efficacy, "
            "analyst accuracy, confirmation quality, or rollback success."
        ),
    }
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    (output / "counterfactual-policies.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output-dir", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        result = run_counterfactuals(arguments.repository_root, arguments.output_dir)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(json.dumps({name: item["unit_counts"] for name, item in result["datasets"].items()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
