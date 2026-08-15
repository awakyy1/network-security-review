# V2 behavioral benchmark

> This benchmark uses benign, deterministic telemetry emulation. It does not execute malware and does not
> estimate real-world malware-detection accuracy.

## Aggregate result

| TP | FP | FN | TN | Precision | Recall | F1 | Specificity |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 3 | 1.000 | 1.000 | 1.000 | 1.000 |

## Scenarios

| Scenario | Category | Expected | Predicted | FP | FN |
|---|---|---|---|---|---|
| endpoint-lineage | endpoint-lineage | BEH-004 | BEH-004 | none | none |

## Ollama grounding validation

Protocol: `grounded`

| Attempts | API success | JSON valid | Schema valid | Accepted | Grounding rate | Evidence coverage |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 | 0 | 0.000 | 1.000 |

Only scenarios with detector findings are submitted to the advisor. Acceptance means schema and
citation validation passed; it does not establish that a security finding is malicious.

## Interpretation boundary

The scores establish only whether the transparent rules behave as specified on the committed lab fixtures.
The benign updater scenario intentionally tests a plausible false positive. External validation requires
independently labeled traffic, repeated runs and a pre-registered analysis protocol.
