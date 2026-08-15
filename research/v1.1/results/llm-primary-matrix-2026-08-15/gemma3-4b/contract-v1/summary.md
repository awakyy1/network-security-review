# Repeated V2 Ollama experiment

Protocol: `grounded`  
Repetitions: 5

| Calls | API success | JSON parse | Schema valid | Grounding accepted | Evidence coverage |
|---:|---:|---:|---:|---:|---:|
| 20 | 1.000 | 0.950 | 0.950 | 0.550 | 0.879 |

| Latency observations | Minimum ms | Q1 ms | Median ms | Q3 ms | Maximum ms |
|---:|---:|---:|---:|---:|---:|
| 20 | 3879.37 | 4227.972 | 4761.038 | 9568.368 | 33350.566 |

Not estimable when each scenario yields at most one finding.

> These system-level metrics do not establish malware-detection accuracy or model correctness.
