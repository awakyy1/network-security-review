# Supplemental matrix summary interpretation erratum

The preserved `matrix-summary.json` contains the generic per-cell field
`ollama.ranking_interpretation` with the sentence “Not estimable when each
scenario yields at most one finding.” That explanation is not applicable to
this supplemental manifest: its single scenario deterministically produces
four findings.

The field was emitted by the original matrix aggregator because no
policy-accepted multi-finding response was available to its legacy ranking
calculation. It does not alter any attempt, response, JSON/schema, acceptance,
coverage, or raw-output value. The original summary remains unchanged.

For the supplemental ranking analysis, the authoritative artifact is
`supplemental-audit.json`. It evaluates schema-valid raw responses even when
the policy validator rejected them and reports that only the three
Llama/evidence-first outputs contained every exact finding identifier once;
their ordering and priority vector repeated exactly, but all three selected
rule-inapplicable controls and therefore remained rejected. Gemma and Qwen had
no complete known-identifier ranking eligible for agreement estimation.

