# V1.1 requirement-to-evidence completion audit

Audit date: 2026-08-15
Source of requirements: the repository owner's original V1.1 improvement list
Detailed checklist: `docs/V1_1_RESEARCH_PLAN.md`

## Decision rule

A requirement is complete only when the current repository contains direct
machine-readable evidence, executable verification, or manuscript text that
matches its full scope. A planned procedure, an unchecked assumption, or a
passing narrow test does not count as completion. Human ratings cannot be
replaced by automated output; where they are infeasible, the only valid
resolution is to record that they were not achieved and make no human-result
claim. Venue-specific work is not applicable because no submission is planned.

## Traceability matrix

| Original requirement group | Status | Direct evidence |
|---|---|---|
| Scientific framing and Related Work | Complete for current draft | `academic/artigo/main.tex` contains the explicit comparison section and differentiators. `docs/V1_1_RELATED_WORK_CLAIM_AUDIT.md` maps all 15 works used in Related Work to primary records and bounded claims. `research/v1.1/reference-doi-audit-2026-08-15.json` resolved all 21 DOI-bearing bibliography entries without a metadata mismatch. |
| Detector expansion and error analysis | Complete | Frozen retrospective and confirmatory protocols, 262 family-separated CTU-13 units, 1/5/10-minute analyses, threshold diagnostics, BEH-001/002/003 interpretation, Wilson intervals, TP/FP/FN examples, and generated tables/figures are preserved under `research/v1.1/results/` and `academic/artigo/generated/`. |
| New untouched holdout | Complete | Scenario 11/RBot development and Scenario 6/DonBot holdout were frozen before download/label parsing. The corrected selection record, original record, hashes, timestamp erratum, development grid, and single confirmatory run are retained. NSIS.ay remains explicitly historical and inspected. |
| Second external dataset | Complete within declared construct boundary | The 529-unit Botnet Group Activity Scenario-1 replay is preserved as synthetic CTU-13-derived implementation-transfer evidence, not independent replication. Its deterministic final replay matched the preserved result exactly. |
| Endpoint context and BEH-004 | Complete as an inert functional experiment | The privacy-bounded endpoint schema covers process, executable, signer, parent, file, DNS, and pseudonymous user context. Five frozen cases test BEH-004 and the with/without-Nmap inventory-context comparison. The manuscript does not claim real endpoint accuracy. |
| Multi-model LLM evaluation | Automated scope complete; human assessment explicitly not achieved | The primary 180-attempt matrix, 31-event supplement, ranking audit, component ablations, raw responses, failures, exact model digests, parameters, schemas, and validators are preserved. `docs/V1_1_PHASE4_SUMMARY.md` records the results. The blinded 36-item package exists, but this solo revision collected no independent ratings and makes no analyst-usefulness or human semantic-correctness claim. |
| Prompt-injection evaluation | Complete for the frozen descriptive protocol | Forty-five inert calls cover fake identifiers/CVEs, instruction override, unauthorized controls, embedded formats, long strings, Unicode confusables, conflicting instructions, process, command line, DNS, file, host, service, and Nmap fields. Eligible paired decision-change denominators and API failures are preserved; no attack-success probability is claimed. |
| Abstract, prose, figures, and discussion | Complete for the IEEE-based preprint | The abstract is 222 words and prioritizes question, method, main findings, and implication. Four required figures plus the BEH-002 distribution figure are generated from code. The manuscript includes concrete TP/FP/FN examples, negative-MCC explanation, review-trigger boundary, and qualitative error-cost analysis. The final presentation is one column with a grayscale figure palette. |
| Counterfactual response policies | Complete | Seven offline policies distinguish triage from containment, retain false-positive/false-negative costs, and execute zero actions. Block-on-alert remains central and approval/confirmation requirements are explicit. |
| Reproducibility and version integrity | Complete for automated V1.1 scope | `python -m src.v1_1_reproduce` covers verification, optional CTU-13 download, parsing, deterministic execution, aggregation, tables, figures, and PDF compilation without LLM inference. V1.0 baseline and V1.1 reproduction logs are under `research/v1.1/verification/`. Dataset/model hashes and parameters are retained; runtime, cache, and generated paths are kept on `E:`. V1.0 and the approved monograph hashes still match their release records. |
| Venue-specific submission | Not applicable | The draft uses a one-column IEEE-based preprint layout only as an international quality ruler. No venue submission is planned, so venue, fee, page-limit, ORCID/CRediT, publisher-analyzer, and submission metadata are not release gates. |

## Verified final automated state

- Detailed checklist: 70 of 70 decisions resolved. The repository owner
  approved the title and final snapshot on 2026-08-15.
- Test suite: 84 tests and 6 subtests passed.
- Static checks: Ruff lint and formatting passed.
- Final V1.1 PDF: 18 pages; no overfull box, undefined citation, or undefined
  reference; visual inspection found no clipping or orphan-only final page.
- Final V1.1 PDF SHA-256:
  `36cc38f3f32add6830da88ca55702c299b3b24af2f45c838ea8053ee12918ba1`.
- V1.0 PDF SHA-256:
  `e2b3f216c1b4380e36014086dd06f35fa1e8cde6ae96dd6ad6b18c2227c6f61d`.
- Approved monograph SHA-256:
  `dcace3dbcfc0b6fdd6e549b686ad76da1c9072933de1579e37bdf8430bccd898`.
- LLM inference during final reproduction: none.
- Automatic operational actions: none.

## Final owner decision

The repository owner approved the current title and authorized finalization,
commit, and push on 2026-08-15. The named V1.1 PDF snapshot and release record
are included. Independent human ratings remain a documented future-work
opportunity, not a prerequisite and not a claimed result.
