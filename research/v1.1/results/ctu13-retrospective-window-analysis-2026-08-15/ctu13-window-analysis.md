# V1.1 retrospective CTU-13 detector diagnostics

> The V1.0 holdout has already been inspected. Window and feature analyses are diagnostic and cannot turn it back into an untouched holdout.

## Window-size metrics

| Role | Family | Window (s) | Units | TP | FP | FN | TN | F1 | Specificity | MCC |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| development | Virut | 60 | 101 | 18 | 34 | 3 | 46 | 0.493 | 0.575 | 0.351 |
| development | Virut | 300 | 31 | 5 | 17 | 0 | 9 | 0.370 | 0.346 | 0.280 |
| development | Virut | 600 | 19 | 3 | 10 | 0 | 6 | 0.375 | 0.375 | 0.294 |
| holdout | NSIS.ay | 60 | 247 | 31 | 53 | 71 | 92 | 0.333 | 0.634 | -0.064 |
| holdout | NSIS.ay | 300 | 108 | 16 | 32 | 37 | 23 | 0.317 | 0.418 | -0.282 |
| holdout | NSIS.ay | 600 | 73 | 13 | 18 | 29 | 13 | 0.356 | 0.419 | -0.271 |

## Five-minute rule diagnostics

| Role | Truth | BEH-001 <6 | No eligible mean | CV >0.15 | BEH-001 match | BEH-003 >=1 MB | Ratio >=10 | Both |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| development | botnet-origin | 0 | 1 | 3 | 1 | 0 | 5 | 0 |
| development | normal-origin | 7 | 6 | 6 | 7 | 0 | 3 | 0 |
| holdout | botnet-origin | 50 | 0 | 3 | 0 | 0 | 28 | 0 |
| holdout | normal-origin | 18 | 16 | 6 | 15 | 0 | 6 | 0 |

BEH-003 is diagnosed component by component; absence of a rule match is not treated as proof that
the underlying behavior was absent. The adapter exposes source and reverse byte counts per flow,
but NetFlow contains no process or file lineage.
