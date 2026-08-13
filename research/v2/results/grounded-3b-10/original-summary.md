# Repeated V2 Ollama experiment

Protocol: `grounded`  
Repetitions: 10

| Calls | API success | JSON parse | Schema valid | Grounding accepted | Evidence coverage |
|---:|---:|---:|---:|---:|---:|
| 50 | 0.800 | 0.800 | 0.800 | 0.800 | 1.000 |

| Latency observations | Minimum ms | Q1 ms | Median ms | Q3 ms | Maximum ms |
|---:|---:|---:|---:|---:|---:|
| 50 | 20015.849 | 23296.877 | 31636.802 | 33375.362 | 110933.692 |

Not estimable when each scenario yields at most one finding.

> These system-level metrics do not establish malware-detection accuracy or model correctness.
