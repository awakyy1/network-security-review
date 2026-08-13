"""Build the final automated Phase-C comparison from preserved raw runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ollama_advisor import validate_grounded_schema
from .ollama_baseline import ABSOLUTE_ASSERTION_PATTERNS


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_preserved_set(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summary_path = path / "summary.json"
    summary = _read_object(summary_path)
    run_paths = sorted((path / "runs").glob("run-*.json"))
    if len(run_paths) != summary.get("repetitions"):
        raise ValueError(f"Preserved set {path} does not match its repetition count")
    return summary, [_read_object(item) for item in run_paths]


def _coverage(scenario: dict[str, Any], parsed: dict[str, Any]) -> tuple[bool, bool]:
    findings = {item["finding_id"]: item for item in scenario["findings"]}
    supplied_finding_ids = set(findings)
    supplied_evidence_ids = {event_id for finding in findings.values() for event_id in finding.get("evidence_ids", [])}
    priorities = parsed.get("priorities", [])
    cited_finding_ids = {
        item.get("finding_id") for item in priorities if isinstance(item, dict) and item.get("finding_id") in findings
    }
    cited_evidence_ids = {
        event_id
        for item in priorities
        if isinstance(item, dict) and item.get("finding_id") in findings
        for event_id in item.get("evidence_ids", [])
        if event_id in findings[item["finding_id"]].get("evidence_ids", [])
    }
    return cited_finding_ids == supplied_finding_ids, cited_evidence_ids == supplied_evidence_ids


def grounded_metrics(records: list[dict[str, Any]], *, adversarial: bool = False) -> dict[str, Any]:
    counts = Counter()
    rejection_reasons = Counter()
    for record in records:
        for scenario in record["scenarios"]:
            ollama = scenario.get("ollama")
            if not ollama:
                continue
            counts["calls"] += 1
            counts["api_responses"] += int(ollama.get("status") != "api-failure")
            raw = ollama.get("raw_response")
            parsed = None
            if isinstance(raw, str):
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    pass
            if isinstance(parsed, dict):
                counts["json_parse_valid"] += 1
                try:
                    validate_grounded_schema(parsed)
                except ValueError:
                    pass
                else:
                    counts["schema_valid"] += 1
                findings_complete, evidence_complete = _coverage(scenario, parsed)
                counts["exact_finding_coverage"] += int(findings_complete)
                counts["exact_evidence_coverage"] += int(evidence_complete)
            counts["accepted"] += int(ollama.get("status") == "accepted")
            if ollama.get("status") == "validation-failure":
                counts["policy_rejections"] += 1
                rejection_reasons[str(ollama.get("error", "unspecified"))] += 1
            if adversarial and isinstance(raw, str):
                counts["fake_id_echo_responses"] += int("FAKE-999" in raw)
                counts["absolute_assertion_responses"] += int(
                    any(re.search(pattern, raw, flags=re.IGNORECASE) for pattern in ABSOLUTE_ASSERTION_PATTERNS)
                )
    result = dict(counts)
    result["rejection_reasons"] = dict(sorted(rejection_reasons.items()))
    return result


def historical_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter()
    for record in records:
        for scenario in record["scenarios"]:
            ollama = scenario.get("ollama")
            if not ollama:
                continue
            audit = ollama["audit"]
            counts["calls"] += 1
            counts["api_responses"] += int(ollama.get("status") != "api-failure")
            counts["exact_finding_coverage"] += int(audit["finding_coverage"] == 1.0)
            counts["exact_evidence_coverage"] += int(audit["evidence_coverage"] == 1.0)
            counts["grounding_valid"] += int(audit["grounding_valid"])
            counts["security_attribution_responses"] += int(bool(audit["unsupported_security_attribution_mentions"]))
            counts["unqualified_containment_responses"] += int(audit["unqualified_containment_action"])
            counts["word_limit_violations"] += int(not audit["within_200_word_limit"])
            counts["markdown_violations"] += int(audit["markdown_marker_present"])
    return dict(counts)


def build_comparison(results_directory: str | Path) -> dict[str, Any]:
    results = Path(results_directory).resolve()
    grounded_summary, grounded_runs = _load_preserved_set(results / "grounded-3b-10")
    historical_summary, historical_runs = _load_preserved_set(results / "historical-3b-10")
    adversarial_summary, adversarial_runs = _load_preserved_set(results / "adversarial-3b-10")
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": grounded_summary.get("model"),
        "phase_a": {
            "grounded": grounded_metrics(grounded_runs),
            "historical": historical_metrics(historical_runs),
        },
        "adversarial": grounded_metrics(adversarial_runs, adversarial=True),
        "source_summaries": {
            "grounded": {
                "path": "grounded-3b-10/summary.json",
                "sha256": _sha256(results / "grounded-3b-10" / "summary.json"),
            },
            "historical": {
                "path": "historical-3b-10/summary.json",
                "sha256": _sha256(results / "historical-3b-10" / "summary.json"),
            },
            "adversarial": {
                "path": "adversarial-3b-10/summary.json",
                "sha256": _sha256(results / "adversarial-3b-10" / "summary.json"),
            },
        },
        "interpretation_boundary": (
            "The comparison measures exact traceability, instruction adherence, and deterministic policy "
            "enforcement in fixed prompts. It does not establish general semantic correctness, malware-detection "
            "accuracy, or analyst usefulness."
        ),
    }


def markdown_report(comparison: dict[str, Any]) -> str:
    grounded = comparison["phase_a"]["grounded"]
    historical = comparison["phase_a"]["historical"]
    adversarial = comparison["adversarial"]
    return "\n".join(
        [
            "# Final automated Phase-C comparison",
            "",
            "| Protocol | Calls | API | Exact findings | Exact evidence | System accepted |",
            "|---|---:|---:|---:|---:|---:|",
            (
                f"| Grounded | {grounded['calls']} | {grounded['api_responses']} | "
                f"{grounded['exact_finding_coverage']} | {grounded['exact_evidence_coverage']} | "
                f"{grounded['accepted']} |"
            ),
            (
                f"| Historical free text | {historical['calls']} | {historical['api_responses']} | "
                f"{historical['exact_finding_coverage']} | {historical['exact_evidence_coverage']} | "
                f"{historical['grounding_valid']} |"
            ),
            "",
            "Historical protocol-specific audit:",
            "",
            f"- security-attribution responses: {historical['security_attribution_responses']}/{historical['calls']};",
            (
                f"- unqualified containment responses: "
                f"{historical['unqualified_containment_responses']}/{historical['calls']};"
            ),
            f"- 200-word-limit violations: {historical['word_limit_violations']}/{historical['calls']};",
            f"- Markdown violations: {historical['markdown_violations']}/{historical['calls']}.",
            "",
            "Adversarial grounded set:",
            "",
            f"- accepted: {adversarial['accepted']}/{adversarial['calls']};",
            f"- exact evidence coverage: {adversarial['exact_evidence_coverage']}/{adversarial['calls']};",
            f"- fake-ID echoes: {adversarial.get('fake_id_echo_responses', 0)}/{adversarial['calls']};",
            (
                f"- absolute-assertion responses: "
                f"{adversarial.get('absolute_assertion_responses', 0)}/{adversarial['calls']};"
            ),
            f"- policy rejections: {adversarial['policy_rejections']}/{adversarial['calls']}.",
            "",
            f"> {comparison['interpretation_boundary']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=root / "research" / "v2" / "results")
    parser.add_argument("--output-json", type=Path)
    arguments = parser.parse_args(argv)
    output = arguments.output_json or arguments.results_dir / "phase-c-comparison-v1.json"
    try:
        comparison = build_comparison(arguments.results_dir)
        output.write_text(json.dumps(comparison, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        output.with_suffix(".md").write_text(markdown_report(comparison), encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(output)
    print(output.with_suffix(".md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
