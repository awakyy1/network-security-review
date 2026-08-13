# Phase-C automated repeated comparison

Analysis date: 2026-08-13 (America/Sao_Paulo)

## Evidence sets

- grounded protocol: `grounded-3b-10/`, ten repetitions, 50 calls;
- reconstructed historical protocol: `historical-3b-10/`, ten repetitions,
  50 calls;
- model tag in both sets: `llama3.2:3b`;
- Phase-A manifest and five finding-producing scenarios were unchanged;
- all historical raw artifacts match their preservation SHA-256 values;
- the grounded source-state snapshot is retrospective; the historical snapshot
  is exact. This provenance difference must remain visible.

## Primary automated results

| Protocol | API responses | JSON parse | Grounded schema | Exact finding coverage | Exact evidence coverage | Semantic acceptance |
|---|---:|---:|---:|---:|---:|---:|
| Grounded | 50/50 | 50/50 | 50/50 | 50/50 | 50/50 | 40/50 |
| Historical free text | 50/50 | 0/50 | 0/50 | 0/50 | 0/50 | 0/50 |

The historical protocol was not instructed to emit JSON, so its zero schema
rate is a representation difference rather than a standalone quality failure.
Its zero exact finding- and evidence-ID coverage is the relevant traceability
result because both protocols received the same identifiers and observations.

Every grounded rejection occurred on `emulated-beacon`. In all ten cases, the
response cited the complete supplied finding and evidence but selected
`segment-source-host-after-approval`, a control outside the frozen set
applicable to `BEH-001`. The deterministic validator rejected all ten. Thus the
end-to-end acceptance rate was 0.800 even though API, JSON, schema and citation
coverage rates were 1.000. This demonstrates enforcement around a repeatable
model error; it does not make the erroneous generations correct.

## Historical free-text audit

The frozen audit schema 1.2 found:

- unsupported security-attribution vocabulary in 43/50 responses (58 distinct
  matched terms across those responses);
- containment vocabulary in 10/50 responses;
- containment without an explicit human-approval qualifier in 10/50 responses;
- violation of the 200-word instruction in 37/50 responses;
- Markdown markers despite the no-Markdown instruction in 50/50 responses;
- median response length 219.5 words (range 151--295).

The scenario distribution was not uniform. Unsupported attribution appeared in
9/10 benign-updater responses and 10/10 tool-transfer responses. Unqualified
containment appeared in 5/10 service-discovery, 4/10 tool-transfer and 1/10
asymmetric-egress responses.

The broad lexical attribution count is reported for the historical audit only.
The repeated-run aggregator did not apply the same free-text extraction to the
grounded JSON fields. A later exploratory application to selected grounded
text fields cannot be promoted to a confirmatory symmetric metric without
documenting that new extraction rule. The defensible primary comparison is
therefore exact traceability and deterministic policy acceptance.

## Stability and latency

All 50 historical raw responses were unique within their scenario groups,
consistent with temperature 0.7. The grounded outputs used temperature zero
and seed 42: three scenario groups had one unique response, while benign updater
and service discovery each had one first-run variant followed by nine identical
responses. Repetition here measures observed stability; the 50 calls are
clustered across five fixed prompts and must not be treated as 50 independent
samples.

Grounded median latency was 31.636 seconds and historical median latency was
95.936 seconds. A causal speed comparison is not justified: the sets were run
at different times and operating-system states, and the Ollama versions differed
(0.32.5 versus 0.32.6). Latency remains descriptive environment evidence.

## Interpretation for RQ2 and H2

Within this fixed model, evidence pack and automated operational definition,
the repeated results support the traceability part of H2: the grounded protocol
preserved exact IDs and the free-text reconstruction did not. They also show
that schema constraint alone was insufficient, because 20% of grounded calls
still required semantic policy rejection.

The results do not establish general model correctness, malware-detection
accuracy or analyst usefulness. The unsupported-claim comparison is not fully
symmetric, ranking stability is not estimable with one finding per scenario,
and blinded human ratings remain absent. RQ2 can be answered for automated
traceability and enforcement in this artifact; broader semantic superiority
remains open.

No inferential p-value is reported. Fixed repeated prompts, deterministic
grounded parameters and scenario clustering violate a simple independent-trials
interpretation; descriptive counts preserve the actual design more honestly.
