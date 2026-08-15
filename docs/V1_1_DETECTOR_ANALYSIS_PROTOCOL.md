# V1.1 detector-analysis protocol

## Purpose

This protocol defines the diagnostic analysis performed on the already
inspected V1.0 CTU-13 sources and the separation required for a future V1.1
confirmatory holdout. Its purpose is to explain the V1.0 error pattern and
prepare a defensible next experiment, not to relabel the historical holdout as
untouched evidence.

Protocol frozen for implementation: 2026-08-15 (America/Sao_Paulo).

## Evidence roles

- Scenario 5/Virut: historical development evidence.
- Scenario 12/NSIS.ay: historical V1.0 holdout, now available only for
  transparent retrospective diagnostics.
- Any threshold, window, feature or interpretation learned from either source
  is development information for V1.1.
- A V1.1 confirmatory result requires a separately frozen family or dataset
  whose scored labels are not inspected before the configuration is frozen.

## Fixed diagnostic questions

1. How do non-overlapping source-host windows of 60, 300 and 600 seconds change
   the number of scored units and the fixed-rule confusion matrix?
2. How much do the botnet-origin and normal-origin distributions of maximum
   distinct endpoints in a 60-second interval overlap?
3. For BEH-001, do units fail because they have fewer than six connections to
   one endpoint, because the mean interval is outside 5--900 seconds, or
   because the minimum coefficient of variation exceeds 0.15?
4. For BEH-003, how many units contain a flow meeting the 1,000,000-byte sent
   threshold, the 10:1 sent/received threshold, or both thresholds?
5. What preserved unit, finding and evidence identifiers illustrate one true
   positive, one false positive and one false negative under each condition?

The diagnostic implementation must not change detector thresholds. Feature
values are extracted independently so threshold investigations remain visible
instead of silently altering the classifier.

## Outputs

`src.ctu13_analysis` produces one machine-readable result containing, for each
source and window size:

- confusion matrix and derived metrics;
- parse and exclusion counts;
- distribution summaries for BEH-001/002/003-relevant features;
- counts showing which BEH-003 threshold component was or was not present;
- deterministic TP, FP and FN examples with anonymized hosts, finding IDs and
  evidence IDs;
- anonymized per-unit diagnostic records for generated plots and later audit.

Raw `.binetflow` data and transient output remain ignored under `E:\tcc\data`
and `E:\tcc\output`. Preserved V1.1 evidence is promoted only after hashes,
source state and interpretation labels are recorded. No file from V1.0 is
overwritten.

## Execution and comparison boundary

The historical 60/300/600-second analysis is exploratory/diagnostic even
though the detector rules themselves remain unchanged. It may explain the
published V1.0 negative result but cannot be used as an independent
confirmatory estimate after it influences V1.1 decisions.

Threshold selection, if undertaken, must use designated V1.1 development
families only. The selected threshold vector, window size, code revision,
dataset hashes and analysis plan must be frozen before the new holdout run.
The new holdout is executed once for the primary report; failures and negative
results are retained.
