"""Run the frozen, resumable V1.1 multi-model and prompt-variant matrix."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from .ctu13_acquire import sha256_file
from .v2_experiment import run_benchmark
from .v2_repetitions import _markdown_report, aggregate_results


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected one JSON object in {path}")
    return value


def _local_models(base_url: str) -> dict[str, dict[str, Any]]:
    response = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=15)
    response.raise_for_status()
    return {item["name"]: item for item in response.json().get("models", [])}


def run_matrix(
    matrix_path: str | Path,
    output_directory: str | Path,
    *,
    base_url: str = "http://127.0.0.1:11434",
) -> dict[str, Any]:
    matrix_file = Path(matrix_path).resolve()
    matrix = _load_json(matrix_file)
    allowed_statuses = {
        "frozen-ready-for-primary-inference",
        "frozen-ready-for-supplemental-inference",
    }
    if matrix.get("status") not in allowed_statuses:
        raise ValueError("LLM matrix is not frozen and ready for inference")

    repository_root = matrix_file.parent.parent.parent
    for relative_path, expected_hash in matrix["code_hashes_at_preregistration"].items():
        if sha256_file(repository_root / relative_path).lower() != expected_hash.lower():
            raise ValueError(f"Frozen LLM code hash mismatch: {relative_path}")

    protocol = matrix["protocol"]
    scenario_manifest = matrix_file.parent / protocol["manifest"]
    if sha256_file(scenario_manifest).lower() != protocol["manifest_sha256"].lower():
        raise ValueError("Frozen LLM scenario-manifest SHA-256 mismatch")
    for relative_path, expected_hash in matrix.get("frozen_fixture_hashes", {}).items():
        fixture = matrix_file.parent / relative_path
        if sha256_file(fixture).lower() != expected_hash.lower():
            raise ValueError(f"Frozen LLM fixture SHA-256 mismatch: {relative_path}")
    selection_evidence = matrix.get("selection_evidence")
    if selection_evidence:
        primary_benchmark = matrix_file.parent / selection_evidence["primary_benchmark"]
        if sha256_file(primary_benchmark).lower() != selection_evidence["primary_benchmark_sha256"].lower():
            raise ValueError("Frozen selection-evidence benchmark SHA-256 mismatch")

    installed = _local_models(base_url)
    for model in matrix["models"]:
        local = installed.get(model["tag"])
        if not local or local.get("digest") != model["local_manifest_digest"]:
            raise ValueError(f"Local model digest mismatch: {model['tag']}")

    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    cells = []
    for model in matrix["models"]:
        for variant in protocol["prompt_variants"]:
            cell_directory = output / _slug(model["tag"]) / variant
            results = []
            for repetition in range(1, protocol["repetitions_per_cell"] + 1):
                run_directory = cell_directory / f"run-{repetition:03d}"
                result_file = run_directory / "benchmark.json"
                if result_file.is_file():
                    results.append(_load_json(result_file))
                    continue
                results.append(
                    run_benchmark(
                        scenario_manifest,
                        run_directory,
                        ollama_model=model["tag"],
                        ollama_url=base_url,
                        ollama_context=protocol["context_length"],
                        ollama_max_output_tokens=protocol["maximum_output_tokens"],
                        ollama_protocol="grounded",
                        ollama_prompt_variant=variant,
                    )
                )
            summary = aggregate_results(results)
            summary.update(
                {
                    "model": model["tag"],
                    "model_digest": model["local_manifest_digest"],
                    "prompt_variant": variant,
                    "scenario_manifest_sha256": protocol["manifest_sha256"],
                    "temperature": protocol["temperature"],
                    "top_p": protocol["top_p"],
                    "seed": protocol["seed"],
                    "context_length": protocol["context_length"],
                    "maximum_output_tokens": protocol["maximum_output_tokens"],
                }
            )
            cell_directory.mkdir(parents=True, exist_ok=True)
            (cell_directory / "summary.json").write_text(
                json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            (cell_directory / "summary.md").write_text(_markdown_report(summary), encoding="utf-8")
            cells.append(summary)

    result = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_role": matrix.get("evidence_role", "frozen-primary-multi-model-matrix"),
        "matrix": matrix_file.name,
        "matrix_sha256_at_execution": sha256_file(matrix_file),
        "expected_model_calls": protocol["model_calls_expected"],
        "observed_model_calls": sum(cell["ollama"]["attempts"] for cell in cells),
        "cells": cells,
        "automatic_actions_executed": 0,
        "human_semantic_ratings": "not-yet-collected",
    }
    (output / "matrix-summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    arguments = parser.parse_args(argv)
    try:
        result = run_matrix(arguments.matrix, arguments.output_dir, base_url=arguments.ollama_url)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, requests.RequestException) as error:
        parser.error(str(error))
    print(f"V1.1 LLM matrix: observed={result['observed_model_calls']} expected={result['expected_model_calls']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
