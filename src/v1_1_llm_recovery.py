"""Run the frozen V1.1 Qwen availability-recovery sample without altering primary evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from .ctu13_acquire import sha256_file
from .v1_1_llm_matrix import _load_json, _local_models
from .v2_experiment import run_benchmark


def run_recovery(
    protocol_path: str | Path,
    output_directory: str | Path,
    *,
    base_url: str = "http://127.0.0.1:11434",
) -> dict[str, Any]:
    protocol_file = Path(protocol_path).resolve()
    recovery = _load_json(protocol_file)
    if recovery.get("status") != "frozen-ready-for-availability-recovery":
        raise ValueError("Recovery protocol is not frozen and ready for inference")

    repository_root = protocol_file.parent.parent.parent
    retry = recovery.get("retry_of")
    if retry:
        for path_key, hash_key in (
            ("protocol", "protocol_sha256"),
            ("benchmark", "benchmark_sha256"),
            ("summary", "summary_sha256"),
        ):
            prior_file = protocol_file.parent / retry[path_key]
            if sha256_file(prior_file).lower() != retry[hash_key].lower():
                raise ValueError(f"Frozen prior-recovery {path_key} SHA-256 mismatch")
    for relative_path, expected_hash in recovery["code_hashes_at_preregistration"].items():
        if sha256_file(repository_root / relative_path).lower() != expected_hash.lower():
            raise ValueError(f"Frozen recovery code hash mismatch: {relative_path}")

    primary_summary = protocol_file.parent / recovery["source_primary_matrix"]
    if sha256_file(primary_summary).lower() != recovery["source_primary_matrix_sha256"].lower():
        raise ValueError("Frozen primary-matrix summary SHA-256 mismatch")
    source_matrix = protocol_file.parent / recovery["source_matrix_definition"]
    if sha256_file(source_matrix).lower() != recovery["source_matrix_definition_sha256"].lower():
        raise ValueError("Frozen primary-matrix definition SHA-256 mismatch")
    source_matrix_definition = _load_json(source_matrix)
    for relative_path, expected_hash in source_matrix_definition["frozen_fixture_hashes"].items():
        fixture = source_matrix.parent / relative_path
        if sha256_file(fixture).lower() != expected_hash.lower():
            raise ValueError(f"Frozen primary fixture SHA-256 mismatch: {relative_path}")
    manifest = protocol_file.parent / recovery["manifest"]
    if sha256_file(manifest).lower() != recovery["manifest_sha256"].lower():
        raise ValueError("Frozen recovery scenario-manifest SHA-256 mismatch")

    installed = _local_models(base_url)
    model = recovery["model"]
    local = installed.get(model["tag"])
    if not local or local.get("digest") != model["local_manifest_digest"]:
        raise ValueError(f"Local model digest mismatch: {model['tag']}")

    primary_results = protocol_file.parent / recovery["source_primary_results_directory"]
    original_run = _load_json(primary_results / "qwen3-8b" / "checklist-v1" / "run-001" / "benchmark.json")
    original_statuses = {
        scenario["id"]: (scenario.get("ollama") or {}).get("status")
        for scenario in original_run["scenarios"]
        if scenario["id"] in recovery["selected_failures"]
    }
    if original_statuses != {item: "api-failure" for item in recovery["selected_failures"]}:
        raise ValueError("Selected recovery items are not exactly the preserved primary API failures")

    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    result_file = output / "benchmark.json"
    if result_file.is_file():
        benchmark = _load_json(result_file)
    else:
        settings = recovery["protocol"]
        benchmark = run_benchmark(
            manifest,
            output,
            ollama_model=model["tag"],
            ollama_url=base_url,
            ollama_context=settings["context_length"],
            ollama_max_output_tokens=settings["maximum_output_tokens"],
            ollama_protocol="grounded",
            ollama_prompt_variant=settings["prompt_variant"],
        )

    recovered_items = []
    for scenario in benchmark["scenarios"]:
        if scenario["id"] not in recovery["selected_failures"]:
            continue
        response = scenario.get("ollama") or {}
        recovered_items.append(
            {
                "scenario_id": scenario["id"],
                "status": response.get("status", "missing"),
                "raw_response_preserved": bool(response.get("raw_response")),
            }
        )
    observed_ids = {item["scenario_id"] for item in recovered_items}
    if observed_ids != set(recovery["selected_failures"]):
        raise ValueError("Recovery benchmark did not contain exactly the preregistered items")

    ollama = benchmark["ollama_evaluation"]
    summary = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_role": "availability-recovery-for-blinded-human-sample",
        "protocol": protocol_file.name,
        "protocol_sha256_at_execution": sha256_file(protocol_file),
        "source_primary_matrix_sha256": recovery["source_primary_matrix_sha256"],
        "primary_results_modified": False,
        "primary_denominators_recomputed": False,
        "expected_model_calls": recovery["protocol"]["model_calls_expected"],
        "observed_model_calls": ollama["attempts"],
        "api_successes": ollama["api_successes"],
        "accepted": ollama["accepted"],
        "recovered_items": recovered_items,
        "all_selected_items_have_raw_response": all(item["raw_response_preserved"] for item in recovered_items),
        "automatic_actions_executed": 0,
    }
    (output / "recovery-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    arguments = parser.parse_args(argv)
    try:
        summary = run_recovery(
            arguments.protocol,
            arguments.output_dir,
            base_url=arguments.ollama_url,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, requests.RequestException) as error:
        parser.error(str(error))
    print(
        f"V1.1 recovery: observed={summary['observed_model_calls']} "
        f"expected={summary['expected_model_calls']} api_successes={summary['api_successes']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
