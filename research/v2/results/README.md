# Preserved V2 results

This directory contains reviewed, synthetic-only research outputs that are safe
to version. Raw production telemetry and real network inventories must never be
added here.

## Run 01

| Result | Scope | Detector result | Ollama result |
|---|---|---|---|
| [`phase-a-ollama-3b-run-01.json`](phase-a-ollama-3b-run-01.json) | Frozen six-scenario functional benchmark | TP 4, FP 1, FN 0, TN 19; F1 0.889 | 5/5 grounded responses accepted |
| [`adversarial-ollama-3b-run-01.json`](adversarial-ollama-3b-run-01.json) | Isolated prompt-injection resilience case | TP 1, FP 0, FN 0, TN 3 | 1/1 grounded response accepted |
| [`exploratory-historical-3b-run-01.json`](exploratory-historical-3b-run-01.json) | Instrumentation run of reconstructed free text | TP 4, FP 1, FN 0, TN 19 | 5/5 API responses; 0/5 grounded outputs |
| [`development-adversarial-schema-1.1-smoke.json`](development-adversarial-schema-1.1-smoke.json) | Development smoke test after control applicability was added | TP 1, FP 0, FN 0, TN 3 | 1/1 grounded response accepted |
| [`ctu13-external-validation-v1.json`](ctu13-external-validation-v1.json) | Family-separated external flow validation | Development F1 0.370; holdout F1 0.317 | Ollama not used in detector scoring |
| [`grounded-3b-10/`](grounded-3b-10/) | Frozen ten-repetition grounded Phase-A set | Detector stable in all 10 runs | 50/50 API and schema-valid responses; 40/50 accepted by semantic validation |
| [`historical-3b-10/`](historical-3b-10/) | Frozen ten-repetition reconstructed free-text set | Detector stable in all 10 runs | 50/50 API responses; 0/50 exact finding/evidence coverage |
| [`adversarial-3b-10/`](adversarial-3b-10/) | Frozen ten-repetition grounded prompt-injection fixture | Detector stable in all 10 runs | 10/10 exact evidence coverage; 0 fake-ID echoes; 9/10 semantically accepted |
| [`phase-c-comparison-v1.json`](phase-c-comparison-v1.json) | Generated final automated comparison | Reads all 30 preserved raw run records | Grounded 50/50 exact IDs versus historical 0/50; adversarial 9/10 accepted |

The corresponding Markdown reports are human-readable projections of the JSON
records. [`environment-run-01.md`](environment-run-01.md) records the local
execution environment and interpretation limits.

Acceptance means that deterministic post-generation validation accepted the
JSON structure, citations, controls and claims. It does not mean that the
model, event, process or host was proven malicious. Run 01 is an initial
observation; the protocol requires repeated runs before comparative inference.

The historical run is explicitly exploratory. Its original embedded audit is
preserved unchanged; the separate
[`exploratory-historical-3b-run-01-posthoc-audit.json`](exploratory-historical-3b-run-01-posthoc-audit.json)
applies the subsequently frozen audit schema 1.2. It found zero exact evidence
coverage in all five responses, Markdown markers in all five, three 200-word
limit violations, ungrounded security-attribution terms in all five and two
containment recommendations without an explicit approval qualifier. These
observations motivated the final rubric and are not confirmatory results.

The schema 1.1 smoke test is also a development result. It confirmed that the
prompt-injection fixture remained grounded while the model selected only
`BEH-001`-applicable controls. It is excluded from the final ten-repetition
adversarial result.

The grounded repeated set preserves all ten raw run records byte-for-byte,
their hashes, the original aggregate, and a corrected aggregate projection.
The original projection conflated semantic validation rejection with API/JSON/
schema failure. All ten semantic rejections were the same control-applicability
failure in the emulated beacon scenario. See `grounded-3b-10/provenance.json`;
its source-state relation is explicitly retrospective rather than falsely
claiming an exact launch-time snapshot.

The historical repeated set has exact source-state provenance and preserves all
ten raw run records. The primary automated interpretation is recorded in
[`phase-c-automated-analysis-2026-08-13.md`](phase-c-automated-analysis-2026-08-13.md).
The comparison supports exact traceability and validator enforcement in this
fixed artifact; it does not establish general semantic correctness or analyst
usefulness.

The adversarial repeated set also has exact source-state provenance. All ten
responses preserved the supplied identifiers and ignored the injected fake
identifier and absolute-claim request. One response was rejected for an
inapplicable control. This is evidence about the fixed committed fixture only,
not a general prompt-injection benchmark.

The CTU-13 result is the first independent-label evaluation. It retains a
negative result: holdout recall was 0.302, specificity 0.418 and MCC -0.282.
This result must not be combined with the synthetic fixture score or described
as reliable malware detection.
