"""Generate article LaTeX tables directly from preserved V2 result JSON."""

from __future__ import annotations

import argparse
import json
import re
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
            r"\resizebox{\columnwidth}{!}{%",
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
            r"\end{tabular}%",
            r"}",
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
        r"\resizebox{\columnwidth}{!}{%",
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
            r"\end{tabular}%",
            r"}",
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
                f"{historical['grounding_valid']} & N/A \\\\"
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


def primary_llm_matrix_table(result: dict[str, Any]) -> str:
    """Render all frozen model/prompt cells, including API and validator failures."""
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{V1.1 primary local-LLM matrix; each cell contains 20 attempted calls.}",
        r"\label{tab:llm-primary-matrix}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llrrrrrrr}",
        r"\toprule",
        r"Model & Prompt & Calls & API & JSON & Schema & Accepted & Finding cov. & Evidence cov. \\",
        r"\midrule",
    ]
    for cell in result["cells"]:
        ollama = cell["ollama"]
        lines.append(
            f"{cell['model']} & {cell['prompt_variant']} & {ollama['attempts']} & "
            f"{ollama['api_successes']} & {ollama['json_parse_valid']} & {ollama['schema_valid']} & "
            f"{ollama['accepted']} & {ollama['mean_finding_coverage']:.3f} & "
            f"{ollama['mean_evidence_coverage']:.3f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} API is the number of responses received; "
                r"JSON and Schema are representation checks; Accepted additionally requires the frozen "
                r"deterministic semantic-policy validator. Coverage is averaged over attempted finding-bearing "
                r"scenarios, so API failures contribute zero.}"
            ),
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def llm_supplement_table(result: dict[str, Any]) -> str:
    """Render the 31-event conflicting-context stress-test denominators."""
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Supplemental 31-event conflicting-context LLM stress test.}",
        r"\label{tab:llm-supplement}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lrrrrrrrr}",
        r"\toprule",
        r"Model & Calls & API & JSON & Schema & Accepted & Output cap & Complete ranks & Rank agreement \\",
        r"\midrule",
    ]
    for model in result["per_model"]:
        agreement = model["ranking_exact_agreement_with_mode"]
        agreement_text = "N/A" if agreement is None else f"{agreement:.3f}"
        lines.append(
            f"{model['model']} & {model['attempts']} & {model['api_responses']} & "
            f"{model['json_parse_valid']} & {model['schema_valid']} & "
            f"{model['grounding_accepted']} & {model['output_limit_reached']} & "
            f"{model['complete_known_finding_rankings']} & {agreement_text} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} All nine inputs plus their reserved output "
                r"fit the 16,384-token context. Output cap counts responses reaching 900 generated tokens. "
                r"Ranking agreement is estimable only for schema-valid outputs containing every exact finding "
                r"identifier once; repeatability is not semantic correctness.}"
            ),
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def llm_ablation_table(result: dict[str, Any]) -> str:
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Single-model component-sensitivity ablation.}",
        r"\label{tab:llm-ablation}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lrrrrrrrr}",
        r"\toprule",
        r"Condition & New calls & Attempts & API & JSON & Schema & Accepted & Finding cov. & Evidence cov. \\",
        r"\midrule",
    ]
    labels = {
        "reference-primary-reuse": "Reference (primary reuse)",
        "temperature-0.7": "Temperature 0.7",
        "api-format-removed": "API format removed",
        "grounding-language-reduced": "Grounding language reduced",
        "validator-bypass-posthoc": "Validator bypass (post hoc)",
    }
    for condition in result["conditions"]:
        ollama = condition["ollama"]
        lines.append(
            f"{labels[condition['condition']]} & {condition['new_calls']} & {ollama['attempts']} & "
            f"{ollama['api_successes']} & {ollama['json_parse_valid']} & {ollama['schema_valid']} & "
            f"{ollama['accepted']} & {ollama['mean_finding_coverage']:.3f} & "
            f"{ollama['mean_evidence_coverage']:.3f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} Reference and validator-bypass rows reuse the "
                r"same 12 primary responses. Bypass counts every API response as usable and was never connected "
                r"to operations. Three clustered repetitions support descriptive sensitivity only.}"
            ),
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def adversarial_matrix_table(result: dict[str, Any]) -> str:
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Adversarial paired-output availability and eligible decision changes.}",
        r"\label{tab:llm-adversarial-matrix}",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Model & Calls & Responses & Failures & Eligible pairs & Parseable pairs \\",
        r"\midrule",
    ]
    for model, metrics in result["models"].items():
        lines.append(
            f"{model} & {metrics['attempted_calls']} & {metrics['api_responses']} & "
            f"{metrics['api_failures']} & {metrics['pairs_with_both_api_responses']} & "
            f"{metrics['pairs_with_both_parseable']} \\\\"
        )
    lines.extend(
        [
            r"\midrule",
            r"\multicolumn{6}{l}{\textit{Decision changes among eligible pairs}} \\",
            r"Metric & Changed & Eligible & \multicolumn{3}{l}{} \\",
            r"\midrule",
        ]
    )
    metric_labels = {
        "accepted_status_changed": "Validator status",
        "priority_label_changed": "Priority label",
        "control_set_changed": "Control set",
        "finding_order_changed": "Finding order",
        "cited_evidence_set_changed": "Evidence set",
        "unsupported_claim_flag_changed": "Lexical safety flag",
    }
    for metric, label in metric_labels.items():
        value = result["metrics"][metric]
        lines.append(f"{label} & {value['changed']} & {value['eligible_pairs']} & & & \\\\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} A pair is eligible for status comparison only "
                r"when both API responses exist, and for structural comparison only when both are parseable. "
                r"Two API failures are not treated as an unchanged decision. One observation per pair does not "
                r"estimate attack-success probability.}"
            ),
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def environment_comparison_table(result: dict[str, Any]) -> str:
    environments = result["environments"]
    if not environments:
        raise ValueError("Environment comparison requires at least one environment")
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Execution-environment provenance for the preserved V1.0 runs and V1.1 development.}",
        r"\label{tab:environment-comparison}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llllll}",
        r"\toprule",
        r"Research state & Operating system & CPU & Topology & RAM (GiB) & Inference device \\",
        r"\midrule",
    ]
    for environment in environments:
        lines.append(
            f"{environment['research_state']} & {environment['operating_system']} & "
            f"{environment['cpu']} & {environment['cpu_topology']} & "
            f"{environment['memory_gib']:.1f} & {environment['inference_device']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} The V1.1 row is an environment inventory, "
                r"not evidence that a V1.1 experiment had already run. Cross-machine latency is descriptive "
                r"only because hardware, operating system, driver, runtime version, and CPU/GPU placement differ.}"
            ),
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def retrospective_window_table(result: dict[str, Any]) -> str:
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Retrospective CTU-13 sensitivity analysis across fixed aggregation windows.}",
        r"\label{tab:ctu13-windows}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llrrrrrrrrr}",
        r"\toprule",
        r"Role & Family & Window (s) & Units & TP & FP & FN & TN & F1 & Specificity & MCC \\",
        r"\midrule",
    ]
    for analysis in result["analyses"]:
        metrics = analysis["metrics"]
        units = sum(metrics[key] for key in ("true_positive", "false_positive", "false_negative", "true_negative"))
        lines.append(
            f"{str(analysis['role']).capitalize()} & {analysis['family']} & {analysis['window_seconds']} & "
            f"{units} & {metrics['true_positive']} & {metrics['false_positive']} & "
            f"{metrics['false_negative']} & {metrics['true_negative']} & {metrics['f1']:.3f} & "
            f"{metrics['specificity']:.3f} & {metrics['matthews_correlation_coefficient']:.3f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} Thresholds were not retuned. Because the "
                r"V1.0 holdout had already been inspected, all window comparisons are diagnostic rather than "
                r"confirmatory and cannot be used to restore an untouched-holdout claim.}"
            ),
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def retrospective_threshold_table(result: dict[str, Any]) -> str:
    five_minute = [analysis for analysis in result["analyses"] if analysis["window_seconds"] == 300]
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Five-minute component diagnostics for the three network-flow rules.}",
        r"\label{tab:ctu13-threshold-diagnostics}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llrrrrrrrrrr}",
        r"\toprule",
        (
            r"Role & Truth & Units & \multicolumn{4}{c}{BEH-001 failure path/match} & "
            r"\multicolumn{2}{c}{BEH-002 destinations} & \multicolumn{3}{c}{BEH-003 component matches} \\"
        ),
        r"\cmidrule(lr){4-7}\cmidrule(lr){8-9}\cmidrule(lr){10-12}",
        r" & & & $<6$ & No mean & CV$>0.15$ & Match & Median & Max. & $\geq1$ MB & Ratio$\geq10$ & Both \\",
        r"\midrule",
    ]
    for analysis in five_minute:
        for truth in ("botnet-origin", "normal-origin"):
            beh_001 = analysis["beh_001_threshold_diagnostics"][truth]
            beh_003 = analysis["beh_003_threshold_diagnostics"][truth]
            destinations = analysis["feature_distributions"][truth]["maximum_distinct_endpoints_in_60_seconds"]
            lines.append(
                f"{str(analysis['role']).capitalize()} & {truth} & {beh_001['units']} & "
                f"{beh_001['below_six_connections_to_one_endpoint']} & "
                f"{beh_001['six_connections_but_no_eligible_mean_interval']} & "
                f"{beh_001['eligible_mean_interval_but_cv_above_0_15']} & "
                f"{beh_001['meets_beh_001_thresholds']} & {destinations['median']:g} & "
                f"{destinations['maximum']:g} & {beh_003['units_meeting_1mb_sent']} & "
                f"{beh_003['units_meeting_10_to_1_ratio']} & "
                f"{beh_003['units_meeting_both_thresholds']} \\\\"
            )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} BEH-001 categories are mutually exclusive. "
                r"BEH-002 reports each unit's maximum distinct destinations in any 60-second interval. "
                r"BEH-003 component counts do not assert that the underlying behavior was absent.}"
            ),
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def retrospective_error_examples_table(result: dict[str, Any]) -> str:
    analysis = next(item for item in result["analyses"] if item["role"] == "holdout" and item["window_seconds"] == 300)
    labels = {
        "true_positive": "TP",
        "false_positive": "FP",
        "false_negative": "FN",
    }
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Deterministically selected five-minute holdout examples.}",
        r"\label{tab:ctu13-error-examples}",
        r"\resizebox{\linewidth}{!}{%",
        r"\begin{tabular}{llrrrrr}",
        r"\toprule",
        r"Class & Rule & Events & Evidence IDs & Max. destinations & Max. sent (KiB) & Max. ratio \\",
        r"\midrule",
    ]
    for key in ("true_positive", "false_positive", "false_negative"):
        example = analysis["examples"][key]
        features = example["features"]
        rule = ",".join(example["rule_ids"]) if example["rule_ids"] else "N/A"
        lines.append(
            f"{labels[key]} & {rule} & {features['event_count']} & {len(example['evidence_ids'])} & "
            f"{features['maximum_distinct_endpoints_in_60_seconds']} & "
            f"{features['maximum_bytes_sent_on_one_connection'] / 1024:.1f} & "
            f"{features['maximum_sent_received_ratio']:.3f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} Examples are selected by a deterministic "
                r"class/time/host ordering from anonymized source-window units; the preserved JSON retains "
                r"the exact finding and evidence identifiers.}"
            ),
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def confirmatory_ctu13_table(development: dict[str, Any], holdout: dict[str, Any]) -> str:
    development_metrics = development["selected"]["metrics"]
    holdout_evaluation = holdout["evaluation"]
    holdout_metrics = holdout_evaluation["metrics"]
    rows = (
        ("Development", development["source"]["family"], development_metrics),
        ("Confirmatory holdout", holdout_evaluation["family"], holdout_metrics),
    )
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Prospective V1.1 development selection and single confirmatory CTU-13 holdout.}",
        r"\label{tab:ctu13-confirmatory}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llrrrrrrrrrr}",
        r"\toprule",
        r"Role & Family & Units & TP & FP & FN & TN & Precision & Recall & F1 & Specificity & MCC \\",
        r"\midrule",
    ]
    for role, family, metrics in rows:
        units = sum(metrics[key] for key in ("true_positive", "false_positive", "false_negative", "true_negative"))
        lines.append(
            f"{role} & {family} & {units} & {metrics['true_positive']} & {metrics['false_positive']} & "
            f"{metrics['false_negative']} & {metrics['true_negative']} & {metrics['precision']:.3f} & "
            f"{metrics['recall']:.3f} & {metrics['f1']:.3f} & {metrics['specificity']:.3f} & "
            f"{metrics['matthews_correlation_coefficient']:.3f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} The 243-configuration grid was evaluated "
                r"only on RBot. The selected configuration and scientific source hashes were frozen before "
                r"the DonBot file was parsed once. Development and holdout metrics are not pooled.}"
            ),
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def second_dataset_table(result: dict[str, Any]) -> str:
    metrics = result["metrics"]
    units = sum(metrics[key] for key in ("true_positive", "false_positive", "false_negative", "true_negative"))
    return "\n".join(
        [
            r"\begin{table*}[t]",
            r"\centering",
            r"\caption{Frozen detector replay on the second, synthetic implementation-transfer dataset.}",
            r"\label{tab:second-dataset-transfer}",
            r"\resizebox{\textwidth}{!}{%",
            r"\begin{tabular}{lrrrrrrrrrr}",
            r"\toprule",
            "Role & Units & TP & FP & FN & TN & Precision & Recall & F1 & Specificity & MCC \\\\",
            r"\midrule",
            (
                f"Implementation transfer & {units} & {metrics['true_positive']} & "
                f"{metrics['false_positive']} & {metrics['false_negative']} & {metrics['true_negative']} & "
                f"{metrics['precision']:.3f} & {metrics['recall']:.3f} & {metrics['f1']:.3f} & "
                f"{metrics['specificity']:.3f} & {metrics['matthews_correlation_coefficient']:.3f} \\\\"
            ),
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} The Botnet Group Activity source is synthetic "
                r"and derives group patterns from CTU-13. It tests parser and detector transfer, not independent "
                r"real-world generalization; these metrics are not pooled with CTU-13.}"
            ),
            r"\end{table*}",
            "",
        ]
    )


def endpoint_truth_table(result: dict[str, Any]) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Frozen inert BEH-004 endpoint truth matrix.}",
        r"\label{tab:endpoint-beh004}",
        r"\resizebox{\columnwidth}{!}{%",
        r"\begin{tabular}{lccc}",
        r"\toprule",
        "Condition & Expected & Predicted & Outcome \\\\",
        r"\midrule",
    ]
    for item in result["truth_matrix"]:
        label = str(item["id"]).replace("-", " ").capitalize()
        expected = "Yes" if item["expected_beh_004"] else "No"
        predicted = "Yes" if item["predicted_beh_004"] else "No"
        outcome = str(item["outcome"]).replace("_", " ").upper()
        lines.append(f"{label} & {expected} & {predicted} & {outcome} \\\\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} Nmap enrichment changed only the "
                r"known-asset context; all finding identifiers and decisions were identical without inventory. "
                r"This is functional validation on constructed evidence, not endpoint accuracy.}"
            ),
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def counterfactual_policy_table(result: dict[str, Any]) -> str:
    labels = {
        "historical-nsis-ay": "Historical NSIS.ay",
        "confirmatory-donbot": "Confirmatory DonBot",
        "synthetic-implementation-transfer": "Synthetic transfer",
    }
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Offline containment-policy counterfactuals; no action was executed.}",
        r"\label{tab:counterfactual-policies}",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Dataset role & \multicolumn{3}{c}{Block every alert} & \multicolumn{3}{c}{Block after two rules} \\",
        r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
        r" & Actions & Normal & Bot missed & Actions & Normal & Bot missed \\",
        r"\midrule",
    ]
    for key, label in labels.items():
        policies = result["datasets"][key]["policies"]
        alert = policies["automatic_block_on_alert"]
        two = policies["automatic_block_after_two_rules"]
        lines.append(
            f"{label} & {alert['containment_actions']} & {alert['normal_origin_actions']} & "
            f"{alert['botnet_origin_without_action']} & {two['containment_actions']} & "
            f"{two['normal_origin_actions']} & {two['botnet_origin_without_action']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            (
                r"\par\vspace{2pt}{\footnotesize\textit{Note:} Dataset labels indicate source origin, not "
                r"business impact. Approval-gated rate limiting and confirmation-gated isolation executed "
                r"zero actions because the required decisions are absent; evidence collection and monitoring "
                r"do not contain hosts.}"
            ),
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def _standardize_table_layout(content: str) -> str:
    """Keep tables compact and readable in the one-column article."""
    content = content.replace(r"\begin{table*}[t]", r"\begin{table}[htbp]")
    content = content.replace(r"\end{table*}", r"\end{table}")
    content = re.sub(r"(\\label\{tab:[^}]+\}\n)", r"\1\\small\n", content)
    content = re.sub(
        r"\\resizebox\{(\\(?:columnwidth|linewidth|textwidth))\}\{!\}\{%\n"
        r"(\\begin\{tabular\}.*?\\end\{tabular\})%\n\}",
        r"\\begin{adjustbox}{max width=\1}\n\2\n\\end{adjustbox}",
        content,
        flags=re.DOTALL,
    )
    content = content.replace(r"{\fontsize{10}{12}\selectfont", r"{\raggedright\fontsize{9}{11}\selectfont")
    content = content.replace(r"{\footnotesize", r"{\raggedright\footnotesize")
    content = re.sub(
        r"\\textbf\{Source:\} Prepared by the authors from .*? \(2026\)\.",
        r"\\textbf{Source:} Research data (2026).",
        content,
    )
    if r"\textbf{Source:}" not in content:
        source = (
            r"\par\vspace{2pt}{\raggedright\fontsize{9}{11}\selectfont"
            r"\textbf{Source:} Research data (2026).}" + "\n"
        )
        content = content.replace(r"\end{table}", source + r"\end{table}")
    return content


def generate_tables(repository_root: str | Path) -> list[Path]:
    root = Path(repository_root).resolve()
    results = root / "research" / "v2" / "results"
    output = root / "academic" / "artigo" / "generated"
    output.mkdir(parents=True, exist_ok=True)
    v1_1_results = root / "research" / "v1.1"
    retrospective = _read_json(
        v1_1_results / "results" / "ctu13-retrospective-window-analysis-2026-08-15" / "ctu13-window-analysis.json"
    )
    confirmatory_development = _read_json(
        v1_1_results / "results" / "ctu13-confirmatory-development-2026-08-15" / "development-tuning.json"
    )
    confirmatory_holdout = _read_json(
        v1_1_results / "results" / "ctu13-confirmatory-holdout-2026-08-15" / "confirmatory-holdout.json"
    )
    second_dataset = _read_json(
        v1_1_results / "results" / "second-dataset-transfer-2026-08-15" / "second-dataset-transfer.json"
    )
    endpoint = _read_json(v1_1_results / "results" / "endpoint-beh004-2026-08-15" / "endpoint-beh004.json")
    counterfactual = _read_json(
        v1_1_results / "results" / "counterfactual-policies-2026-08-15" / "counterfactual-policies.json"
    )
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
        "environment-comparison-table.tex": environment_comparison_table(
            _read_json(v1_1_results / "environment-development-2026-08-15.json")
        ),
        "ctu13-window-analysis-table.tex": retrospective_window_table(retrospective),
        "ctu13-threshold-diagnostics-table.tex": retrospective_threshold_table(retrospective),
        "ctu13-error-examples-table.tex": retrospective_error_examples_table(retrospective),
        "ctu13-confirmatory-table.tex": confirmatory_ctu13_table(confirmatory_development, confirmatory_holdout),
        "second-dataset-transfer-table.tex": second_dataset_table(second_dataset),
        "endpoint-beh004-table.tex": endpoint_truth_table(endpoint),
        "counterfactual-policies-table.tex": counterfactual_policy_table(counterfactual),
        "llm-primary-matrix-table.tex": primary_llm_matrix_table(
            _read_json(v1_1_results / "results" / "llm-primary-matrix-2026-08-15" / "matrix-summary.json")
        ),
        "llm-supplement-table.tex": llm_supplement_table(
            _read_json(v1_1_results / "results" / "llm-supplement-matrix-2026-08-15" / "supplemental-audit.json")
        ),
        "llm-ablation-table.tex": llm_ablation_table(
            _read_json(v1_1_results / "results" / "llm-ablation-matrix-2026-08-15" / "ablation-summary.json")
        ),
        "llm-adversarial-matrix-table.tex": adversarial_matrix_table(
            _read_json(
                v1_1_results / "results" / "llm-adversarial-matrix-2026-08-15" / "adversarial-denominator-audit.json"
            )
        ),
    }
    paths = []
    for filename, content in documents.items():
        path = output / filename
        path.write_text(_standardize_table_layout(content), encoding="utf-8")
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
