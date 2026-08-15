"""Run the preregistered V1.1 LLM component ablations without changing frozen primary code."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import requests

from . import v2_experiment
from .ctu13_acquire import sha256_file
from .ollama_advisor import (
    OUTPUT_SCHEMA,
    RULE_CONTROLS,
    OllamaAdvisor,
    OllamaOutputError,
    validate_grounded_output,
    validate_grounded_schema,
)
from .telemetry import TelemetryEvent
from .v1_1_llm_matrix import _local_models
from .v2_repetitions import _markdown_report, aggregate_results

REDUCED_SYSTEM_PROMPT = (
    "You are a defensive security review assistant. Review the supplied findings and return only JSON "
    "matching the supplied schema."
)


def _request_payload(
    *,
    model: str,
    prompt: str,
    condition: str,
    context_length: int,
    maximum_output_tokens: int,
) -> dict[str, Any]:
    """Build a request in which exactly the preregistered component is changed."""
    temperature = 0.7 if condition == "temperature-0.7" else 0
    payload: dict[str, Any] = {
        "model": model,
        "system": REDUCED_SYSTEM_PROMPT if condition == "grounding-language-reduced" else None,
        "prompt": prompt,
        "format": OUTPUT_SCHEMA,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "seed": 42,
            "num_ctx": context_length,
            "num_predict": maximum_output_tokens,
        },
    }
    if condition == "api-format-removed":
        payload.pop("format")
    return payload


class AblationAdvisor(OllamaAdvisor):
    """Grounded advisor with one controlled request-level change."""

    def __init__(self, *args: Any, condition: str, **kwargs: Any):
        super().__init__(*args, **kwargs)
        if condition not in {"temperature-0.7", "api-format-removed", "grounding-language-reduced"}:
            raise ValueError(f"Unknown call-producing ablation condition: {condition}")
        self.condition = condition

    def analyze(self, findings: list[dict[str, Any]], events: list[TelemetryEvent]) -> dict[str, Any]:
        evidence_index = {item.event_id: item.to_evidence() for item in events}
        evidence_pack = [
            {
                "finding": finding,
                "events": [evidence_index[item] for item in finding["evidence_ids"] if item in evidence_index],
            }
            for finding in findings
        ]
        schema = json.dumps(OUTPUT_SCHEMA, ensure_ascii=False, sort_keys=True)
        controls = json.dumps({key: sorted(value) for key, value in RULE_CONTROLS.items()}, sort_keys=True)
        evidence = json.dumps(evidence_pack, ensure_ascii=False, sort_keys=True)
        if self.condition == "grounding-language-reduced":
            prompt = (
                f"Review these findings.\nJSON schema: {schema}\nRule/control map: {controls}\nEvidence:\n{evidence}"
            )
        else:
            from .ollama_advisor import SYSTEM_PROMPT, build_grounded_prompt

            prompt = build_grounded_prompt(self.prompt_variant, evidence_pack)

        payload = _request_payload(
            model=self.model,
            prompt=prompt,
            condition=self.condition,
            context_length=self.context_length,
            maximum_output_tokens=self.max_output_tokens,
        )
        if payload["system"] is None:
            payload["system"] = SYSTEM_PROMPT
        started = time.perf_counter()
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        body = response.json()
        raw_response = body.get("response", "")
        metadata = {
            "model": body.get("model", self.model),
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
            "ollama_total_duration_ns": body.get("total_duration"),
            "prompt_eval_count": body.get("prompt_eval_count"),
            "eval_count": body.get("eval_count"),
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "schema_version": "1.1",
            "prompt_variant": self.prompt_variant,
            "ablation_condition": self.condition,
            "api_response_received": True,
            "json_parse_valid": False,
            "schema_valid": False,
            "grounding_valid": False,
            "temperature": payload["options"]["temperature"],
            "top_p": 0.9,
            "seed": 42,
            "context_length": self.context_length,
            "max_output_tokens": self.max_output_tokens,
            "request_timeout_seconds": self.timeout,
            "api_format_schema_supplied": "format" in payload,
            "full_grounding_language_supplied": self.condition != "grounding-language-reduced",
        }
        try:
            parsed = json.loads(raw_response)
        except (TypeError, json.JSONDecodeError) as error:
            raise OllamaOutputError(
                "Ollama returned no valid structured response",
                raw_response=raw_response if isinstance(raw_response, str) else repr(raw_response),
                metadata=metadata,
            ) from error
        metadata["json_parse_valid"] = True
        try:
            validate_grounded_schema(parsed)
        except ValueError as error:
            raise OllamaOutputError(str(error), raw_response=raw_response, metadata=metadata) from error
        metadata["schema_valid"] = True
        try:
            validated = validate_grounded_output(parsed, findings)
        except ValueError as error:
            raise OllamaOutputError(str(error), raw_response=raw_response, metadata=metadata) from error
        metadata["grounding_valid"] = True
        return {"analysis": validated, "raw_response": raw_response, "metadata": metadata}


@contextmanager
def _patched_advisor(condition: str) -> Iterator[None]:
    original = v2_experiment.OllamaAdvisor

    def factory(*args: Any, **kwargs: Any) -> AblationAdvisor:
        return AblationAdvisor(*args, condition=condition, **kwargs)

    v2_experiment.OllamaAdvisor = factory  # type: ignore[assignment]
    try:
        yield
    finally:
        v2_experiment.OllamaAdvisor = original


def _validator_bypass_summary(reference_results: list[dict[str, Any]]) -> dict[str, Any]:
    copied = json.loads(json.dumps(reference_results))
    for result in copied:
        evaluation = result["ollama_evaluation"]
        evaluation["accepted"] = evaluation["api_successes"]
        for scenario in result["scenarios"]:
            response = scenario.get("ollama")
            if response and response.get("status") != "api-failure":
                response["status"] = "usable-without-validator"
    summary = aggregate_results(copied)
    summary["posthoc_policy"] = (
        "Every received API response is counted as usable; this unsafe condition was never connected to operations."
    )
    return summary


def run_ablation_matrix(
    matrix_path: str | Path,
    primary_directory: str | Path,
    output_directory: str | Path,
    *,
    base_url: str = "http://127.0.0.1:11434",
) -> dict[str, Any]:
    matrix_file = Path(matrix_path).resolve()
    matrix = json.loads(matrix_file.read_text(encoding="utf-8"))
    if matrix.get("status") != "frozen-ready-for-ablation-inference":
        raise ValueError("Ablation matrix is not frozen and ready for inference")
    repository_root = matrix_file.parent.parent.parent
    for relative_path, expected_hash in matrix["scientific_code"].items():
        if sha256_file(repository_root / relative_path).lower() != expected_hash.lower():
            raise ValueError(f"Ablation scientific-code hash mismatch: {relative_path}")
    scenario_manifest = matrix_file.parent / matrix["scenario_manifest"]["path"]
    if sha256_file(scenario_manifest).lower() != matrix["scenario_manifest"]["sha256"].lower():
        raise ValueError("Ablation scenario-manifest SHA-256 mismatch")
    installed = _local_models(base_url)
    model = matrix["model"]
    if installed.get(model["tag"], {}).get("digest") != model["digest"]:
        raise ValueError("Ablation local-model digest mismatch")

    primary = Path(primary_directory)
    reference_paths = [
        primary / "llama3-2-3b" / "contract-v1" / f"run-{index:03d}" / "benchmark.json" for index in range(1, 4)
    ]
    if not all(path.is_file() for path in reference_paths):
        raise ValueError("The first three frozen primary Llama/contract repetitions are required")
    reference_results = [json.loads(path.read_text(encoding="utf-8")) for path in reference_paths]
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []

    reference_summary = aggregate_results(reference_results)
    reference_summary.update({"condition": "reference-primary-reuse", "new_calls": 0})
    summaries.append(reference_summary)

    parameters = matrix["base_parameters"]
    for condition in ("temperature-0.7", "api-format-removed", "grounding-language-reduced"):
        condition_directory = output / condition
        results = []
        with _patched_advisor(condition):
            for repetition in range(1, matrix["repetitions"] + 1):
                run_directory = condition_directory / f"run-{repetition:03d}"
                result_file = run_directory / "benchmark.json"
                if result_file.is_file():
                    results.append(json.loads(result_file.read_text(encoding="utf-8")))
                else:
                    results.append(
                        v2_experiment.run_benchmark(
                            scenario_manifest,
                            run_directory,
                            ollama_model=model["tag"],
                            ollama_url=base_url,
                            ollama_context=parameters["context_length"],
                            ollama_max_output_tokens=parameters["maximum_output_tokens"],
                            ollama_protocol="grounded",
                            ollama_prompt_variant=parameters["prompt_variant"],
                        )
                    )
        summary = aggregate_results(results)
        summary.update({"condition": condition, "new_calls": summary["ollama"]["attempts"]})
        condition_directory.mkdir(parents=True, exist_ok=True)
        (condition_directory / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        (condition_directory / "summary.md").write_text(_markdown_report(summary), encoding="utf-8")
        summaries.append(summary)

    bypass = _validator_bypass_summary(reference_results)
    bypass.update({"condition": "validator-bypass-posthoc", "new_calls": 0})
    summaries.append(bypass)
    result = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_role": "preregistered-component-sensitivity-ablation",
        "matrix": matrix_file.name,
        "matrix_sha256_at_execution": sha256_file(matrix_file),
        "expected_new_calls": matrix["expected_new_calls"],
        "observed_new_calls": sum(item["new_calls"] for item in summaries),
        "conditions": summaries,
        "automatic_actions_executed": 0,
        "claim_boundary": matrix["claim_boundary"],
    }
    (output / "ablation-summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--primary-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    arguments = parser.parse_args(argv)
    try:
        result = run_ablation_matrix(
            arguments.matrix,
            arguments.primary_dir,
            arguments.output_dir,
            base_url=arguments.ollama_url,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, requests.RequestException) as error:
        parser.error(str(error))
    print(f"V1.1 ablation matrix: observed={result['observed_new_calls']} expected={result['expected_new_calls']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
