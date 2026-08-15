# Source modules

| Module | Purpose |
|---|---|
| `nmap_to_zabbix.py` | Parser, transparent review rules, report generation, Zabbix client and CLI orchestration |
| `dashboard.py` | Escaped, self-contained HTML dashboard renderer |
| `telemetry.py` | Strict normalized JSONL telemetry loader with stable evidence records |
| `behavior_detector.py` | Four transparent behavioral review rules and stable finding IDs |
| `ollama_advisor.py` | Loopback-only grounded Ollama protocol and deterministic semantic validator |
| `ollama_baseline.py` | Reconstructed historical free-text control and protocol-specific audit |
| `v2_experiment.py` | Labeled functional benchmark and optional local-model evaluation |
| `v2_repetitions.py` | Repeated-run orchestration and aggregate stability measurements |
| `result_preservation.py` | Byte-preserving promotion, hashes and measurement-boundary correction |
| `phase_c_analysis.py` | Final automated grounded/historical/adversarial comparison |
| `ctu13_acquire.py` | Restricted acquisition and verification of frozen CTU-13 text flows |
| `ctu13_experiment.py` | Streaming family-separated external validation |
| `ctu13_analysis.py` | V1.1 multi-window feature distributions, BEH-003 diagnostics and TP/FP/FN examples |
| `ctu13_confirmatory.py` | Frozen-grid development selection and source-state-gated single CTU-13 holdout run |
| `v1_1_llm_matrix.py` | Frozen, resumable primary and supplemental local-model matrices |
| `v1_1_llm_recovery.py` | Separately preserved Qwen availability recovery without primary-result replacement |
| `llm_posthoc_analysis.py` | Primary multi-finding ranking audit over preserved responses |
| `llm_supplement_analysis.py` | 31-event supplement denominators, output-limit and ranking audit |
| `human_evaluation.py` | Blinded 36-item reviewer-package and concealed-mapping generation |
| `human_evaluation_analysis.py` | Strict completed-rating validation, descriptive aggregation and pairwise agreement |
| `article_tables.py` | LaTeX table generation from preserved JSON evidence |
| `article_figures.py` | PDF/PNG figure generation from preserved evidence and declared architecture |
| `endpoint_experiment.py` | Frozen inert BEH-004 endpoint-lineage truth matrix |
| `second_dataset_experiment.py` | Streaming implementation-transfer replay on the frozen second source |
| `counterfactual_policies.py` | Offline response-policy replay with zero operational actions |
| `v1_1_reproduce.py` | One-command deterministic verification, regeneration and PDF build without LLM inference |

The modules are intentionally direct and separated by evidence boundary for
academic auditability. See the [current-system map](../docs/CURRENT_SYSTEM.md),
[architecture](../docs/ARCHITECTURE.md) and
[security model](../docs/SECURITY_MODEL.md).
