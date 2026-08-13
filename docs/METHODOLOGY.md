# Methodology and evidence boundary

This document supports the post-defense refinement of the scientific article and the interpretation of the software artifact. It does not amend the approved monograph, which remains archived unchanged.

## Research design

The study is applied, exploratory and technological. Its artifact is described
through Design Science Research: problem identification, objectives,
design/development, demonstration, evaluation and communication.

The approved 2025 monograph remains a historical source with incomplete raw
experimental evidence. The post-defense V1 article adds a separately frozen
evaluation with three layers that must not be merged:

1. a deterministic functional benchmark on six inert authored scenarios;
2. a family-separated external CTU-13 flow evaluation with development and
   holdout sources;
3. repeated automated assessment of a grounded local-LLM protocol, a
   reconstructed historical free-text control and a separate adversarial
   fixture.

## Units of analysis

1. **Observation:** host, port, protocol and fingerprint present in an Nmap XML document.
2. **Derived review item:** a documented rule matched an observation.
3. **Generated narrative:** contextual text produced by the pre-defense optional LLM path.
4. **Human conclusion:** validation that requires environmental and independent evidence.

The LLM comparison additionally separates API response, JSON parsing, schema
validity, exact finding/evidence traceability, semantic policy validation and
blinded human judgment. A failure or success at one boundary is not counted as
a result at another boundary.

These units must not be collapsed into a single “vulnerability” count.

## Preserved results

The source manuscript reported 24 hosts, 21 open ports, seven rule-scoped items and 352 aggregate seconds across three scenarios. The corrected descriptive ratio is approximately 14.7 seconds per host. It is not a benchmark because port range, timeout, latency, scan technique, retries and inference hardware were not controlled in the preserved material.

The V1 post-defense evaluation preserves raw or aggregate evidence and reports:

- synthetic functional result: TP 4, FP 1, FN 0, TN 19 and F1 0.889; the false
  positive is the deliberate benign-updater hard negative;
- CTU-13 holdout: precision 0.333, recall 0.302, specificity 0.418, F1 0.317
  and MCC -0.282;
- grounded repeated protocol: exact finding and evidence IDs in 50/50 calls,
  with 40/50 passing semantic policy validation;
- reconstructed historical free text: exact finding and evidence IDs in 0/50
  calls, with protocol-specific format and claim audits reported separately;
- separate adversarial fixture: exact evidence in 10/10, no fake-ID echo or
  absolute malware assertion, and 9/10 semantic acceptances.

These results support exact traceability and deterministic enforcement in the
fixed artifact. They do not support general semantic superiority, real-world
malware-detection accuracy or analyst usefulness.

## Claims intentionally not retained

- zero false positives without an independent truth matrix;
- linear scalability or `R² = 0.94` without the measurement series;
- universal 100% detection from a small catalogued rule set;
- CVSS, compliance certification or exploitability derived from static heuristics;
- operational firewall integration not present in the inspected code;
- conclusive SUS or expert-review results without instruments and anonymized responses.

## Threats to validity

- **Internal:** authored fixture expectations reflect the same rule design; the
  CTU-13 holdout was inspected after evaluation and cannot be reused as an
  untouched tuning set.
- **External:** two of thirteen CTU-13 scenarios, two malware-family labels,
  one local 3B model, six fixed prompts and one workstation do not represent
  arbitrary networks, models or analysts.
- **Construct:** open port, behavior match, botnet-origin flow, model acceptance
  and confirmed malicious activity are different constructs.
- **Statistical:** LLM calls are clustered by six fixed prompts; ten repetitions
  do not create 50 independent scenarios, and several observed rates are at
  boundaries that preclude meaningful ranking-stability estimates.
- **Measurement:** broad unsupported-claim vocabulary was audited for historical
  prose but not extracted symmetrically from grounded JSON fields.
- **Reproducibility:** the repeated raw outputs and environment state are
  preserved, but exact external downloads and local model availability remain
  outside repository control; the grounded run's source snapshot is explicitly
  retrospective.
- **Human validity:** no blinded expert ratings were collected for correctness
  or usefulness.

The practical contribution is therefore an evidence-preserving review and
triage workflow with transparent negative results and enforceable trust
boundaries, not autonomous vulnerability or malware confirmation.
