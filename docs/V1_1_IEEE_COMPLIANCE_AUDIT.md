# V1.1 IEEE journal-baseline compliance audit

Audit date: 2026-08-15
Scope: IEEE-based scientific-article quality baseline in a sober one-column
preprint layout. The repository owner has confirmed that no publication
submission is planned; periodical-specific page limits, metadata, fees, and
submission checks are therefore not applicable.

## Normative sources

- [IEEE Author Center: Structure Your Article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- [IEEE Editorial Style Manual for Authors](https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE-Editorial-Style-Manual-for-Authors.pdf)
- [IEEE Reference Guide](https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf)
- [IEEE article-creation checklist](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/checklist-for-creating-your-article/)
- [IEEE ethical requirements](https://journals.ieeeauthorcenter.ieee.org/author-ethics/ethical-requirements/)

The UniOpet manual is not a normative source for article V1.1.

## Current conformance

| Requirement | Status | Repository evidence or remaining action |
|---|---|---|
| IEEE structural baseline | Implemented | `academic/artigo/main.tex` uses `IEEEtran` with `11pt`, `a4paper`, and `onecolumn`. This is a readable preprint layout, not a claim of conformance to a particular periodical. |
| Concise descriptive title | Implemented | Title describes evidence grounding, local language models, behavioral telemetry, and defensive review. |
| One-paragraph, self-contained abstract, at most 250 words | Implemented | The final automated-matrix and block-on-alert implications are integrated; the abstract has 222 words, no citations, equations, or mathematical dash notation. |
| Index terms | Implemented | Five concise index terms are present. |
| Introduction with literature context and research questions | Implemented | Introduction states three RQs and six contributions. |
| Reproducible methodology | Implemented for the automated scope | Frozen manifests, hashes, thresholds, dataset roles, exclusion policy, model settings, hardware, analysis boundaries, and final reproduction logs are documented. |
| Results separated from interpretation | Implemented | Results, Discussion, Threats to Validity, and Conclusion are separate sections. |
| Conclusion limited to observed evidence | Implemented for the automated scope | Final matrix, supplement, failure, and zero-action results are integrated without an automatic-response effectiveness or malware-attribution claim. |
| References directly supporting claims | Audited for the current draft | The manuscript cites and renders exactly 27 sources. All 21 DOI-bearing bibliography records resolved without a DOI/year mismatch, including all 19 DOI-bearing sources used by the article, and every Related Work citation has a source-to-claim record. Preprints are explicitly labeled and are not described as peer reviewed. Recheck corrections/retractions before any future public release. |
| Dataset citation and provenance | Implemented | Article and dataset records are separate; DOI, license, hashes, row exclusions, and synthetic/derived status are explicit. |
| Accurate and complete reporting | Implemented by policy | Negative MCC, false positives, parser exclusions, rejected model outputs, API failures, and zero executed actions are retained. |
| Author submission metadata and ORCID | Not applicable | No venue submission is planned. Names and historical affiliation are retained; identifiers and contacts are not invented. |
| Human-subjects/ethics statement | Not applicable to completed experiments | Current experiments use public or synthetic telemetry and no human participants. The unexecuted blinded-rating package remains future work and would require an ethics/consent determination before use. |
| Human semantic evaluation | Explicitly not achieved | A rubric and blinded package exist, but this solo revision collected no independent ratings. Automated output does not substitute for them, and no analyst-usefulness claim is made. |
| Publication-specific template and limits | Not applicable | The one-column IEEE-based layout is used only as a quality ruler. |
| Development PDF build and visual inspection | Implemented | The preprint build has 18 pages, correct Unicode metadata, 26 distinct external links, 51 internal links, no undefined citations/references, no overfull boxes, and no clipped or orphan-only page in the visual audit. No em or en dash glyph appears in extracted PDF text. |
| IEEE submission-only analyzers and PDF Checker | Not applicable | These publisher workflow tools are not required for a non-submitted research artifact. Local build, reference, metadata, font, link, and visual checks remain required. |
| Publisher similarity screening | Not applicable | Local citation and claim audits are retained; no publisher submission is planned. |

## Claim-control rules

1. A cited source must support the sentence in which it appears; metadata correctness alone is insufficient.
2. Publisher pages, standards bodies, official dataset records, and peer-reviewed papers are preferred over secondary summaries.
3. arXiv items remain labeled as preprints even if recent and relevant.
4. Automated lexical audits are reported as lexical flags, not human-confirmed semantic errors.
5. API failure, missing response, or validator rejection remains in the denominator defined by the frozen protocol.
6. Retrospective analyses are never renamed confirmatory, and inspected holdouts are never described as untouched.
7. Synthetic CTU-13-derived transfer data are never presented as an independent real-world replication.
8. No model output authorizes containment, attribution, or a claim of confirmed compromise.

## Quality-baseline gate

The manuscript may be frozen as a repository research artifact after its local
claim, citation, reproducibility, build, font/link, and visual checks pass. This
audit does not describe the article as IEEE-published, IEEE-reviewed, or ready
for a specific venue. Any future submission would reopen venue-specific gates.
