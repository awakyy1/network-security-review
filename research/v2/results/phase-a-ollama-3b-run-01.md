# V2 behavioral benchmark

> This benchmark uses benign, deterministic telemetry emulation. It does not execute malware and does not
> estimate real-world malware-detection accuracy.

## Aggregate result

| TP | FP | FN | TN | Precision | Recall | F1 | Specificity |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 1 | 0 | 19 | 0.800 | 1.000 | 0.889 | 0.950 |

## Scenarios

| Scenario | Category | Expected | Predicted | FP | FN |
|---|---|---|---|---|---|
| benign-web | benign | none | none | none | none |
| benign-updater | benign-hard-negative | none | BEH-001 | BEH-001 | none |
| emulated-beacon | benign-emulation | BEH-001 | BEH-001 | none | none |
| emulated-service-discovery | benign-emulation | BEH-002 | BEH-002 | none | none |
| emulated-asymmetric-egress | benign-emulation | BEH-003 | BEH-003 | none | none |
| emulated-tool-transfer | benign-emulation | BEH-004 | BEH-004 | none | none |

## Ollama grounding validation

| Attempts | Accepted | API failures | Validation failures | Accepted grounding rate |
|---:|---:|---:|---:|---:|
| 5 | 5 | 0 | 0 | 1.000 |

Only scenarios with detector findings are submitted to the advisor. Acceptance means schema and
citation validation passed; it does not establish that a security finding is malicious.

## Interpretation boundary

The scores establish only whether the transparent rules behave as specified on the committed lab fixtures.
The benign updater scenario intentionally tests a plausible false positive. External validation requires
independently labeled traffic, repeated runs and a pre-registered analysis protocol.
