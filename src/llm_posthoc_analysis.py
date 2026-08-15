"""Analyze preserved primary LLM outputs without rerunning inference."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ctu13_acquire import sha256_file
from .ollama_advisor import validate_grounded_schema


def analyze_primary_directory(primary_directory: str | Path, output_path: str | Path) -> dict[str, Any]:
    root = Path(primary_directory).resolve()
    run_files = sorted(root.glob("*/*/run-*/benchmark.json"))
    if len(run_files) != 45:
        raise ValueError(f"Expected 45 primary repetition files, found {len(run_files)}")
    rankings: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    availability: Counter[str] = Counter()
    for run_file in run_files:
        cell = f"{run_file.parents[2].name}/{run_file.parents[1].name}"
        result = json.loads(run_file.read_text(encoding="utf-8"))
        scenario = next(item for item in result["scenarios"] if item["id"] == "multi-finding-mixed-rules")
        response = scenario["ollama"]
        availability[f"{cell}|attempts"] += 1
        if response.get("status") == "api-failure":
            availability[f"{cell}|api_failures"] += 1
            continue
        availability[f"{cell}|api_responses"] += 1
        raw = response.get("raw_response")
        if not isinstance(raw, str):
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        availability[f"{cell}|json_parse_valid"] += 1
        try:
            validate_grounded_schema(parsed)
        except ValueError:
            continue
        availability[f"{cell}|schema_valid"] += 1
        ranking = tuple(item["finding_id"] for item in parsed["priorities"])
        rankings[cell].append(ranking)

    cells = []
    for cell in sorted({key.rsplit("|", 1)[0] for key in availability}):
        observed = rankings[cell]
        if observed:
            modal, count = Counter(observed).most_common(1)[0]
            ranking_summary: dict[str, Any] | None = {
                "observations": len(observed),
                "distinct_rankings": len(set(observed)),
                "modal_ranking": list(modal),
                "exact_agreement_with_mode": round(count / len(observed), 6),
            }
        else:
            ranking_summary = None
        cells.append(
            {
                "cell": cell,
                "attempts": availability[f"{cell}|attempts"],
                "api_responses": availability[f"{cell}|api_responses"],
                "api_failures": availability[f"{cell}|api_failures"],
                "json_parse_valid": availability[f"{cell}|json_parse_valid"],
                "schema_valid": availability[f"{cell}|schema_valid"],
                "schema_valid_ranking_stability": ranking_summary,
            }
        )
    summary_file = root / "matrix-summary.json"
    result = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_role": "posthoc-schema-valid-multi-finding-ranking-audit",
        "source_summary_sha256": sha256_file(summary_file),
        "cells": cells,
        "interpretation_boundary": (
            "Ranking is measured for schema-valid multi-finding responses even when the semantic-policy validator "
            "rejected them. It describes repeatability of ordering, not correctness or usefulness. Cells without "
            "schema-valid responses have no estimable ranking stability."
        ),
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        result = analyze_primary_directory(arguments.primary_dir, arguments.output)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
    estimable = sum(item["schema_valid_ranking_stability"] is not None for item in result["cells"])
    print(f"Primary ranking audit: cells={len(result['cells'])} estimable={estimable}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
