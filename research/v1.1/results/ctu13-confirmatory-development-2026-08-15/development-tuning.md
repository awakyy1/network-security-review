# V1.1 CTU-13 development-only threshold selection

> The confirmatory holdout was not accessed by this command.

Candidates: 243
Selected candidate: 97
Units: 18
TP/FP/FN/TN: 0/2/3/13
F1: 0.000
Specificity: 0.867
MCC: -0.158

## Selected thresholds

```json
{
  "beh_001_minimum_connections": 6,
  "beh_001_minimum_mean_interval_seconds": 5,
  "beh_001_maximum_mean_interval_seconds": 900,
  "beh_001_maximum_interval_cv": 0.15,
  "beh_002_minimum_distinct_endpoints": 16,
  "beh_002_interval_seconds": 60,
  "beh_003_minimum_bytes_sent": 1000000,
  "beh_003_minimum_sent_received_ratio": 10,
  "beh_004_minimum_bytes_received": 32768,
  "beh_004_maximum_delay_seconds": 120
}
```
