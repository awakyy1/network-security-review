# V2 behavioral benchmark

> This benchmark uses benign, deterministic telemetry emulation. It does not execute malware and does not
> estimate real-world malware-detection accuracy.

## Aggregate result

| TP | FP | FN | TN | Precision | Recall | F1 | Specificity |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 6 | 1 | 0 | 13 | 0.857 | 1.000 | 0.923 | 0.929 |

## Scenarios

| Scenario | Category | Expected | Predicted | FP | FN |
|---|---|---|---|---|---|
| benign-web | benign | none | none | none | none |
| benign-updater-hard-negative | benign-hard-negative | none | BEH-001 | BEH-001 | none |
| incomplete-single-observation | incomplete-evidence | BEH-003 | BEH-003 | none | none |
| endpoint-lineage | endpoint-lineage | BEH-004 | BEH-004 | none | none |
| multi-finding-mixed-rules | multi-finding-ranking | BEH-001, BEH-002, BEH-003, BEH-004 | BEH-001, BEH-002, BEH-003, BEH-004 | none | none |

## Ollama grounding validation

Protocol: `grounded`

| Attempts | API success | JSON valid | Schema valid | Accepted | Grounding rate | Evidence coverage |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 4 | 2 | 2 | 2 | 0.500 | 0.662 |

Only scenarios with detector findings are submitted to the advisor. Acceptance means schema and
citation validation passed; it does not establish that a security finding is malicious.

## Interpretation boundary

The scores establish only whether the transparent rules behave as specified on the committed lab fixtures.
The benign updater scenario intentionally tests a plausible false positive. External validation requires
independently labeled traffic, repeated runs and a pre-registered analysis protocol.
