# Methodology and evidence boundary

This document supports the post-defense refinement of the scientific article and the interpretation of the software artifact. It does not amend the approved monograph, which remains archived unchanged.

## Research design

The study is applied, exploratory and technological. Its artifact is described retrospectively through Design Science Research: problem identification, objectives, design/development, demonstration, evaluation and communication.

The available evaluation is an exploratory demonstration rather than a controlled comparative experiment. Reported scenario totals describe the source study; they do not establish universal detection accuracy or exploitability.

## Units of analysis

1. **Observation:** host, port, protocol and fingerprint present in an Nmap XML document.
2. **Derived review item:** a documented rule matched an observation.
3. **Generated narrative:** contextual text produced by the pre-defense optional LLM path.
4. **Human conclusion:** validation that requires environmental and independent evidence.

These units must not be collapsed into a single “vulnerability” count.

## Preserved results

The source manuscript reported 24 hosts, 21 open ports, seven rule-scoped items and 352 aggregate seconds across three scenarios. The corrected descriptive ratio is approximately 14.7 seconds per host. It is not a benchmark because port range, timeout, latency, scan technique, retries and inference hardware were not controlled in the preserved material.

## Claims intentionally not retained

- zero false positives without an independent truth matrix;
- linear scalability or `R² = 0.94` without the measurement series;
- universal 100% detection from a small catalogued rule set;
- CVSS, compliance certification or exploitability derived from static heuristics;
- operational firewall integration not present in the inspected code;
- conclusive SUS or expert-review results without instruments and anonymized responses.

## Threats to validity

- **Internal:** expected outcomes may have been derived from the same rules used by the artifact.
- **External:** three scenarios and a narrow service set cannot represent arbitrary networks.
- **Construct:** open port, review item and confirmed vulnerability are different constructs.
- **Reproducibility:** complete original XMLs, logs, repeated runs, prompts, hardware and independent labels were not all preserved.

The practical contribution is therefore an evidence-preserving review workflow and a transparent defensive implementation, not a claim of autonomous vulnerability confirmation.
