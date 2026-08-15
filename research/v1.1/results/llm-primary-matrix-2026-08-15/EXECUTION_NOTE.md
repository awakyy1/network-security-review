# Primary LLM matrix execution note

Execution date: 2026-08-15  
Frozen expected calls: 180  
Observed attempted calls in the aggregate: 180  
Automatic actions executed: 0

The Llama 3.2 3B and Gemma 3 4B cells received API responses for all 120 attempted calls. Qwen 3 8B received responses for all 20 `contract-v1` calls and for the first five `evidence-first-v1` calls. The next Qwen request ended with a connection reset; the remaining 34 attempts recorded loopback connection-refused errors because the Ollama server was no longer running. Thus, 35 of 60 Qwen attempts have no model response.

The cause of the local Ollama server exit was not established from a preserved primary-run server log. It must not be described as a model-quality failure, a timeout, or an out-of-memory event without additional evidence. It is reported as an end-to-end availability failure of this exact local execution. The frozen runner preserved all per-call errors, counted failed attempts in the planned denominator, and did not retry or replace them. The Qwen `evidence-first-v1` and `checklist-v1` cells therefore cannot support a clean output-quality comparison with cells that received all responses.

The `unsupported_claim_rate` field is produced by the frozen lexical/structural audit. It flags any attribution term such as “malware,” including a negated limitation such as “malware is not confirmed,” and can flag containment vocabulary unless an approval phrase matches the fixed pattern. It is therefore a conservative lexical safety-flag rate, not a human-adjudicated rate of semantically unsupported claims. The raw flags remain unchanged; manuscript prose must not present them as expert-confirmed semantic errors.

Balanced blinded human evaluation cannot be prepared for all nine cells because one cell contains no Qwen response and another is incomplete. The package generator correctly refuses to substitute `null` or another model's output. Any human study must use a newly declared sampling plan and real reviewers.
