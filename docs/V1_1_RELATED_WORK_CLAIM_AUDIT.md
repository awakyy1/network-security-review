# V1.1 related-work source-to-claim audit

Audit date: 2026-08-15
Manuscript section: `Related Work and Positioning`

The machine-readable DOI audit is `research/v1.1/reference-doi-audit-2026-08-15.json`: all 21 bibliography entries carrying a DOI resolved through Crossref or DataCite with no DOI/year mismatch. That check is necessary but not sufficient. The table below records the separate semantic check for every work cited in the Related Work section.

| Key | Publication status | Primary record checked | Claim actually supported in the manuscript | Decision |
|---|---|---|---|---|
| `sommer2010` | Peer-reviewed IEEE S&P conference paper | [IEEE Xplore](https://ieeexplore.ieee.org/document/5504793) | Operational ML-NIDS limitations, including error cost, semantic gap, traffic variability, evaluation, and adversarial setting. | Retain. Do not generalize its 2010 observations into a quantitative claim about this artifact. |
| `buczak2016` | Peer-reviewed IEEE survey | [DOI/publisher record](https://doi.org/10.1109/COMST.2015.2494502) | Surveys a broad range of data-mining and ML methods for intrusion detection. | Retain. Used only as breadth/context. |
| `garcia2014ctu13` | Peer-reviewed journal article | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0167404814000923) | Introduces and compares botnet-detection methods on a labeled dataset containing botnet, normal, and background traffic. | Retain. The article does not imply that every positive-origin window contains a rule-observable attack. |
| `neupane2022` | Peer-reviewed IEEE Access survey | [DOI/publisher record](https://doi.org/10.1109/ACCESS.2022.3216617) | Calls for stakeholder-tailored explanations, explanation metrics, and human-in-the-loop X-IDS design. | Retain. |
| `ali2026huntgpt` | Peer-reviewed journal article | [MDPI](https://www.mdpi.com/2673-4001/7/3/73) | Integrates a Random Forest IDS, SHAP/LIME explanations, and an LLM conversational interface for analyst-facing interpretation. | Retain. Describe it as a prototype/integration study, not proof of operational SOC benefit. |
| `sadlek2025` | Peer-reviewed journal article | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2214212624002588) | Correlates alert sequences with kill-chain attack graphs, MITRE ATT&CK context, and asset criticality before assigning severity. | Retain. Current manuscript wording “graph-based incident triage” is supported. |
| `xu2024llmsecurity` | arXiv preprint/systematic review | [arXiv](https://arxiv.org/abs/2405.04760) | Reviews LLM applications across cybersecurity and reports dataset diversity, interpretability, privacy, and evaluation limitations. | Retain only with explicit preprint label. Do not call peer reviewed. |
| `habibzadeh2026` | Peer-reviewed journal survey | [Wiley](https://onlinelibrary.wiley.com/doi/10.1155/jece/3383674) | Maps LLM use across SOC detection, analysis, and response and identifies operational/research gaps. | Retain. Avoid adopting its industry-statistic claims, which are not needed here. |
| `alqahtani2026` | Peer-reviewed journal systematic review | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0045790626002569) | Reviews autonomy, tool use, multi-agent design, execution safety, and governance constraints in LLM cyber defense. | Retain. Supports the governance/autonomy boundary, not autonomous containment effectiveness. |
| `hammar2026` | Peer-reviewed NDSS conference paper | [NDSS paper](https://www.ndss-symposium.org/wp-content/uploads/2026-f358-paper.pdf) | Uses fine-tuning, retrieval, and lookahead planning to reduce hallucination in incident-response planning under stated assumptions. | Retain. Manuscript wording says “reduce,” not “eliminate,” hallucination. |
| `khanna2026` | arXiv preprint | [arXiv](https://arxiv.org/abs/2607.28460) | Evaluates reasoning-enabled triage on human-labeled Windows endpoint detections. | Retain only with explicit preprint label; no transfer of its reported accuracy to this artifact. |
| `geng2025` | arXiv preprint | [arXiv](https://arxiv.org/abs/2501.10868) | JSONSchemaBench evaluates constraint coverage, efficiency, and output quality across structured-generation frameworks. | Retain only with explicit preprint label. Supports the distinction between schema compliance and output quality. |
| `amershi2019` | Peer-reviewed ACM CHI paper | [ACM DOI page](https://doi.org/10.1145/3290605.3300233) | Proposes and evaluates human–AI interaction guidance including user control, correction, and communicating system limits. | Retain. Used as design guidance, not a security-control standard. |
| `greshake2023` | Peer-reviewed ACM AISec paper | [AISec 2023 record](https://aisec.cc/2023/) | Demonstrates indirect prompt injection arising when LLM applications blur instructions and externally controlled data. | Retain. Telemetry is described as an analogous adversarial input surface, not as proof of identical exploitability. |
| `pandey2026` | arXiv preprint | [arXiv](https://arxiv.org/abs/2605.24421) | Places adversarial instructions in SOC/log fields and reports that defenses reduce but do not remove decision manipulation. | Retain only with explicit preprint label and bounded wording. |

## Editorial findings

- The section currently distinguishes peer-reviewed works from preprints in prose. Keep that distinction in every revision.
- The cited sources support methodological positioning; none supports a claim that the present detector identifies malware or that its model recommendations are semantically correct.
- Recent 2026 sources are legitimate as of the audit date, but their correction/retraction status must be checked again immediately before submission because the literature is still changing.
- Publisher metadata and abstracts support the current paraphrases. No long quotation is used.
- A target journal may require a different balance of references. Relevance and direct support take priority over increasing citation count.
