# BEH-004 endpoint truth matrix

| Scenario | Expected | Predicted | Outcome |
|---|---:|---:|---|
| same-process-within-window | true | true | true_positive |
| received-bytes-below-threshold | false | false | true_negative |
| different-processes | false | false | true_negative |
| file-after-time-window | false | false | true_negative |
| non-executable-like-suffix | false | false | true_negative |

Constructed inert fixtures validate rule logic and evidence lineage, not endpoint detection accuracy.
