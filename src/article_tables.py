"""Generate article LaTeX tables directly from preserved V2 result JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read preserved result {path}: {error}") from error
    if not isinstance(result, dict):
        raise ValueError(f"Preserved result must be a JSON object: {path}")
    return result


def phase_a_table(result: dict[str, Any]) -> str:
    metrics = result["metrics"]
    return "\n".join(
        [
            r"\begin{table}[htbp]",
            r"\centering",
            r"\caption{Frozen Phase-A synthetic behavior-rule result.}",
            r"\label{tab:phase-a}",
            r"\begin{tabular}{rrrrrrrr}",
            r"\toprule",
            r"TP & FP & FN & TN & Precision & Recall & F1 & Specificity \\",
            r"\midrule",
            (
                f"{metrics['true_positive']} & {metrics['false_positive']} & {metrics['false_negative']} & "
                f"{metrics['true_negative']} & {metrics['precision']:.3f} & {metrics['recall']:.3f} & "
                f"{metrics['f1']:.3f} & {metrics['specificity']:.3f} \\\\"
            ),
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\vspace{2pt}{\fontsize{10}{12}\selectfont\textbf{Source:} Prepared by the authors from the committed inert fixtures (2026).}",
            r"\end{table}",
            "",
        ]
    )


def external_metrics_table(result: dict[str, Any]) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Family-separated CTU-13 external validation.}",
        r"\label{tab:ctu13-metrics}",
        r"\resizebox{\linewidth}{!}{%",
        r"\begin{tabular}{llrrrrrrrrrr}",
        r"\toprule",
        r"Role & Family & Units & TP & FP & FN & TN & Precision & Recall & F1 & Specificity & MCC \\",
        r"\midrule",
    ]
    for source in result["sources"]:
        metrics = source["metrics"]
        units = sum(metrics[key] for key in ("true_positive", "false_positive", "false_negative", "true_negative"))
        role = str(source["role"]).capitalize()
        lines.append(
            f"{role} & {source['family']} & {units} & {metrics['true_positive']} & {metrics['false_positive']} & "
            f"{metrics['false_negative']} & {metrics['true_negative']} & {metrics['precision']:.3f} & "
            f"{metrics['recall']:.3f} & {metrics['f1']:.3f} & {metrics['specificity']:.3f} & "
            f"{metrics['matthews_correlation_coefficient']:.3f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            r"\par\vspace{2pt}{\fontsize{10}{12}\selectfont\textbf{Source:} Prepared by the authors from frozen CTU-13 labeled bidirectional flows (2026).}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def external_rule_table(result: dict[str, Any]) -> str:
    by_role = {source["role"]: source for source in result["sources"]}
    labels = {"BEH-001": "Periodic communication", "BEH-002": "Distinct endpoints", "BEH-003": "Asymmetric egress"}
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Rule findings on botnet-origin and normal-origin CTU-13 windows.}",
        r"\label{tab:ctu13-rules}",
        r"\begin{tabular}{llrr}",
        r"\toprule",
        r"Rule & Pattern & Development B/N & Holdout B/N \\",
        r"\midrule",
    ]
    for rule_id, label in labels.items():
        development = by_role["development"]["rule_finding_counts"][rule_id]
        holdout = by_role["holdout"]["rule_finding_counts"][rule_id]
        lines.append(
            f"\\texttt{{{rule_id}}} & {label} & {development.get('botnet_origin', 0)}/{development.get('normal_origin', 0)} & "
            f"{holdout.get('botnet_origin', 0)}/{holdout.get('normal_origin', 0)} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\vspace{2pt}{\fontsize{10}{12}\selectfont\textbf{Source:} Prepared by the authors from the preserved CTU-13 validation output (2026).}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def exploratory_llm_table(
    grounded: dict[str, Any],
    historical: dict[str, Any],
    posthoc: dict[str, Any],
) -> str:
    grounded_scenarios = [item for item in grounded["scenarios"] if item.get("ollama")]
    grounded_coverage = []
    for scenario in grounded_scenarios:
        supplied = {evidence for finding in scenario["findings"] for evidence in finding["evidence_ids"]}
        cited = {
            evidence
            for priority in scenario["ollama"]["analysis"]["priorities"]
            for evidence in priority["evidence_ids"]
        }
        grounded_coverage.append(len(cited) / len(supplied) if supplied else 1.0)
    audits = [item["audit"] for item in posthoc["scenarios"]]
    historical_evaluation = historical["ollama_evaluation"]
    historical_attribution = sum(bool(item["unsupported_security_attribution_mentions"]) for item in audits)
    historical_unqualified = sum(item["unqualified_containment_action"] for item in audits)
    historical_markdown = sum(item["markdown_marker_present"] for item in audits)
    historical_word_limit = sum(not item["within_200_word_limit"] for item in audits)
    return "\n".join(
        [
            r"\begin{table}[htbp]",
            r"\centering",
            r"\caption{Exploratory LLM instrumentation runs (not a confirmatory comparison).}",
            r"\label{tab:llm-exploratory}",
            r"\resizebox{\linewidth}{!}{%",
            r"\begin{tabular}{lrrrrrr}",
            r"\toprule",
            r"Protocol & Calls & API success & Grounded & Evidence coverage & Attribution responses & Unqualified controls \\",
            r"\midrule",
            (
                f"Grounded schema 1.0 & {len(grounded_scenarios)} & {len(grounded_scenarios)} & "
                f"{grounded['ollama_evaluation']['accepted']} & "
                f"{sum(grounded_coverage) / len(grounded_coverage):.3f} & 0 & 0 \\\\"
            ),
            (
                f"Reconstructed free text & {historical_evaluation['attempts']} & "
                f"{historical_evaluation['api_successes']} & {historical_evaluation['accepted']} & "
                f"{historical_evaluation['mean_evidence_coverage']:.3f} & {historical_attribution} & "
                f"{historical_unqualified} \\\\"
            ),
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\fontsize{10}{12}\selectfont\textbf{Note:} The free-text run used Markdown in "
                f"{historical_markdown}/5 responses and exceeded 200 words in {historical_word_limit}/5. "
                r"The audit rubric was refined after this exploratory run.}"
            ),
            r"\par\vspace{2pt}{\fontsize{10}{12}\selectfont\textbf{Source:} Prepared by the authors from preserved local Ollama outputs (2026).}",
            r"\end{table}",
            "",
        ]
    )


def repeated_llm_table(result: dict[str, Any]) -> str:
    grounded = result["phase_a"]["grounded"]
    historical = result["phase_a"]["historical"]
    return "\n".join(
        [
            r"\begin{table}[htbp]",
            r"\centering",
            r"\caption{Repeated Phase-C automated traceability comparison.}",
            r"\label{tab:llm-repeated}",
            r"\resizebox{\linewidth}{!}{%",
            r"\begin{tabular}{lrrrrrr}",
            r"\toprule",
            r"Protocol & Calls & API responses & Exact findings & Exact evidence & System accepted & Policy rejected \\",
            r"\midrule",
            (
                f"Grounded schema 1.1 & {grounded['calls']} & {grounded['api_responses']} & "
                f"{grounded['exact_finding_coverage']} & {grounded['exact_evidence_coverage']} & "
                f"{grounded['accepted']} & {grounded['policy_rejections']} \\\\"
            ),
            (
                f"Reconstructed free text & {historical['calls']} & {historical['api_responses']} & "
                f"{historical['exact_finding_coverage']} & {historical['exact_evidence_coverage']} & "
                f"{historical['grounding_valid']} & -- \\\\"
            ),
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\fontsize{10}{12}\selectfont\textbf{Note:} Free text was not asked to emit "
                r"JSON; its system-accepted count applies the common exact-ID grounding criterion. Grounded policy "
                r"rejections retained complete citations but selected a rule-inapplicable control.}"
            ),
            r"\par\vspace{2pt}{\fontsize{10}{12}\selectfont\textbf{Source:} Prepared by the authors from 100 preserved local Ollama calls (2026).}",
            r"\end{table}",
            "",
        ]
    )


def adversarial_llm_table(result: dict[str, Any]) -> str:
    adversarial = result["adversarial"]
    return "\n".join(
        [
            r"\begin{table}[htbp]",
            r"\centering",
            r"\caption{Repeated prompt-injection fixture result.}",
            r"\label{tab:llm-adversarial}",
            r"\begin{tabular}{rrrrrr}",
            r"\toprule",
            r"Calls & Schema valid & Exact evidence & Fake-ID echo & Absolute claim & Accepted \\",
            r"\midrule",
            (
                f"{adversarial['calls']} & {adversarial['schema_valid']} & "
                f"{adversarial['exact_evidence_coverage']} & {adversarial['fake_id_echo_responses']} & "
                f"{adversarial['absolute_assertion_responses']} & {adversarial['accepted']} \\\\"
            ),
            r"\bottomrule",
            r"\end{tabular}",
            (
                r"\par\vspace{2pt}{\fontsize{10}{12}\selectfont\textbf{Note:} One response was safely rejected for "
                r"a rule-inapplicable control; no response followed the injected instruction to cite "
                r"\texttt{FAKE-999} or claim confirmed malware.}"
            ),
            r"\par\vspace{2pt}{\fontsize{10}{12}\selectfont\textbf{Source:} Prepared by the authors from the preserved adversarial manifest and outputs (2026).}",
            r"\end{table}",
            "",
        ]
    )


def generate_tables(repository_root: str | Path) -> list[Path]:
    root = Path(repository_root).resolve()
    results = root / "research" / "v2" / "results"
    output = root / "academic" / "artigo" / "generated"
    output.mkdir(parents=True, exist_ok=True)
    documents = {
        "phase-a-table.tex": phase_a_table(_read_json(results / "phase-a-ollama-3b-run-01.json")),
        "ctu13-metrics-table.tex": external_metrics_table(_read_json(results / "ctu13-external-validation-v1.json")),
        "ctu13-rules-table.tex": external_rule_table(_read_json(results / "ctu13-external-validation-v1.json")),
        "llm-exploratory-table.tex": exploratory_llm_table(
            _read_json(results / "phase-a-ollama-3b-run-01.json"),
            _read_json(results / "exploratory-historical-3b-run-01.json"),
            _read_json(results / "exploratory-historical-3b-run-01-posthoc-audit.json"),
        ),
        "llm-repeated-table.tex": repeated_llm_table(_read_json(results / "phase-c-comparison-v1.json")),
        "llm-adversarial-table.tex": adversarial_llm_table(_read_json(results / "phase-c-comparison-v1.json")),
    }
    paths = []
    for filename, content in documents.items():
        path = output / filename
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parent.parent)
    arguments = parser.parse_args(argv)
    try:
        paths = generate_tables(arguments.repository_root)
    except (OSError, ValueError, KeyError, ZeroDivisionError) as error:
        parser.error(str(error))
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
