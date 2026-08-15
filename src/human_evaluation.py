"""Create a blinded, randomized rating package from preserved V1.1 LLM outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any


def prepare_blinded_package(
    matrix_results: str | Path,
    reviewer_output: str | Path,
    mapping_output: str | Path,
    *,
    seed: int = 20260815,
    recovery_map: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(matrix_results)
    summaries = sorted(root.glob("*/*/summary.json"))
    if len(summaries) != 9:
        raise ValueError("Human package requires all nine completed model/prompt cells")
    recovery_by_key: dict[tuple[str, str, str], tuple[dict[str, Any], str]] = {}
    recovery_map_sha256 = None
    expected_recovery_substitutions = 0
    if recovery_map is not None:
        recovery_map_file = Path(recovery_map).resolve()
        recovery_definition = json.loads(recovery_map_file.read_text(encoding="utf-8"))
        recovery_map_sha256 = hashlib.sha256(recovery_map_file.read_bytes()).hexdigest()
        expected_recovery_substitutions = int(recovery_definition["expected_substitutions"])
        for entry in recovery_definition["entries"]:
            benchmark_file = recovery_map_file.parent / entry["benchmark"]
            observed_hash = hashlib.sha256(benchmark_file.read_bytes()).hexdigest()
            if observed_hash.lower() != entry["benchmark_sha256"].lower():
                raise ValueError(f"Recovery benchmark SHA-256 mismatch: {entry['benchmark']}")
            benchmark = json.loads(benchmark_file.read_text(encoding="utf-8"))
            scenarios = {item["id"]: item for item in benchmark["scenarios"]}
            for scenario_id in entry["scenario_ids"]:
                scenario = scenarios.get(scenario_id)
                if not scenario or not scenario.get("ollama"):
                    raise ValueError(f"Recovery benchmark lacks scenario output: {scenario_id}")
                key = (entry["model"], entry["prompt_variant"], scenario_id)
                if key in recovery_by_key:
                    raise ValueError(f"Duplicate recovery mapping: {'|'.join(key)}")
                recovery_by_key[key] = (
                    scenario["ollama"],
                    f"availability-recovery:{entry['benchmark']}",
                )

    records = []
    recovery_substitutions = 0
    mapping = []
    for summary_file in summaries:
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        run_file = summary_file.parent / "run-001" / "benchmark.json"
        run = json.loads(run_file.read_text(encoding="utf-8"))
        for scenario in run["scenarios"]:
            if not scenario.get("ollama"):
                continue
            primary_response = scenario["ollama"]
            selected_response = primary_response
            response_source = f"primary:{run_file.relative_to(root).as_posix()}"
            recovery_key = (summary["model"], summary["prompt_variant"], scenario["id"])
            primary_raw = primary_response.get("raw_response", "")
            primary_raw_missing = not isinstance(primary_raw, str) or not primary_raw.strip()
            if primary_raw_missing and recovery_key in recovery_by_key:
                selected_response, response_source = recovery_by_key[recovery_key]
                recovery_substitutions += 1
            raw_response = selected_response.get("raw_response", "")
            if not isinstance(raw_response, str) or not raw_response.strip():
                raise ValueError(
                    "Balanced human package requires a preserved model response for every item; "
                    f"none exists in {run_file} for {scenario['id']}"
                )
            source_key = f"{summary['model']}|{summary['prompt_variant']}|{scenario['id']}"
            records.append(
                {
                    "source_key": source_key,
                    "primary_response_status": primary_response.get("status"),
                    "selected_response_status": selected_response.get("status"),
                    "response_source": response_source,
                    "scenario_id": scenario["id"],
                    "evidence": scenario["findings"],
                    "model_output": raw_response,
                    "ratings": {
                        "usefulness": None,
                        "clarity": None,
                        "evidence_fidelity": None,
                        "misinterpretation_risk": None,
                        "recommendation_quality": None,
                        "contains_unsupported_claim": None,
                        "suggests_unauthorized_action": None,
                        "reviewer_note": "",
                    },
                }
            )
    if len(records) != 36:
        raise ValueError(f"Expected 36 blinded items, found {len(records)}")
    if recovery_map is not None and recovery_substitutions != expected_recovery_substitutions:
        raise ValueError(
            f"Expected exactly {expected_recovery_substitutions} preregistered recovery substitutions, "
            f"found {recovery_substitutions}"
        )

    random.Random(seed).shuffle(records)
    reviewer_items = []
    for index, record in enumerate(records, start=1):
        item_id = hashlib.sha256(f"{seed}|{index}|{record['source_key']}".encode()).hexdigest()[:16]
        reviewer_items.append(
            {
                "item_id": item_id,
                "scenario_id": record["scenario_id"],
                "evidence": record["evidence"],
                "model_output": record["model_output"],
                "ratings": record["ratings"],
            }
        )
        mapping.append(
            {
                "item_id": item_id,
                "source_key": record["source_key"],
                "primary_response_status": record["primary_response_status"],
                "selected_response_status": record["selected_response_status"],
                "response_source": record["response_source"],
            }
        )

    package = {
        "schema_version": "1.0",
        "status": "blank-rating-template",
        "reviewer_id": "",
        "items": reviewer_items,
    }
    reviewer_file = Path(reviewer_output)
    mapping_file = Path(mapping_output)
    reviewer_file.parent.mkdir(parents=True, exist_ok=True)
    mapping_file.parent.mkdir(parents=True, exist_ok=True)
    reviewer_file.write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")
    mapping_file.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "seed": seed,
                "recovery_substitutions": recovery_substitutions,
                "recovery_map_sha256": recovery_map_sha256,
                "mapping": mapping,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return package


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix-results", type=Path, required=True)
    parser.add_argument("--reviewer-output", type=Path, required=True)
    parser.add_argument("--mapping-output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260815)
    parser.add_argument("--recovery-map", type=Path)
    arguments = parser.parse_args(argv)
    try:
        package = prepare_blinded_package(
            arguments.matrix_results,
            arguments.reviewer_output,
            arguments.mapping_output,
            seed=arguments.seed,
            recovery_map=arguments.recovery_map,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(f"Prepared {len(package['items'])} blinded rating items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
