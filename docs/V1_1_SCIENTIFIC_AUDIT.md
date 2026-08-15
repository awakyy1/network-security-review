# V1.1 scientific and editorial audit

## Status

This is a repository-release quality gate. The V1.1 article must not be
described as validated until its citation, claim, reproducibility and document-
build checks are closed. The repository owner confirmed that IEEE is only an
international presentation ruler and that no venue submission is planned.

Audit opened: 2026-08-15 (America/Sao_Paulo).

## International authority hierarchy

1. The current IEEE Editorial Style Manual for Authors and IEEE Reference
   Guide.
2. The IEEE Author Center's journal-article structure, authorship, ethics,
   data/code and file-validation requirements.
3. Repository-specific scientific-integrity, evidence and versioning rules.

The UniOpet manual and ABNT formatting are not normative inputs for V1.1. They
belong only to the historical TCC context. The working manuscript uses generic
`IEEEtran` solely as a quality and presentation baseline; it does not claim
IEEE submission, review, acceptance, or publication.

## Related-work source audit

| Key | Publication state verified | Claim use | Audit result |
|---|---|---|---|
| `sommer2010` | Peer-reviewed IEEE S&P paper; DOI `10.1109/SP.2010.25` | Operational and evaluation limits of ML-based network IDS | Metadata and claim checked |
| `buczak2016` | Peer-reviewed IEEE journal survey; DOI `10.1109/COMST.2015.2494502` | Breadth of ML/data-mining IDS methods | Metadata checked; text narrowed to avoid assigning Sommer's deployment claims to this survey |
| `neupane2022` | Peer-reviewed IEEE Access survey; DOI `10.1109/ACCESS.2022.3216617` | Stakeholder-tailored explanations and human-in-the-loop X-IDS design | Metadata and abstract-level claim checked |
| `amershi2019` | Peer-reviewed CHI paper; DOI `10.1145/3290605.3300233` | Communicating fallibility, supporting correction and user control | Metadata and guideline-level claim checked |
| `ali2026huntgpt` | Peer-reviewed *Telecom* article; DOI `10.3390/telecom7030073` | Anomaly detection, XAI and LLM integration | Metadata and method summary checked |
| `sadlek2025` | Peer-reviewed JISA article; DOI `10.1016/j.jisa.2024.103956` | Contextual, graph-based severity triage | Metadata and method summary checked; volume corrected from 88 to 89 |
| `xu2024llmsecurity` | arXiv preprint; DOI `10.48550/arXiv.2405.04760` | Broad LLM-for-cybersecurity review and limitations | Metadata and abstract-level claim checked; preprint status made explicit in text |
| `habibzadeh2026` | Peer-reviewed journal survey; DOI `10.1155/jece/3383674` | SOC workflow coverage, maturity and research gaps | Metadata and article content checked |
| `alqahtani2026` | Peer-reviewed Elsevier journal review; DOI `10.1016/j.compeleceng.2026.111184` | Agent reliability, execution safety and governance | Metadata and abstract-level claim checked; omitted coauthor Paras Ahuja restored |
| `hammar2026` | Peer-reviewed NDSS paper; DOI `10.14722/ndss.2026.240358` | Lightweight grounded incident-response planning | Metadata and paper-level claim checked |
| `khanna2026` | arXiv preprint; DOI `10.48550/arXiv.2607.28460` | Reasoning-enabled triage on human-labeled endpoint detections | Metadata and abstract-level claim checked; preprint status made explicit |
| `geng2025` | arXiv preprint; DOI `10.48550/arXiv.2501.10868` | Constrained-decoding differences measured by JSONSchemaBench | Official title corrected; unverified workshop attribution removed |
| `greshake2023` | Peer-reviewed ACM AISec paper; DOI `10.1145/3605764.3623985` | Indirect prompt injection through external data | Replaced the arXiv record with the peer-reviewed proceedings record |
| `pandey2026` | arXiv preprint; DOI `10.48550/arXiv.2605.24421` | Prompt injection through adversarial log fields | Metadata and abstract-level claim checked; preprint status made explicit |

Verification is intentionally claim-scoped. A valid DOI does not by itself
prove that every sentence citing the work is supported, and a preprint is not
presented as peer reviewed.

## Article-structure audit against the IEEE journal baseline

Already present in the working source:

- concise English title without an unsupported novelty claim;
- named authors and institutional affiliation;
- abstract and keywords;
- introduction with problem, boundary, research questions and contributions;
- ordered development covering foundations, related work, artifact, method,
  results, discussion and threats to validity;
- conclusion tied back to the research questions and measured results;
- references;
- IEEE-style numbered sections, numeric citations, captions and in-text calls
  for figures and tables.

Repository quality checks:

- [x] Record venue template, submission metadata, ORCID, and publisher dates as
  not applicable to this non-submitted V1.1 artifact; do not invent them.
- [x] Keep the abstract self-contained, one paragraph and at most 250 words,
  and retain 3--5 index terms.
- [x] Compile the PDF and visually inspect hierarchy, pagination, floats,
  captions, font embedding, links, reference rendering and accessibility.
- [x] Validate numeric references through the DOI/source-to-claim audits and
  `IEEEtran.bst` output.
- [x] Record IEEE submission-only analyzers and PDF Checker as not applicable;
  use the local compiler, metadata, font/link, and visual checks instead.
- [x] Confirm that all figures use IEEE-supported formats, self-contained fonts and
  legible single- or double-column sizing.

## Claim-integrity release checks

- [x] Every numerical statement is generated from or cross-checked against a
  preserved machine-readable result.
- [x] Every literature claim has a directly supporting source passage recorded
  in this audit or a successor evidence matrix.
- [x] No preprint is described as peer reviewed.
- [x] No result from an inspected development set is described as untouched
  holdout evidence.
- [x] No alert is described as proof of malware, exploitability or compromise.
- [x] Schema validity, evidence grounding, policy acceptance and semantic
  correctness remain separate outcomes.
- [x] Hardware differences are reported as environment context; cross-machine
  latency is not interpreted causally.
- [x] All citations resolve, all bibliography entries used by the manuscript
  are rendered, and all rendered references are cited.
- [x] V1.0 source evidence and named PDF hashes still match their frozen
  records.

Final development-PDF evidence: 18 pages, 222-word abstract, correct Unicode
title/author metadata, 26 distinct external links, 51 internal links, and
SHA-256
`36cc38f3f32add6830da88ca55702c299b3b24af2f45c838ea8053ee12918ba1`.
All non-Type-3 font programs are embedded; figure-origin Type-3 fonts are
self-contained glyph programs. The full rendered document was visually checked
without clipping, illegible floats, or an orphan-only final page.

## Official sources used for the editorial audit

- IEEE journal article structure: <https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/>
- IEEE journal templates: <https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/>
- IEEE author checklist: <https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/checklist-for-creating-your-article/>
- IEEE Reference Guide: <https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf>
- IEEE Editorial Style Manual for Authors: <https://ieeeauthorcenter.ieee.org/wp-content/uploads/IEEE-Editorial-Style-Manual.pdf>
