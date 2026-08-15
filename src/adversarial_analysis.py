"""Reaggregate preserved adversarial outputs with explicit eligible denominators."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ctu13_acquire import sha256_file

STRUCTURAL_FIELDS = (
    "priority_label_changed",
    "control_set_changed",
    "finding_order_changed",
    "cited_evidence_set_changed",
)


def reaggregate_adversarial(result: dict[str, Any]) -> dict[str, Any]:
    pairs = [item for item in result["records"] if "influence" in item]
    controls = [item for item in result["records"] if "control" in item]
    received_pairs = [
        item
        for item in pairs
        if item["attack"].get("status") != "api-failure" and item["sanitized"].get("status") != "api-failure"
    ]
    parseable_pairs = [item for item in received_pairs if item["influence"].get("both_parseable")]
    audited_pairs = [
        item
        for item in received_pairs
        if isinstance(item["attack"].get("audit"), dict) and isinstance(item["sanitized"].get("audit"), dict)
    ]

    all_calls = [
        response
        for item in result["records"]
        for response in ([item["attack"], item["sanitized"]] if "influence" in item else [item["control"]])
    ]
    models: dict[str, dict[str, int]] = {}
    for model in sorted({item["model"] for item in result["records"]}):
        model_records = [item for item in result["records"] if item["model"] == model]
        model_calls = [
            response
            for item in model_records
            for response in ([item["attack"], item["sanitized"]] if "influence" in item else [item["control"]])
        ]
        model_pairs = [item for item in model_records if "influence" in item]
        models[model] = {
            "attempted_calls": len(model_calls),
            "api_responses": sum(item.get("status") != "api-failure" for item in model_calls),
            "api_failures": sum(item.get("status") == "api-failure" for item in model_calls),
            "paired_comparisons": len(model_pairs),
            "pairs_with_both_api_responses": sum(
                item["attack"].get("status") != "api-failure" and item["sanitized"].get("status") != "api-failure"
                for item in model_pairs
            ),
            "pairs_with_both_parseable": sum(item["influence"].get("both_parseable", False) for item in model_pairs),
        }

    metrics = {
        "accepted_status_changed": {
            "changed": sum(item["influence"]["accepted_status_changed"] for item in received_pairs),
            "eligible_pairs": len(received_pairs),
        },
        **{
            field: {
                "changed": sum(item["influence"][field] for item in parseable_pairs),
                "eligible_pairs": len(parseable_pairs),
            }
            for field in STRUCTURAL_FIELDS
        },
        "unsupported_claim_flag_changed": {
            "changed": sum(item["influence"]["unsupported_claim_flag_changed"] for item in audited_pairs),
            "eligible_pairs": len(audited_pairs),
        },
    }
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_role": "posthoc-denominator-correction",
        "attempted_calls": len(all_calls),
        "api_responses": sum(item.get("status") != "api-failure" for item in all_calls),
        "api_failures": sum(item.get("status") == "api-failure" for item in all_calls),
        "paired_comparisons_planned": len(pairs),
        "pairs_with_both_api_responses": len(received_pairs),
        "pairs_with_both_parseable_responses": len(parseable_pairs),
        "pairs_with_both_audits": len(audited_pairs),
        "hard_negative_controls": len(controls),
        "metrics": metrics,
        "models": models,
        "interpretation_boundary": (
            "Pairs with two API failures are availability failures, not evidence of unchanged model decisions. "
            "Each comparison has one observation, so rates are descriptive and do not estimate attack success probability."
        ),
    }


def analyze_file(input_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    source = Path(input_path).resolve()
    result = json.loads(source.read_text(encoding="utf-8"))
    analysis = reaggregate_adversarial(result)
    analysis["source_file"] = source.name
    analysis["source_sha256"] = sha256_file(source)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    return analysis


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        result = analyze_file(arguments.input, arguments.output)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(
        f"Adversarial denominator audit: calls={result['attempted_calls']} "
        f"responses={result['api_responses']} eligible_pairs={result['pairs_with_both_api_responses']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
