# V2 research protocol: grounded LLM analysis and safe malware-behavior emulation

## Status and document boundary

This protocol governs the post-defense V2 article and software experiments. It
does not amend the approved monograph. Results must be reported only after the
corresponding raw inputs, code state, parameters and outputs have been
preserved.

## Research objective

Evaluate whether a hybrid defensive pipeline can correlate authorized Nmap
inventory with endpoint/network telemetry, identify reviewable behavior
patterns associated with malware operations, and use a local language model to
prioritize those findings without escalating them into unsupported claims.

The study evaluates **behavioral review**, not malware-family attribution,
exploitability, compromise confirmation or autonomous response.

## Research questions and hypotheses

### RQ1 — behavioral review

To what extent do transparent temporal and flow rules identify the behavior
classes specified in a controlled benign laboratory while avoiding alerts on
benign activity?

- **H1:** all four positive emulations will be identified by their predeclared
  rule, but periodic legitimate software will expose a measurable false-positive
  limitation in simple beaconing heuristics.
- **Null H1:** the rules will not distinguish the specified emulations from the
  committed benign scenarios better than the predeclared scenario labels.

### RQ2 — grounded local inference

Can a local Ollama model produce schema-valid prioritization whose claims cite
only supplied findings and event IDs, including when evidence fields contain
prompt-like untrusted text?

- **H2:** schema constraint, temperature zero, evidence-ID validation and a
  fixed control catalog will yield a higher accepted-grounding rate than the
  reconstructed 2025 free-text protocol.
- **Null H2:** the grounded protocol will not improve accepted-grounding rate or
  unsupported-claim rate relative to the historical protocol.

### RQ3 — practical contribution

Which defensive actions can the system responsibly support before a human has
confirmed malicious activity?

- **H3:** the artifact can reproducibly propose evidence collection and scoped
  containment candidates, but the available observations cannot justify direct
  blocking or malware attribution.

## Evidence model

The pipeline preserves five distinct states:

1. Nmap observation: host, service, port and fingerprint;
2. endpoint/network event: connection, DNS query or file creation;
3. transparent behavior-rule match;
4. LLM prioritization citing states 1–3;
5. independent analyst conclusion and any authorized response.

No earlier state may be represented as a later one. Every V2 behavior finding
therefore includes:

```text
classification = behavior-review
confirmed_malware = false
confirmed_vulnerability = false
automatic_response_authorized = false
```

## Behavior classes

| Rule | Observable pattern | ATT&CK context | Primary limitation |
|---|---|---|---|
| `BEH-001` | at least six near-periodic connections to one endpoint | T1071, Application Layer Protocol | legitimate polling can be periodic |
| `BEH-002` | at least eight distinct endpoints in 60 seconds | T1046, Network Service Discovery | authorized administration/scanning can match |
| `BEH-003` | at least 1 MB sent with a sent/received ratio of at least 10:1 | T1041, Exfiltration Over C2 Channel | backups and uploads can be legitimate |
| `BEH-004` | at least 32 KiB received followed by executable-like file metadata within 120 seconds | T1105, Ingress Tool Transfer | normal installers and package managers can match |

ATT&CK documents application-layer protocols as a way for command traffic to
blend with ordinary traffic, rapid service probing as a discovery behavior,
transfer over an existing command channel as an exfiltration behavior, and
network transfer followed by file creation as an ingress-tool-transfer chain:

- [T1071 — Application Layer Protocol](https://attack.mitre.org/techniques/T1071/)
- [T1046 — Network Service Discovery](https://attack.mitre.org/techniques/T1046/)
- [T1041 — Exfiltration Over C2 Channel](https://attack.mitre.org/techniques/T1041/)
- [T1105 — Ingress Tool Transfer](https://attack.mitre.org/techniques/T1105/)

These mappings provide behavioral context, not proof that an ATT&CK technique
or malware family occurred.

## Laboratory design

Phase A uses deterministic inert JSON Lines fixtures under `research/v2/`.
There are no sockets, payloads, persistence mechanisms or operating-system
changes. Positive scenarios emulate timing and byte-count relationships;
negative scenarios include ordinary browsing and a deliberately difficult
periodic updater.

Phase B uses only independently labeled CTU-13 bidirectional text-flow records.
Scenario 5/Virut was frozen as development and scenario 12/NSIS.ay as the
family-separated holdout before complete-label inspection. The exact CC BY
provenance, URLs, byte lengths, ETags and SHA-256 values are frozen in
`research/v2/ctu13_manifest.json`. Acquisition code permits only the two
official `.binetflow` URLs; malware binaries, archives, Argus binary files and
packet captures are explicitly prohibited.

The scored unit is an anonymized source host by non-overlapping five-minute
window. Only `From-Botnet` and `From-Normal` are clean positive and negative
labels. `Background` and all `To-*` traffic are excluded because the publisher
does not define them as reliable binary ground truth. The labels are never
given to the detector.

The Phase-A thresholds are frozen before Phase B. Changes made after inspecting
external labels must be reported as model development and evaluated on a
separate holdout subset.

The frozen baseline has now been evaluated without tuning. Holdout precision
was 0.333, recall 0.302, specificity 0.418, F1 0.317 and MCC -0.282. This
negative result is retained: timing and destination diversity without process
or file context do not support reliable malware-origin detection. See
`docs/CTU13_EXTERNAL_VALIDATION.md` for the full method and uncertainty bounds.

## Metrics

### Deterministic detector

- scenario-rule true positives, false positives, false negatives and true
  negatives;
- precision, recall, F1 and specificity;
- results per behavior class and aggregate results;
- event-processing latency and peak memory in repeated runs;
- false positives described by scenario rather than hidden in an aggregate.

Synthetic fixtures measure functional behavior only. They must not be mixed
with external-validation metrics.

### Ollama protocol

For each model/protocol combination, preserve model tag and digest, Ollama
version, hardware, prompt hash, schema version, generation parameters, raw
response, validated response, token counts and latency. Run at least ten
repetitions per prompt set.

Report:

- API success rate;
- JSON parse rate and schema-valid rate;
- accepted-grounding rate after deterministic validation;
- unknown finding-ID and evidence-ID citation counts;
- unsupported CVE and absolute-compromise assertion counts;
- evidence coverage among prioritized findings;
- median and interquartile latency;
- ranking agreement across repeated runs;
- blinded human ratings for evidence fidelity, correctness, usefulness and
  clarity when reviewers become available.

The grounded protocol uses Ollama structured output with a JSON schema. Ollama's
official documentation states that the `format` field accepts a schema and
recommends including the schema in the prompt as well:
[Structured Outputs](https://docs.ollama.com/capabilities/structured-outputs).

The comparison control is a documented reconstruction of the 2025 technical
free-text path at repository commit `b63c894`. It preserves the historical
temperature 0.7 and `top_p` 0.9 and omits a system prompt and output schema. Its
technical-analysis prompt is adapted to the V2 evidence pack so both protocols
receive the same observations. The former penetration-test prompt is excluded
because it asks a different question and conflicts with the safe defensive
scope. A fixed context, output ceiling and timeout are added and reported for
reproducibility; therefore this is a reconstructed control, not a byte-exact
replay of the defended system.

The final comparison also records exact finding/event-ID coverage, free-text
security-attribution mentions unsupported by the evidence, containment terms
without an explicit human-approval qualifier, Markdown-format violations and
the original 200-word-limit violations. These automated lexical measures do
not replace blinded human review.

An initial single historical run was used only to validate instrumentation and
refine the audit rubric. Because those outputs informed audit version 1.2, that
run is exploratory and excluded from the final repeated comparison.

## Operating-system telemetry path

The normalized event schema can be populated from Windows Sysmon in a future
authorized deployment. Microsoft's documentation identifies Event ID 3 as
process-associated network connections, Event ID 22 as process-associated DNS
queries and Event ID 11 as file creation. Network Connection is disabled by
default due to volume and must be selectively configured:
[Sysmon events](https://learn.microsoft.com/en-us/windows/security/operating-system-security/sysmon/sysmon-events).

Raw production Sysmon data is not committed to the public repository. Field
mapping, consent/scope, retention and anonymization must be approved before any
collection from a real endpoint.

## LLM trust boundary

- only a loopback Ollama endpoint is accepted;
- evidence values are delimited as untrusted data;
- topology is not sent to a cloud model;
- output must match a closed JSON schema;
- cited finding and event IDs must already exist;
- CVEs absent from evidence and absolute compromise claims are rejected;
- proposed controls are selected from a fixed catalog;
- schema version 1.1 requires every supplied finding exactly once and permits
  only controls mapped to that finding's behavior rule;
- the model receives no firewall, Zabbix or operating-system credentials;
- model output cannot invoke a tool or apply a control.

The raw model-failure rate and the post-validator acceptance rate must be
reported separately. A validator that rejects unsafe output improves system
safety but does not prove that the model itself is reliable.

## Response evaluation

The system may recommend collecting more telemetry, validating process
ownership, or preparing a temporary scoped control. Isolation, quarantine,
segmentation or egress restriction require human confirmation, change logging,
an expiration/rollback plan and an independently tested recovery path.

The V2 experiment evaluates whether a recommendation is justified and
traceable. It does not evaluate actual firewall blocking until a separate,
authorized, reversible laboratory protocol is approved.

## Reproducibility checklist

- [ ] committed scenario manifest and immutable input hashes;
- [ ] exact repository commit;
- [ ] Python, dependency and operating-system versions;
- [ ] model tag, digest, Ollama version and hardware description;
- [ ] raw and normalized results kept separately;
- [ ] exploratory runs separated from final frozen-protocol runs;
- [ ] no tuning on the external holdout labels;
- [x] article tables generated from preserved result JSON;
- [x] every figure/table mentioned before it appears and supplied with source;
- [x] monograph hash rechecked and unchanged;
- [ ] limitations and negative results retained in the conclusion.
