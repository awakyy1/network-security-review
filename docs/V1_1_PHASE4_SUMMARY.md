# V1.1 Phase 4 summary

## Status

The automated protocol work is complete. Eight of the nine originally proposed
Phase 4 experiments have preserved exit evidence. Independent blinded ratings
were not feasible in this solo revision and are explicitly recorded as not
achieved; no rating was fabricated or inferred. Analyst usefulness and semantic
correctness therefore remain outside the demonstrated claims.

## Primary model and prompt matrix

- Three locally installed model families were evaluated: `llama3.2:3b`,
  `gemma3:4b`, and `qwen3:8b`.
- Three prompt protocols, four scenario classes, and five clustered repetitions
  produced 180 planned attempts.
- The endpoint returned 145 responses; 122 were valid JSON matching the schema,
  and 73 passed the deterministic semantic-policy validator.
- The accepted denominators remain 73/180 planned attempts and 73/145 received
  responses. Representation, grounding, and policy acceptance are reported
  separately.
- All 45 primary multi-finding attempts were rejected or unavailable. A post-hoc
  audit found four estimable schema-valid ranking cells; ordering repeated within
  each cell, but every ordering was incomplete or policy-invalid. Repeatability
  was therefore not treated as correctness.

## Availability failure and declared recovery

- The primary run retained one connection reset and 34 subsequent refused Qwen
  calls after the local server exited. They were not silently retried or replaced.
- A separately labeled four-call recovery first returned four HTTP 500 responses.
  Contemporaneous diagnostics identified two orphaned Ollama child processes and
  a CUDA allocation failure for this recovery run; that cause was not
  retroactively assigned to the primary run because its server log was absent.
- After only the verified orphaned processes were terminated, the declared retry
  returned 4/4 bodies; one passed validation.
- A separate one-call endpoint recovery supplied the fifth missing display body
  for the human package. It was schema-valid but rejected for an unsupported
  absolute claim.
- None of these five recovery outputs changed the primary denominators.

## Supplemental, ablation, and adversarial evidence

- A frozen 31-event stress case covered all four rules, mixed findings, opposing
  contextual cues, and dozens of unique evidence events. Context was raised from
  8,192 to 16,384 tokens before inference after deterministic prompt sizing.
- All 9 supplemental calls returned responses; 4 were JSON/schema-valid, 0 were
  accepted, and 5 reached the 900-token output cap. Llama produced three complete,
  exactly repeated rankings, but all selected rule-inapplicable controls.
- The component ablation separated temperature, API format constraint, grounding
  language, and validator enforcement. Removing the API format constraint yielded
  0/12 valid JSON responses; bypassing the validator would have admitted malformed
  or policy-invalid output.
- The inert adversarial matrix attempted 45 calls. Twenty returned HTTP 500;
  11/21 pairs had both responses, and validator status changed in 8/11. Among ten
  parseable pairs, priority changed in two, controls in four, finding order in one,
  and the cited evidence set in none. These are descriptive paired observations,
  not an attack-success probability.
- No model had credentials or an execution path, and no automatic action occurred.

## Human-evaluation package

- A concealed 36-item package, identity map, rubric, and reviewer instructions
  were generated from frozen first-repetition outputs.
- Five objectively selected availability substitutions are disclosed in a frozen
  recovery map and are excluded from primary metric replacement.
- The analyzer requires at least two complete, genuinely rated packages and
  computes medians, interquartile ranges, and pairwise weighted Cohen kappa. It
  refuses missing ratings, duplicate pseudonyms, mismatched items, or invalid
  values.
- Reviewer identities, free-text notes, and the concealed model/prompt mapping are
  excluded from the intended public aggregate.

## Integrity boundary

Exact model digests, parameters, prompt/schema versions, fixture hashes, raw
responses, errors, execution notes, and machine-readable aggregates are preserved
under `research/v1.1/`. Availability recovery and post-hoc audits are labeled as
such. The historical V1.0 comparison remains separate, and no result was promoted
to semantic correctness without independent human evidence.
