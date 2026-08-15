"""Audit the frozen V1.1 conflicting-context supplemental LLM matrix."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ctu13_acquire import sha256_file
from .ollama_advisor import validate_grounded_schema


def _safe_rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def analyze_supplement(
    matrix_summary_path: str | Path,
    results_directory: str | Path,
) -> dict[str, Any]:
    summary_file = Path(matrix_summary_path).resolve()
    root = Path(results_directory).resolve()
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    expected_calls = int(summary["expected_model_calls"])

    attempts: list[dict[str, Any]] = []
    stable_orders: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    stable_priority_vectors: dict[str, list[tuple[tuple[str, str], ...]]] = defaultdict(list)
    for benchmark_file in sorted(root.glob("*/*/run-*/benchmark.json")):
        benchmark = json.loads(benchmark_file.read_text(encoding="utf-8"))
        model = benchmark_file.parents[2].name
        prompt_variant = benchmark_file.parents[1].name
        repetition = benchmark_file.parent.name
        for scenario in benchmark["scenarios"]:
            response = scenario.get("ollama")
            if not response:
                continue
            metadata = response.get("metadata", {})
            audit = response.get("audit", {})
            raw_response = response.get("raw_response", "")
            parsed: Any = None
            json_valid = False
            schema_valid = False
            if isinstance(raw_response, str) and raw_response:
                try:
                    parsed = json.loads(raw_response)
                    json_valid = True
                except json.JSONDecodeError:
                    parsed = None
            if json_valid:
                try:
                    validate_grounded_schema(parsed)
                    schema_valid = True
                except ValueError:
                    pass

            supplied = {item["finding_id"] for item in scenario["findings"]}
            order: tuple[str, ...] | None = None
            priority_vector: tuple[tuple[str, str], ...] | None = None
            if schema_valid:
                priorities = parsed["priorities"]
                candidate_order = tuple(item["finding_id"] for item in priorities)
                if len(candidate_order) == len(set(candidate_order)) and set(candidate_order) == supplied:
                    order = candidate_order
                    priority_vector = tuple((item["finding_id"], item["priority"]) for item in priorities)
                    stable_orders[model].append(order)
                    stable_priority_vectors[model].append(priority_vector)

            prompt_tokens = metadata.get("prompt_eval_count")
            output_tokens = metadata.get("eval_count")
            maximum_output_tokens = metadata.get("max_output_tokens")
            context_length = metadata.get("context_length")
            attempts.append(
                {
                    "model": model,
                    "prompt_variant": prompt_variant,
                    "repetition": repetition,
                    "scenario_id": scenario["id"],
                    "status": response.get("status"),
                    "api_response_received": response.get("status") != "api-failure",
                    "json_parse_valid": json_valid,
                    "schema_valid": schema_valid,
                    "grounding_accepted": response.get("status") == "accepted",
                    "prompt_eval_count": prompt_tokens,
                    "eval_count": output_tokens,
                    "maximum_output_tokens": maximum_output_tokens,
                    "context_length": context_length,
                    "input_and_reserved_output_fit_context": bool(
                        isinstance(prompt_tokens, int)
                        and isinstance(maximum_output_tokens, int)
                        and isinstance(context_length, int)
                        and prompt_tokens + maximum_output_tokens <= context_length
                    ),
                    "reached_output_limit": bool(
                        isinstance(output_tokens, int)
                        and isinstance(maximum_output_tokens, int)
                        and output_tokens >= maximum_output_tokens
                    ),
                    "finding_coverage_lexical_or_structured": audit.get("finding_coverage"),
                    "evidence_coverage_lexical_or_structured": audit.get("evidence_coverage"),
                    "unsupported_claim_categories_lexical": audit.get("unsupported_claim_categories", []),
                    "unauthorized_control_mentions": len(audit.get("unauthorized_controls", [])),
                    "complete_known_finding_order": list(order) if order else None,
                    "complete_priority_vector": [list(item) for item in priority_vector] if priority_vector else None,
                    "validation_error": response.get("error"),
                }
            )

    if len(attempts) != expected_calls:
        raise ValueError(f"Expected {expected_calls} supplemental attempts, found {len(attempts)}")

    per_model = []
    for model in sorted({item["model"] for item in attempts}):
        rows = [item for item in attempts if item["model"] == model]
        orders = stable_orders[model]
        priority_vectors = stable_priority_vectors[model]
        order_mode = Counter(orders).most_common(1)[0] if orders else None
        priority_mode = Counter(priority_vectors).most_common(1)[0] if priority_vectors else None
        per_model.append(
            {
                "model": model,
                "attempts": len(rows),
                "api_responses": sum(item["api_response_received"] for item in rows),
                "json_parse_valid": sum(item["json_parse_valid"] for item in rows),
                "schema_valid": sum(item["schema_valid"] for item in rows),
                "grounding_accepted": sum(item["grounding_accepted"] for item in rows),
                "output_limit_reached": sum(item["reached_output_limit"] for item in rows),
                "complete_known_finding_rankings": len(orders),
                "distinct_complete_rankings": len(set(orders)),
                "ranking_exact_agreement_with_mode": (_safe_rate(order_mode[1], len(orders)) if order_mode else None),
                "distinct_complete_priority_vectors": len(set(priority_vectors)),
                "priority_exact_agreement_with_mode": (
                    _safe_rate(priority_mode[1], len(priority_vectors)) if priority_mode else None
                ),
            }
        )

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_role": "posthoc-supplemental-ranking-and-denominator-audit",
        "source_matrix_summary": summary_file.name,
        "source_matrix_summary_sha256": sha256_file(summary_file),
        "attempts": len(attempts),
        "api_responses": sum(item["api_response_received"] for item in attempts),
        "json_parse_valid": sum(item["json_parse_valid"] for item in attempts),
        "schema_valid": sum(item["schema_valid"] for item in attempts),
        "grounding_accepted": sum(item["grounding_accepted"] for item in attempts),
        "input_and_reserved_output_fit_context": sum(
            item["input_and_reserved_output_fit_context"] for item in attempts
        ),
        "output_limit_reached": sum(item["reached_output_limit"] for item in attempts),
        "automatic_actions_executed": 0,
        "per_model": per_model,
        "attempt_records": attempts,
        "interpretation": {
            "ranking": "Stability is estimable only from schema-valid outputs containing every exact supplied finding ID once; it is not semantic correctness.",
            "lexical_flags": "Unsupported-claim categories are conservative lexical safety flags and may include negated or uncertainty-preserving language; they are not human-confirmed errors.",
            "complexity": "Failure under the 31-event stress case is retained as a result and does not replace primary-matrix estimates.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix-summary", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        result = analyze_supplement(arguments.matrix_summary, arguments.results_dir)
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(
        f"Supplement audit: attempts={result['attempts']} api={result['api_responses']} "
        f"schema={result['schema_valid']} accepted={result['grounding_accepted']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
