# Repeated V2 Ollama experiment

Protocol: `grounded`  
Repetitions: 5

| Calls | API success | JSON parse | Schema valid | Grounding accepted | Evidence coverage |
|---:|---:|---:|---:|---:|---:|
| 20 | 1.000 | 0.800 | 0.800 | 0.100 | 0.712 |

| Latency observations | Minimum ms | Q1 ms | Median ms | Q3 ms | Maximum ms |
|---:|---:|---:|---:|---:|---:|
| 20 | 4141.615 | 5521.788 | 7551.833 | 9499.842 | 10604.691 |

Not estimable when each scenario yields at most one finding.

> These system-level metrics do not establish malware-detection accuracy or model correctness.
