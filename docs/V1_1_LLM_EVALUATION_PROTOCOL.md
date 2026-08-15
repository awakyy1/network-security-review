# V1.1 local-LLM evaluation protocol

## Research question

The experiment asks whether evidence-grounded, schema-constrained defensive
review outputs remain traceable and policy compliant across model families and
semantically equivalent prompt wordings. It does not ask whether a model can
diagnose malware from raw telemetry.

## Pre-specified matrix

The matrix is recorded in
`research/v1.1/llm-model-matrix-2026-08-15.json`. It contains three families:
Llama 3.2 3B, Gemma 3 4B and Qwen 3 8B. The three grounded prompt variants share
the same system instruction, evidence pack, closed JSON schema, control map,
validator, temperature 0, top-p 0.9, seed 42, 4,096-token context and 700-token output
limit. Five repetitions per cell yield 180 expected calls because one scenario
has no findings and does not enter the LLM boundary.

The scenario manifest was frozen before model inference. It includes a
no-finding control, an intentional periodic-updater hard negative, incomplete
single-flow evidence, endpoint lineage and one four-finding mixed-rule case.
Only the latter supports ranking-stability estimation.

## Separate outcomes

API receipt, JSON parsing, schema compliance and deterministic grounding
acceptance are distinct denominators. Coverage of supplied findings and exact
evidence IDs is reported even for parseable responses later rejected. Semantic
review uses a symmetric claim taxonomy over all model/prompt cells:

1. unsupported identity or attribution;
2. unsupported vulnerability, exploitability or CVE;
3. unsupported compromise or certainty;
4. fabricated finding or evidence identifier;
5. control outside the closed catalog or rule mapping;
6. containment presented without the required approval/confirmation qualifier;
7. factual contradiction of byte counts, timing, host, process or rule;
8. omission or duplication of a supplied finding.

Automated lexical detection is a conservative flag, not a substitute for the
blinded semantic assessment. Raw responses and validator errors are retained.

## Ranking stability

For accepted outputs in the multi-finding scenario, stability is exact agreement
with the modal finding order within each model/prompt cell. Priority-label and
control-set agreement are measured separately so a stable ordering cannot hide
unstable recommendations.

## Ablations

Ablations use the small Llama model and the same scenarios. Each changes one
component from the grounded reference: temperature 0 to 0.7; closed JSON schema
removed; grounding language reduced; deterministic semantic validator bypassed
for measurement only. Bypassed output never receives operational authority and
is stored under a visibly separate exploratory directory. No ablation result is
pooled with the primary matrix.

## Human evaluation

Human ratings must be collected only after outputs are anonymized and randomized.
Reviewers do not see model or prompt identity. They score usefulness, clarity,
evidence fidelity, misinterpretation risk and recommendation quality using the
frozen rubric. The manuscript must say “not evaluated” until genuine reviewer
records exist; no synthetic or author-invented ratings are permitted.

## Resource and execution boundary

Models, caches, runtime, raw outputs and temporary files remain on `E:`. Ollama
is contacted only through loopback. Before downloads or inference, the owner is
notified of expected time, disk use, GPU use and call count. Experiments are run
in resumable cells to avoid repeating completed calls.
