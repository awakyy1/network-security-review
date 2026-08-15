# V1.1 conflicting-context supplement execution note

The fixture contains 31 unique inert events and deterministically produces one
finding for each of BEH-001, BEH-002, BEH-003 and BEH-004. Signed
maintenance-like process context accompanies the first three, while BEH-004
lacks signer and parent-process context. Neither cue is treated as proof of
benignity, maliciousness or authorization.

A pre-inference size check compared the 25,397 combined prompt/system
characters with the observed Qwen tokenization ratio of the prior 17-event
case. The projected input was about 9,849 tokens, so the common context was
increased from 8,192 to 16,384 before any supplemental output existed. Observed
prompt token counts were 8,249 (Llama), 9,906 (Gemma) and 9,123 (Qwen). Every
input plus its 900-token output reservation fit the context.

All nine calls received API responses. Four were valid JSON/schema outputs and
none passed the full validator. Five reached the 900-token output cap. The
Llama ordering and priority vector were identical in three complete schema-valid
outputs, but all three selected rule-inapplicable controls and were rejected.
The result is descriptive stress evidence, not an update to the 180-call
primary matrix and not evidence of semantic correctness.

The matrix summary SHA-256 is
`3013a838cb518a12fb43544e46e4bd62871aa15da9b8076fbf7115a2bc418493`.
The post-hoc denominator/ranking audit is
`supplemental-audit.json`. No automatic action was executed.
