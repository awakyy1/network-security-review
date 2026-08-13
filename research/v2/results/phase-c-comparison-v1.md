# Final automated Phase-C comparison

| Protocol | Calls | API | Exact findings | Exact evidence | System accepted |
|---|---:|---:|---:|---:|---:|
| Grounded | 50 | 50 | 50 | 50 | 40 |
| Historical free text | 50 | 50 | 0 | 0 | 0 |

Historical protocol-specific audit:

- security-attribution responses: 43/50;
- unqualified containment responses: 10/50;
- 200-word-limit violations: 37/50;
- Markdown violations: 50/50.

Adversarial grounded set:

- accepted: 9/10;
- exact evidence coverage: 10/10;
- fake-ID echoes: 0/10;
- absolute-assertion responses: 0/10;
- policy rejections: 1/10.

> The comparison measures exact traceability, instruction adherence, and deterministic policy enforcement in fixed prompts. It does not establish general semantic correctness, malware-detection accuracy, or analyst usefulness.
