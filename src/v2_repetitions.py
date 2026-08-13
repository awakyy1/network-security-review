"""Run and aggregate repeated V2 Ollama experiments."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from .ollama_advisor import validate_grounded_schema
from .v2_experiment import run_benchmark


def _safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def aggregate_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate preserved run records without discarding failed model calls."""
    if not results:
        raise ValueError("At least one repeated result is required")
    evaluations = [item["ollama_evaluation"] for item in results]
    if any(item is None for item in evaluations):
        raise ValueError("Repeated aggregation requires Ollama-enabled results")
    protocols = {item["protocol"] for item in evaluations}
    if len(protocols) != 1:
        raise ValueError("Repeated results must use one Ollama protocol")

    count_fields = [
        "attempts",
        "api_successes",
        "accepted",
        "api_failures",
        "validation_failures",
        "json_parse_valid",
        "schema_valid",
        "unknown_finding_citations",
        "unknown_evidence_citations",
        "unsupported_cve_mentions",
        "absolute_assertions",
        "unsupported_security_attribution_mentions",
        "containment_action_mentions",
        "unqualified_containment_actions",
        "word_limit_violations",
        "markdown_format_violations",
    ]
    totals = {field: sum(item[field] for item in evaluations) for field in count_fields}
    protocol = next(iter(protocols))
    json_parse_valid = 0
    schema_valid = 0
    finding_coverage_values: list[float] = []
    evidence_coverage_values: list[float] = []

    latencies = []
    rankings: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    for result in results:
        for scenario in result["scenarios"]:
            ollama = scenario["ollama"]
            if not ollama:
                continue
            if ollama.get("status") != "api-failure":
                if protocol == "historical" and isinstance(ollama.get("audit"), dict):
                    audit = ollama["audit"]
                    json_parse_valid += int(audit["json_parse_valid"])
                    schema_valid += int(audit["schema_valid"])
                    finding_coverage_values.append(float(audit["finding_coverage"]))
                    evidence_coverage_values.append(float(audit["evidence_coverage"]))
                elif protocol == "grounded":
                    parsed = ollama.get("analysis")
                    if parsed is None and isinstance(ollama.get("raw_response"), str):
                        try:
                            parsed = json.loads(ollama["raw_response"])
                        except json.JSONDecodeError:
                            parsed = None
                    if isinstance(parsed, dict):
                        json_parse_valid += 1
                        try:
                            validate_grounded_schema(parsed)
                        except ValueError:
                            pass
                        else:
                            schema_valid += 1
                        finding_index = {item["finding_id"]: item for item in scenario.get("findings", [])}
                        supplied_findings = set(finding_index)
                        supplied_evidence = {
                            evidence
                            for finding in finding_index.values()
                            for evidence in finding.get("evidence_ids", [])
                        }
                        priorities = parsed.get("priorities", []) if isinstance(parsed.get("priorities"), list) else []
                        cited_findings = {
                            item.get("finding_id")
                            for item in priorities
                            if isinstance(item, dict) and item.get("finding_id") in supplied_findings
                        }
                        cited_evidence = {
                            evidence
                            for item in priorities
                            if isinstance(item, dict) and item.get("finding_id") in finding_index
                            for evidence in item.get("evidence_ids", [])
                            if evidence in finding_index[item["finding_id"]].get("evidence_ids", [])
                        }
                        finding_coverage_values.append(_safe_divide(len(cited_findings), len(supplied_findings)))
                        evidence_coverage_values.append(_safe_divide(len(cited_evidence), len(supplied_evidence)))
                    else:
                        finding_coverage_values.append(0.0)
                        evidence_coverage_values.append(0.0)
            if "metadata" not in ollama:
                continue
            elapsed = ollama["metadata"].get("elapsed_ms")
            if isinstance(elapsed, (int, float)):
                latencies.append(float(elapsed))
            analysis = ollama.get("analysis")
            if isinstance(analysis, dict) and isinstance(analysis.get("priorities"), list):
                ranking = tuple(item["finding_id"] for item in analysis["priorities"])
                if len(ranking) > 1:
                    rankings[scenario["id"]].append(ranking)

    ranking_details = {}
    for scenario_id, observed in rankings.items():
        modal_ranking, modal_count = Counter(observed).most_common(1)[0]
        ranking_details[scenario_id] = {
            "observations": len(observed),
            "distinct_rankings": len(set(observed)),
            "modal_ranking": list(modal_ranking),
            "exact_agreement_with_mode": round(modal_count / len(observed), 6),
        }

    detector_metrics = [item["metrics"] for item in results]
    totals["api_successes"] = totals["attempts"] - totals["api_failures"]
    totals["json_parse_valid"] = json_parse_valid
    totals["schema_valid"] = schema_valid
    return {
        "schema_version": "1.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "protocol": protocol,
        "repetitions": len(results),
        "detector_stable_across_repetitions": all(item == detector_metrics[0] for item in detector_metrics),
        "detector_metrics": detector_metrics[0],
        "ollama": {
            **totals,
            "api_success_rate": round(_safe_divide(totals["api_successes"], totals["attempts"]), 6),
            "json_parse_rate": round(_safe_divide(totals["json_parse_valid"], totals["attempts"]), 6),
            "schema_valid_rate": round(_safe_divide(totals["schema_valid"], totals["attempts"]), 6),
            "accepted_grounding_rate": round(_safe_divide(totals["accepted"], totals["attempts"]), 6),
            "mean_finding_coverage": round(_safe_divide(sum(finding_coverage_values), len(finding_coverage_values)), 6),
            "mean_evidence_coverage": round(
                _safe_divide(sum(evidence_coverage_values), len(evidence_coverage_values)), 6
            ),
            "latency_ms": {
                "observations": len(latencies),
                "minimum": round(min(latencies), 3) if latencies else None,
                "q1": round(_percentile(latencies, 0.25), 3) if latencies else None,
                "median": round(statistics.median(latencies), 3) if latencies else None,
                "q3": round(_percentile(latencies, 0.75), 3) if latencies else None,
                "maximum": round(max(latencies), 3) if latencies else None,
            },
            "ranking_stability": ranking_details,
            "ranking_interpretation": (
                "Not estimable when each scenario yields at most one finding."
                if not ranking_details
                else "Exact agreement with the modal ordering, reported per multi-finding scenario."
            ),
        },
        "measurement_note": (
            "Schema 1.1 counts every received response as an API success, including output rejected later by the "
            "deterministic validator; acceptance is reported separately."
        ),
    }


def _markdown_report(summary: dict[str, Any]) -> str:
    ollama = summary["ollama"]
    latency = ollama["latency_ms"]
    return "\n".join(
        [
            "# Repeated V2 Ollama experiment",
            "",
            f"Protocol: `{summary['protocol']}`  ",
            f"Repetitions: {summary['repetitions']}",
            "",
            "| Calls | API success | JSON parse | Schema valid | Grounding accepted | Evidence coverage |",
            "|---:|---:|---:|---:|---:|---:|",
            (
                f"| {ollama['attempts']} | {ollama['api_success_rate']:.3f} | "
                f"{ollama['json_parse_rate']:.3f} | {ollama['schema_valid_rate']:.3f} | "
                f"{ollama['accepted_grounding_rate']:.3f} | {ollama['mean_evidence_coverage']:.3f} |"
            ),
            "",
            "| Latency observations | Minimum ms | Q1 ms | Median ms | Q3 ms | Maximum ms |",
            "|---:|---:|---:|---:|---:|---:|",
            (
                f"| {latency['observations']} | {latency['minimum']} | {latency['q1']} | "
                f"{latency['median']} | {latency['q3']} | {latency['maximum']} |"
            ),
            "",
            summary["ollama"]["ranking_interpretation"],
            "",
            "> These system-level metrics do not establish malware-detection accuracy or model correctness.",
            "",
        ]
    )


def run_repetitions(
    manifest: str | Path,
    output_directory: str | Path,
    *,
    model: str,
    protocol: str,
    repetitions: int,
    ollama_url: str = "http://127.0.0.1:11434",
    ollama_context: int = 4096,
    ollama_timeout: float = 300,
    ollama_max_output_tokens: int | None = None,
) -> dict[str, Any]:
    if not 1 <= repetitions <= 100:
        raise ValueError("Repetitions must be between 1 and 100")
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for index in range(1, repetitions + 1):
        run_output = output / f"run-{index:03d}"
        results.append(
            run_benchmark(
                manifest,
                run_output,
                ollama_model=model,
                ollama_url=ollama_url,
                ollama_context=ollama_context,
                ollama_timeout=ollama_timeout,
                ollama_max_output_tokens=ollama_max_output_tokens,
                ollama_protocol=protocol,
            )
        )
    summary = aggregate_results(results)
    summary["model"] = model
    summary["manifest"] = Path(manifest).as_posix()
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "summary.md").write_text(_markdown_report(summary), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=repository_root / "research" / "v2" / "scenarios.json")
    parser.add_argument("--output-dir", type=Path, default=repository_root / "output" / "v2-repetitions")
    parser.add_argument("--ollama-model", required=True)
    parser.add_argument("--ollama-protocol", choices=("grounded", "historical"), required=True)
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--ollama-context", type=int, default=4096)
    parser.add_argument("--ollama-timeout", type=float, default=300)
    parser.add_argument("--ollama-max-output-tokens", type=int)
    arguments = parser.parse_args(argv)
    try:
        summary = run_repetitions(
            arguments.manifest,
            arguments.output_dir,
            model=arguments.ollama_model,
            protocol=arguments.ollama_protocol,
            repetitions=arguments.repetitions,
            ollama_url=arguments.ollama_url,
            ollama_context=arguments.ollama_context,
            ollama_timeout=arguments.ollama_timeout,
            ollama_max_output_tokens=arguments.ollama_max_output_tokens,
        )
    except (OSError, ValueError, requests.RequestException) as error:
        parser.error(str(error))
    print(
        f"Repeated V2 experiment: protocol={summary['protocol']} repetitions={summary['repetitions']} "
        f"accepted_grounding_rate={summary['ollama']['accepted_grounding_rate']:.3f}"
    )
    print(f"Summary: {arguments.output_dir / 'summary.md'}, {arguments.output_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
