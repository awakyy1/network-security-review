# Repeated V2 Ollama experiment

Protocol: `grounded`  
Repetitions: 5

| Calls | API success | JSON parse | Schema valid | Grounding accepted | Evidence coverage |
|---:|---:|---:|---:|---:|---:|
| 20 | 1.000 | 0.750 | 0.750 | 0.550 | 0.750 |

| Latency observations | Minimum ms | Q1 ms | Median ms | Q3 ms | Maximum ms |
|---:|---:|---:|---:|---:|---:|
| 20 | 1578.752 | 1714.762 | 2161.789 | 7293.283 | 47061.334 |

Not estimable when each scenario yields at most one finding.

> These system-level metrics do not establish malware-detection accuracy or model correctness.
