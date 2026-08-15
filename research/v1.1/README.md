# V1.1 research evidence

This directory is reserved for the V1.1 article revision. It must contain only
new manifests, environment records, frozen configurations and preserved
results. Nothing under `research/v2/results/` may be overwritten or relabeled
as new V1.1 evidence.

Current state: environment and protocols are recorded; retrospective and
prospective CTU-13 detector results, a second-dataset implementation-transfer
replay, the primary/ablation/adversarial LLM matrices, and the 31-event
conflicting-context supplement are preserved. A blinded 36-item reviewer
package is generated, but no human ratings have been collected. The previously
inspected V1.0 holdout is used only for error and window-sensitivity diagnosis.

Preserved evidence:

- `results/ctu13-retrospective-window-analysis-2026-08-15/` contains the exact
  JSON and Markdown outputs plus a provenance manifest. The manifest binds the
  artifacts to the input hashes, scientific source-file hashes, and repository
  base commit. The machine inventory is recorded separately in
  `environment-development-2026-08-15.json`; it is not embedded in that
  evidence package.
- `results/ctu13-confirmatory-development-2026-08-15/` preserves all 243 RBot
  candidate results and the development-only selected configuration; it
  records that the holdout was not accessed.
- `results/ctu13-confirmatory-holdout-2026-08-15/` preserves the single DonBot
  run tied to the development artifact and identical scientific source hashes.
- `results/second-dataset-transfer-2026-08-15/` preserves the aggregate replay,
  deterministic examples and provenance for Scenario 1 of the synthetic,
  CTU-13-derived Botnet Group Activity Dataset. It is implementation-transfer
  evidence, not independent external validation.
- `results/endpoint-beh004-2026-08-15/` preserves the five-case inert endpoint
  truth matrix and with/without-Nmap ablation. It validates rule logic, not
  endpoint accuracy.
- `results/counterfactual-policies-2026-08-15/` replays seven response-policy
  definitions offline. Approval- and confirmation-gated policies execute zero
  actions because those decisions are absent from the datasets.
- `results/llm-primary-matrix-2026-08-15/` preserves 180 attempted calls across
  three models and three prompts, including 35 Qwen availability failures.
- `results/llm-ablation-matrix-2026-08-15/` preserves 36 new single-model
  component-ablation calls plus explicitly labeled response reuse.
- `results/llm-adversarial-matrix-2026-08-15/` preserves 45 adversarial calls,
  the protocol amendment and a corrected eligible-denominator audit.
- `results/llm-supplement-matrix-2026-08-15/` preserves nine calls over one
  31-event, four-finding conflicting-context stress case and its post-hoc
  ranking audit.
- The two `llm-availability-recovery*` packages and the single-item endpoint
  recovery preserve availability attempts used only to populate otherwise
  empty blinded-review display items. They do not change primary metrics.
- `human-evaluation/` contains the blank blinded package, concealed mapping,
  reviewer instructions and no completed rating data.
- `verification/` contains the frozen V1.0 baseline record and the final V1.1
  deterministic full/external reproduction logs. These runs made no LLM calls.

Frozen prospective records:

- `ctu13-confirmatory-selection-2026-08-15-corrected.json` assigns Scenario 11/RBot to
  development and Scenario 6/DonBot to the only new CTU-13 holdout before any
  selected flow file was downloaded or parsed. The original record and hash
  are retained, and `CTU13_SELECTION_ERRATUM.md` discloses its timestamp typo.

The requirement and release gates are tracked in
[`docs/V1_1_RESEARCH_PLAN.md`](../../docs/V1_1_RESEARCH_PLAN.md).
The complete automated Phase 4 summary and its remaining human-review gate are
recorded in [`docs/V1_1_PHASE4_SUMMARY.md`](../../docs/V1_1_PHASE4_SUMMARY.md).
The original request-to-evidence audit is
[`docs/V1_1_COMPLETION_AUDIT.md`](../../docs/V1_1_COMPLETION_AUDIT.md).
