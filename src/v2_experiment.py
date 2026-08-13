"""Run the reproducible V2 behavioral benchmark and optional Ollama review."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from .behavior_detector import BehaviorDetector, inventory_context
from .nmap_to_zabbix import NmapParser
from .ollama_advisor import OllamaAdvisor, OllamaOutputError
from .ollama_baseline import HistoricalOllamaAdvisor
from .telemetry import load_telemetry


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65_536), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _metrics(true_positive: int, false_positive: int, false_negative: int, true_negative: int) -> dict[str, Any]:
    precision = _safe_divide(true_positive, true_positive + false_positive)
    recall = _safe_divide(true_positive, true_positive + false_negative)
    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(_safe_divide(2 * precision * recall, precision + recall), 6),
        "specificity": round(_safe_divide(true_negative, true_negative + false_positive), 6),
    }


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to load V2 scenario manifest: {error}") from error
    if not isinstance(manifest, dict) or not isinstance(manifest.get("scenarios"), list):
        raise ValueError("V2 scenario manifest must contain a scenarios array")
    return manifest


def run_benchmark(
    manifest_path: str | Path,
    output_directory: str | Path,
    *,
    ollama_model: str | None = None,
    ollama_url: str = "http://127.0.0.1:11434",
    ollama_context: int = 4096,
    ollama_timeout: float = 300,
    ollama_max_output_tokens: int | None = None,
    ollama_protocol: str = "grounded",
) -> dict[str, Any]:
    """Run all labeled scenarios and write machine- and human-readable reports."""
    manifest_file = Path(manifest_path).resolve()
    manifest = _load_manifest(manifest_file)
    base_directory = manifest_file.parent
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)

    nmap_file = (base_directory / str(manifest["nmap_input"])).resolve()
    nmap_parser = NmapParser(nmap_file)
    hosts = nmap_parser.parse_xml()
    detector = BehaviorDetector(inventory_context(hosts))
    if ollama_protocol not in {"grounded", "historical"}:
        raise ValueError("Ollama protocol must be grounded or historical")
    selected_output_tokens = ollama_max_output_tokens
    if selected_output_tokens is None:
        selected_output_tokens = 700 if ollama_protocol == "grounded" else 512
    advisor_type = OllamaAdvisor if ollama_protocol == "grounded" else HistoricalOllamaAdvisor
    advisor = (
        advisor_type(
            ollama_model,
            base_url=ollama_url,
            timeout=ollama_timeout,
            context_length=ollama_context,
            max_output_tokens=selected_output_tokens,
        )
        if ollama_model
        else None
    )

    totals = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    ollama_totals = {
        "attempts": 0,
        "api_successes": 0,
        "accepted": 0,
        "api_failures": 0,
        "validation_failures": 0,
        "json_parse_valid": 0,
        "schema_valid": 0,
        "unknown_finding_citations": 0,
        "unknown_evidence_citations": 0,
        "unsupported_cve_mentions": 0,
        "absolute_assertions": 0,
        "unsupported_security_attribution_mentions": 0,
        "containment_action_mentions": 0,
        "unqualified_containment_actions": 0,
        "word_limit_violations": 0,
        "markdown_format_violations": 0,
        "finding_coverage_sum": 0.0,
        "evidence_coverage_sum": 0.0,
    }
    scenario_results = []
    all_rule_ids = BehaviorDetector.RULE_IDS

    for scenario in manifest["scenarios"]:
        if not isinstance(scenario, dict):
            raise ValueError("Each V2 scenario must be a JSON object")
        scenario_id = str(scenario.get("id", "")).strip()
        if not scenario_id:
            raise ValueError("Every V2 scenario requires an id")
        telemetry_file = (base_directory / str(scenario["telemetry"])).resolve()
        expected = set(scenario.get("expected_rule_ids", []))
        if not expected <= all_rule_ids:
            raise ValueError(f"Scenario {scenario_id} contains an unknown expected rule")

        events = load_telemetry(telemetry_file)
        findings = [item.to_dict() for item in detector.analyze(events)]
        predicted = {item["rule_id"] for item in findings}
        true_positive = len(expected & predicted)
        false_positive = len(predicted - expected)
        false_negative = len(expected - predicted)
        true_negative = len(all_rule_ids - (expected | predicted))
        totals["tp"] += true_positive
        totals["fp"] += false_positive
        totals["fn"] += false_negative
        totals["tn"] += true_negative

        ollama_result = None
        if advisor and findings:
            ollama_totals["attempts"] += 1
            try:
                advisor_result = advisor.analyze(findings, events)
                ollama_totals["api_successes"] += 1
                if ollama_protocol == "grounded":
                    ollama_result = {"status": "accepted", **advisor_result}
                    ollama_totals["accepted"] += 1
                    ollama_totals["json_parse_valid"] += 1
                    ollama_totals["schema_valid"] += 1
                    ollama_totals["finding_coverage_sum"] += 1.0
                    ollama_totals["evidence_coverage_sum"] += 1.0
                else:
                    audit = advisor_result["audit"]
                    ollama_result = {"status": "observed", **advisor_result}
                    ollama_totals["accepted"] += int(audit["grounding_valid"])
                    ollama_totals["json_parse_valid"] += int(audit["json_parse_valid"])
                    ollama_totals["schema_valid"] += int(audit["schema_valid"])
                    ollama_totals["unknown_finding_citations"] += len(audit["unknown_finding_citations"])
                    ollama_totals["unknown_evidence_citations"] += len(audit["unknown_evidence_citations"])
                    ollama_totals["unsupported_cve_mentions"] += len(audit["unsupported_cve_mentions"])
                    ollama_totals["absolute_assertions"] += len(audit["absolute_assertions"])
                    ollama_totals["unsupported_security_attribution_mentions"] += len(
                        audit["unsupported_security_attribution_mentions"]
                    )
                    ollama_totals["containment_action_mentions"] += len(audit["containment_action_mentions"])
                    ollama_totals["unqualified_containment_actions"] += int(audit["unqualified_containment_action"])
                    ollama_totals["word_limit_violations"] += int(not audit["within_200_word_limit"])
                    ollama_totals["markdown_format_violations"] += int(audit["markdown_marker_present"])
                    ollama_totals["finding_coverage_sum"] += audit["finding_coverage"]
                    ollama_totals["evidence_coverage_sum"] += audit["evidence_coverage"]
            except requests.RequestException as error:
                ollama_result = {
                    "status": "api-failure",
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
                ollama_totals["api_failures"] += 1
            except OllamaOutputError as error:
                ollama_result = {
                    "status": "validation-failure",
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "raw_response": error.raw_response,
                    "metadata": error.metadata,
                }
                ollama_totals["api_successes"] += int(error.metadata.get("api_response_received", True))
                ollama_totals["json_parse_valid"] += int(error.metadata.get("json_parse_valid", False))
                ollama_totals["schema_valid"] += int(error.metadata.get("schema_valid", False))
                ollama_totals["validation_failures"] += 1
            except ValueError as error:
                ollama_result = {
                    "status": "validation-failure",
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
                ollama_totals["validation_failures"] += 1
        scenario_results.append(
            {
                "id": scenario_id,
                "category": scenario.get("category", "unspecified"),
                "description": scenario.get("description", ""),
                "telemetry_file": telemetry_file.relative_to(manifest_file.parent.parent.parent).as_posix(),
                "telemetry_sha256": _sha256(telemetry_file),
                "event_count": len(events),
                "expected_rule_ids": sorted(expected),
                "predicted_rule_ids": sorted(predicted),
                "true_positive": sorted(expected & predicted),
                "false_positive": sorted(predicted - expected),
                "false_negative": sorted(expected - predicted),
                "findings": findings,
                "ollama": ollama_result,
            }
        )

    result = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "dataset": "deterministic benign emulation",
            "purpose": "functional and construct-validity benchmark",
            "not_claimed": [
                "real-world malware detection accuracy",
                "malware-family attribution",
                "confirmed compromise",
                "automated prevention effectiveness",
            ],
        },
        "inputs": {
            "manifest": manifest_file.name,
            "manifest_sha256": _sha256(manifest_file),
            "nmap_file": nmap_file.relative_to(manifest_file.parent.parent.parent).as_posix(),
            "nmap_sha256": _sha256(nmap_file),
        },
        "detector": {
            "rule_ids": sorted(all_rule_ids),
            "thresholds": {
                "periodic_connections_minimum": 6,
                "periodic_interval_cv_maximum": 0.15,
                "service_discovery_endpoints_minimum": 8,
                "service_discovery_window_seconds": 60,
                "asymmetric_egress_bytes_minimum": 1_000_000,
                "asymmetric_egress_ratio_minimum": 10,
                "download_file_window_seconds": 120,
            },
        },
        "metrics": _metrics(totals["tp"], totals["fp"], totals["fn"], totals["tn"]),
        "ollama_evaluation": (
            {
                "protocol": ollama_protocol,
                **{key: value for key, value in ollama_totals.items() if not key.endswith("_sum")},
                "accepted_grounding_rate": round(_safe_divide(ollama_totals["accepted"], ollama_totals["attempts"]), 6),
                "mean_finding_coverage": round(
                    _safe_divide(ollama_totals["finding_coverage_sum"], ollama_totals["api_successes"]), 6
                ),
                "mean_evidence_coverage": round(
                    _safe_divide(ollama_totals["evidence_coverage_sum"], ollama_totals["api_successes"]), 6
                ),
            }
            if advisor
            else None
        ),
        "scenarios": scenario_results,
    }
    (output / "benchmark.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "benchmark.md").write_text(_markdown_report(result), encoding="utf-8")
    return result


def _markdown_report(result: dict[str, Any]) -> str:
    metrics = result["metrics"]
    lines = [
        "# V2 behavioral benchmark",
        "",
        "> This benchmark uses benign, deterministic telemetry emulation. It does not execute malware and does not",
        "> estimate real-world malware-detection accuracy.",
        "",
        "## Aggregate result",
        "",
        "| TP | FP | FN | TN | Precision | Recall | F1 | Specificity |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| {metrics['true_positive']} | {metrics['false_positive']} | {metrics['false_negative']} | "
            f"{metrics['true_negative']} | {metrics['precision']:.3f} | {metrics['recall']:.3f} | "
            f"{metrics['f1']:.3f} | {metrics['specificity']:.3f} |"
        ),
        "",
        "## Scenarios",
        "",
        "| Scenario | Category | Expected | Predicted | FP | FN |",
        "|---|---|---|---|---|---|",
    ]
    for scenario in result["scenarios"]:
        expected = ", ".join(scenario["expected_rule_ids"]) or "none"
        predicted = ", ".join(scenario["predicted_rule_ids"]) or "none"
        false_positive = ", ".join(scenario["false_positive"]) or "none"
        false_negative = ", ".join(scenario["false_negative"]) or "none"
        lines.append(
            f"| {scenario['id']} | {scenario['category']} | {expected} | {predicted} | "
            f"{false_positive} | {false_negative} |"
        )
    ollama = result["ollama_evaluation"]
    if ollama is not None:
        lines.extend(
            [
                "",
                "## Ollama grounding validation",
                "",
                f"Protocol: `{ollama['protocol']}`",
                "",
                "| Attempts | API success | JSON valid | Schema valid | Accepted | Grounding rate | Evidence coverage |",
                "|---:|---:|---:|---:|---:|---:|---:|",
                (
                    f"| {ollama['attempts']} | {ollama['api_successes']} | {ollama['json_parse_valid']} | "
                    f"{ollama['schema_valid']} | {ollama['accepted']} | "
                    f"{ollama['accepted_grounding_rate']:.3f} | {ollama['mean_evidence_coverage']:.3f} |"
                ),
                "",
                "Only scenarios with detector findings are submitted to the advisor. Acceptance means schema and",
                "citation validation passed; it does not establish that a security finding is malicious.",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "The scores establish only whether the transparent rules behave as specified on the committed lab fixtures.",
            "The benign updater scenario intentionally tests a plausible false positive. External validation requires",
            "independently labeled traffic, repeated runs and a pre-registered analysis protocol.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repository_root / "research" / "v2" / "scenarios.json",
    )
    parser.add_argument("--output-dir", type=Path, default=repository_root / "output" / "v2")
    parser.add_argument("--ollama-model", help="Enable grounded local Ollama analysis with this installed model")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument(
        "--ollama-protocol",
        choices=("grounded", "historical"),
        default="grounded",
        help="Use the V2 grounded protocol or the reconstructed 2025 free-text control",
    )
    parser.add_argument("--ollama-context", type=int, default=4096, help="Local model context length in tokens")
    parser.add_argument("--ollama-timeout", type=float, default=300, help="Per-request timeout in seconds")
    parser.add_argument(
        "--ollama-max-output-tokens",
        type=int,
        help="Defaults to 700 for grounded JSON and 512 for the historical free-text control",
    )
    arguments = parser.parse_args(argv)
    try:
        result = run_benchmark(
            arguments.manifest,
            arguments.output_dir,
            ollama_model=arguments.ollama_model,
            ollama_url=arguments.ollama_url,
            ollama_context=arguments.ollama_context,
            ollama_timeout=arguments.ollama_timeout,
            ollama_max_output_tokens=arguments.ollama_max_output_tokens,
            ollama_protocol=arguments.ollama_protocol,
        )
    except (OSError, ValueError, requests.RequestException) as error:
        parser.error(str(error))
    metrics = result["metrics"]
    print(
        f"V2 benchmark: TP={metrics['true_positive']} FP={metrics['false_positive']} "
        f"FN={metrics['false_negative']} F1={metrics['f1']:.3f}"
    )
    print(f"Reports: {arguments.output_dir / 'benchmark.md'}, {arguments.output_dir / 'benchmark.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
