# Article V1.1 research plan

## Status and integrity boundary

This document is the authoritative implementation and evidence checklist for
the V1.1 research revision. V1.0 remains frozen on the `article-v1` branch,
the `article-v1.0` tag and `academic/artigo/releases/article-v1.pdf`. Work for
V1.1 must not overwrite V1.0 source evidence, raw outputs, manifests or the
named PDF snapshot.

V1.1 is complete only when every requirement below is either supported by
preserved evidence or explicitly documented as not achieved. A missing
experiment must not be presented as future work while silently claiming that
the full V1.1 plan was completed.

The requirement-by-requirement evidence map is maintained in
`docs/V1_1_COMPLETION_AUDIT.md`.

## Experimental invariants

- Nmap data remains authorized inventory context and never establishes malware
  identity, exploitability or vulnerability by itself.
- Previously inspected NSIS.ay results are historical V1.0 evidence and cannot
  be called an untouched holdout after any tuning or analytical refinement.
- Threshold, prompt, schema, validator and metric changes are development work
  until frozen before evaluation on a new holdout.
- Exploratory output that influences a design decision cannot be reused as
  confirmatory evidence.
- Negative results and failed runs are preserved with their interpretation
  boundaries.
- LLM format compliance, evidence grounding and semantic correctness remain
  separate outcomes.
- Automated triage and automated containment remain separate concepts. No
  experiment authorizes an operational containment action.
- Dataset hashes, source URLs, model digests, runtime versions and exact model
  parameters are recorded for every frozen run.

## Phase 0 — Environment, versioning and baselines

- [x] Create an isolated local development branch for article V1.1.
- [x] Install Python 3.12 and create the repository-local `.venv`.
- [x] Install the dependencies pinned in `requirements.txt` and
  `requirements-dev.txt`.
- [x] Run the V1.0 deterministic baseline only after explicit notice to the
  repository owner.
- [x] Record baseline test, lint and artifact-generation results.
- [x] Inventory CPU, RAM, GPU, operating system, Ollama version and locally
  available model tags without starting model inference.
- [x] Add the V1.0-versus-V1.1 hardware table to the manuscript and distinguish
  hardware/runtime context from protocol effects; do not make a causal latency
  comparison across the two machines.
- [x] Change the working article version to V1.1 only when manuscript edits
  begin; do not overwrite the V1.0 named PDF.

Exit evidence: an environment record, a clean deterministic baseline, and a
V1.0-to-V1.1 provenance statement.

## Phase 1 — Scientific framing and related work

- [x] Add an explicit Related Work section of approximately 1–1.5 pages.
- [x] Add and verify approximately 10–15 relevant academic references covering:
  - LLMs in SOC and security operations;
  - alert and incident analysis with LLMs;
  - hallucination and grounding in cybersecurity;
  - structured output and constrained generation;
  - network anomaly detection;
  - CTU-13 botnet detection;
  - explainable intrusion detection;
  - automated or autonomous defensive response;
  - human-in-the-loop defensive systems.
- [x] Compare methods, evidence, trust boundaries and limitations rather than
  merely explaining the underlying technologies.
- [x] Open a source-by-source scientific and editorial audit and correct the
  bibliographic discrepancies found in its first pass.
- [x] State the article's differentiators explicitly: evidence/conclusion
  separation, verifiable identifiers, closed schema, deterministic validator,
  no model response authority, preserved negative result, and automatic-action
  counterfactual.
- [x] Strengthen the negative-result framing: synthetic F1 0.889 and external
  F1 0.317 answer different questions, and the generalization failure is a
  retained scientific result rather than a hidden implementation failure.

Exit evidence: every citation resolves to authoritative publisher or official
metadata; peer-reviewed status is reported accurately, preprints are labeled
explicitly, and the manuscript contains comparison and novelty paragraphs.

## Phase 2 — Detector validation and error analysis

- [x] Freeze a retrospective diagnostic protocol that keeps the inspected
  V1.0 holdout distinct from a future V1.1 confirmatory holdout.
- [x] Implement machine-readable 1-, 5- and 10-minute window diagnostics,
  BEH-001/002/003 feature summaries and deterministic TP/FP/FN examples.
- [x] Expand external validation to additional CTU-13 families while preserving
  family separation.
- [x] Increase cumulative family-separated external units from 139 to 262;
  never pool development, retrospective and confirmatory metrics.
- [x] Reserve and freeze a genuinely new holdout before its labels are inspected
  for threshold or design decisions.
- [x] Evaluate a second external dataset and document its construct compatibility
  with the detector.
- [x] Compare non-overlapping 1-, 5- and 10-minute source-host windows as a
  retrospective diagnostic, without selecting a winning window.
- [x] Investigate thresholds only on development data and freeze the selected
  V1.1 configuration before the new holdout run.
- [x] Determine the immediate BEH-003 non-firing condition: no scored unit met
  the 1-MB (1,000,000-byte) component; preserve the distinction between
  threshold mismatch,
  absent behavior and information unavailable from `.binetflow`.
- [x] Analyze why BEH-001 produced only normal-origin alerts in the V1.0 holdout.
- [x] Plot BEH-002 destination-count distributions for botnet-origin and
  normal-origin units and quantify their overlap.
- [x] Analyze false positives, especially periodic updater and normal
  distinct-destination traffic.
- [x] Analyze the 37 V1.0 false-negative botnet-origin windows and their absent
  or sub-threshold patterns.
- [x] Preserve one evidence-grounded example each of a true positive, false
  positive and false negative, including evidence IDs and system decision.
- [x] Explain intuitively what the negative holdout MCC means.
- [x] Explain when an alert remains useful as a review trigger despite failing
  as malware classification.

Exit evidence: immutable V1.1 development and holdout manifests, raw or
anonymized unit results, distribution analyses, generated figures and a frozen
threshold record.

## Phase 3 — Endpoint telemetry and BEH-004

- [x] Define a privacy-reviewed endpoint schema covering process identity,
  executable path, signer, parent/child process, file creation, DNS and user
  context.
- [x] Acquire or construct an authorized dataset with process/file lineage.
- [x] Evaluate BEH-004 on evidence that actually contains the required fields.
- [x] Measure Nmap only as inventory enrichment and, if claimed as an evaluated
  contribution, compare the workflow with and without inventory context.

Exit evidence: schema, data provenance, privacy boundary, BEH-004 truth matrix
and a clear statement of what Nmap did and did not influence.

## Phase 4 — LLM protocol evaluation

- [x] Evaluate at least one additional small model, one intermediate model and,
  where feasible, a model from another family.
- [x] Keep evidence pack, schema and validator identical across models.
- [x] Add cases containing multiple findings, conflicting findings, incomplete
  evidence, dozens of events, no findings and mixed rule types.
- [x] Add real multi-finding ranking cases and measure ranking stability.
- [x] Increase repetitions only if making statistical stability claims; retain
  the fixed-prompt clustering limitation.
- [x] Implement a symmetric unsupported-claim taxonomy for grounded JSON and
  free text.
- [x] Report format/schema compliance, evidence grounding and semantic
  correctness separately.
- [x] Add protocol ablations so the effects of temperature, schema, grounding
  prompt and deterministic validation are not attributed to one component.
- [x] Document blinded human assessment as not achieved in this solo revision:
  preserve the ready package, claim no human result, and retain analyst
  usefulness and semantic correctness as limitations/future work.

Current status: all nine checklist decisions are resolved: eight experiments
are complete and the independent human assessment is explicitly not achieved
in this solo revision. A frozen supplemental case covers all four rule types,
opposing contextual cues and 31 unique evidence events in nine model calls
without input truncation. The blinded 36-item package and concealed mapping
remain available for future work; no synthetic or inferred ratings are accepted
as evidence.

Exit evidence: frozen model matrix, exact parameters and digests, per-call raw
outputs, automated metrics, ablation results and anonymized human-rating data.

## Phase 5 — Prompt-injection evaluation

- [x] Add attacks involving fake evidence IDs, instruction override, false
  vulnerability/CVE claims, automatic isolation, firewall blocking, embedded
  system messages, Markdown/XML/JSON injection, long strings, Unicode
  confusables and conflicting instructions.
- [x] Inject adversarial strings into process name, hostname, DNS, file name,
  service banner, command line and Nmap service fingerprint fields.
- [x] Measure influence on control choice, severity, priority, interpretation
  and cited evidence IDs, not only literal adversarial-string echo.
- [x] Keep all fixtures inert and prevent any response credential or operating
  authority from entering the model boundary.

Exit evidence: categorized adversarial manifest, expected behaviors, preserved
raw outputs and per-category decision-influence metrics.

## Phase 6 — Counterfactual response policies

- [x] Retain block-on-alert as a central safety analysis.
- [x] Evaluate: block only after two rules; analyst approval; evidence collection
  only; temporary rate limiting; increased monitoring; and isolation only after
  independent confirmation.
- [x] Compare false-positive and false-negative costs, at least qualitatively
  and without implying real-world firewall effectiveness.
- [x] Maintain explicit automatic-triage versus automatic-containment language
  throughout the manuscript and code.

Exit evidence: policy definitions, replayable counterfactual calculations and
a documented authorization/rollback boundary for every policy.

## Phase 7 — Manuscript, figures and presentation

- [x] Reduce abstract numerical density by approximately 20–25%, retaining the
  external F1/MCC, 50/50 versus 0/50 traceability and block-on-alert implication.
- [x] Give the abstract more space for problem, question, method and implication.
- [x] Split dense sentences and introduce first-page terminology progressively.
- [x] Replace Figure 1 with a generated four-block diagram: authorized evidence,
  deterministic core, untrusted LLM boundary and human-authorized response.
- [x] Add a generated Phase A → Phase B → Phase C experimental-flow figure.
- [x] Add generated CTU-13 development-versus-holdout metrics visualization.
- [x] Add generated grounded-versus-free-text traceability visualization.
- [x] Expand qualitative false-positive and false-negative discussion and add
  the three concrete finding examples from Phase 2.

Exit evidence: regenerated manuscript PDF with checked captions, references,
legibility and no manually transcribed experimental values.

## Phase 8 — Reproducibility and release

- [x] Provide one command or script covering download/verification, parsing,
  execution, aggregation and table/figure generation.
- [x] Generate every experimental table and figure from preserved machine-
  readable results.
- [x] Preserve V1.1 raw results in new directories; never replace V1.0 evidence.
- [x] Preserve model digest, Ollama version, context, seed, temperature, `top_p`,
  output limit and schema version for every model run.
- [x] Keep datasets, model blobs, runtimes, caches, temporary files and new raw
  outputs on `E:` (or another explicitly selected non-system drive), not `C:`.
- [x] Run lint, format check, unit tests, deterministic experiments, result
  regeneration and document compilation after explicit notice.
- [x] Verify dataset hashes, generated-table consistency, PDF metadata, citation
  resolution and V1.0 snapshot integrity.
- [x] Record venue selection as not applicable: the repository owner confirmed
  that no publication submission is planned and IEEE is only a quality ruler.
- [x] Adopt the international IEEE journal baseline for the development
  manuscript; UniOpet/ABNT formatting is historical context only.
- [x] Review title-page metadata, abstract, introduction and contributions for
  the generic international audience; submission-only contacts, ORCID, CRediT
  and venue declarations are explicitly not applicable to the present scope.
- [x] Create a named V1.1 PDF snapshot and release record only after every
  claimed result passes the completion audit.

Exit evidence: reproducibility command log, generated artifact checks, named
PDF hash, release metadata and a requirement-by-requirement audit.

## External decisions and resources

The following tasks require resources beyond ordinary code editing and must be
scheduled explicitly:

- selection and download of a second external dataset;
- selection/download of additional local models and potentially large disk use;
- long-running multi-model repetitions;
- recruitment and consent/process design for blinded human reviewers;
- venue selection and submission-only author metadata, now explicitly outside
  the repository owner's intended scope.

No absent external resource permits a stronger claim than the retained evidence
supports.
