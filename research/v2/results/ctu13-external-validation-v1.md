# CTU-13 external flow validation

> Only labeled bidirectional text flows are processed. No malware, executable or packet capture is acquired.

| Role | Scenario | Family | Units | TP | FP | FN | TN | Precision | Recall | F1 | Specificity | MCC |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| development | 5 | Virut | 31 | 5 | 17 | 0 | 9 | 0.227 | 1.000 | 0.370 | 0.346 | 0.280 |
| holdout | 12 | NSIS.ay | 108 | 16 | 32 | 37 | 23 | 0.333 | 0.302 | 0.317 | 0.418 | -0.282 |

`Background` and `To-*` flows are excluded from binary scoring. A positive unit contains only
traffic labeled `From-Botnet`; a negative unit contains only traffic labeled `From-Normal`.
The labels are never supplied to the detector. BEH-004 is not evaluated because NetFlow lacks
endpoint file-creation evidence. Development and holdout metrics must remain separate.

No automatic action is executed. If every alert had instead caused a block, the observed false
positive share would also be the unnecessary-action rate; this counterfactual is reported in JSON
to show why human confirmation and endpoint context are required.
