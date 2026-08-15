# V1.1 preserved results

Each child directory is an immutable evidence package. A package must contain
the generated artifacts and a provenance manifest with hashes for the inputs,
scientific source state, and outputs. Existing machine-generated artifacts must
never be edited or overwritten; a changed protocol or implementation requires a
new directory. A clearly labeled audit note or erratum may be appended while the
original artifact and its hash remain unchanged.

## Current packages

- `ctu13-retrospective-window-analysis-2026-08-15/`: diagnostic reuse of the
  already inspected V1.0 development and holdout sources. It compares fixed
  60, 300, and 600 second windows, decomposes BEH-001 through BEH-003 threshold
  behavior, and preserves deterministic TP, FP, and FN examples. It is not
  confirmatory evidence and does not make the holdout untouched again.
- `ctu13-confirmatory-development-2026-08-15/`: development-only evaluation
  of the frozen 243-member threshold grid on RBot, including every candidate,
  the selected configuration and anonymized selected-unit evidence.
- `ctu13-confirmatory-holdout-2026-08-15/`: the single source-state-gated
  DonBot holdout run. Its JSON links the exact development artifact, selection
  record, acquisition record, thresholds and code hashes.
- `second-dataset-transfer-2026-08-15/`: the Scenario-1 aggregate,
  deterministic examples and source/code/output hashes for the synthetic
  Botnet Group Activity implementation-transfer replay.
- `endpoint-beh004-2026-08-15/`: the five-case inert BEH-004 truth matrix and
  Nmap inventory ablation, with source/code/output provenance.
- `counterfactual-policies-2026-08-15/`: offline policy counts for alert-block,
  two-rule block, approval, evidence collection, rate limiting, monitoring and
  confirmation-gated isolation; no operational action was executed.
- `llm-primary-matrix-2026-08-15/`: 180 primary attempts across three local
  model families and three prompt variants, with raw responses and failures.
- `llm-ablation-matrix-2026-08-15/`: temperature, API-format and grounding-
  language ablations plus labeled reference reuse and validator bypass.
- `llm-adversarial-matrix-2026-08-15/`: inert paired prompt-injection cases and
  the corrected audit that excludes unavailable pairs from change metrics.
- `llm-supplement-matrix-2026-08-15/`: nine responses to a 31-event,
  four-finding conflicting-context stress case. Four were schema-valid and
  none passed the complete validator. `SUMMARY_ERRATUM.md` identifies one
  inapplicable generic ranking-explanation field without changing the preserved
  summary; `supplemental-audit.json` is authoritative for ranking eligibility.
- `llm-availability-recovery-2026-08-15/` and
  `llm-availability-recovery-retry1-2026-08-15/`: the preserved failed and
  successful four-item availability attempts for blinded-package display.
- `llm-human-recovery-endpoint-2026-08-15/`: one frozen recovery of a primary
  response with an empty body; its schema-valid output remained rejected.
