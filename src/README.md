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
| `article_tables.py` | LaTeX table generation from preserved JSON evidence |

The modules are intentionally direct and separated by evidence boundary for
academic auditability. See the [current-system map](../docs/CURRENT_SYSTEM.md),
[architecture](../docs/ARCHITECTURE.md) and
[security model](../docs/SECURITY_MODEL.md).
