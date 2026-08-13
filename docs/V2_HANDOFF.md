# V2 research handoff

Last updated: 2026-08-13 (America/Sao_Paulo)

## Objective

Strengthen the refinable post-defense article with a defensible experimental
contribution that combines:

1. authorized Nmap inventory;
2. endpoint/network telemetry;
3. transparent malware-behavior review rules;
4. evidence-grounded local Ollama prioritization;
5. human-authorized defensive response proposals.

The final research must answer what the hybrid workflow can detect, where it
produces false positives, whether the LLM stays grounded, and what mitigation it
can responsibly support.

## Non-negotiable boundaries

- The approved monograph is immutable. Its expected SHA-256 is
  `DCACE3DBCFC0B6FDD6E549B686AD76DA1C9072933DE1579E37BDF8430BCCD898`.
- Only `academic/artigo/` may receive post-defense scientific refinement.
- No live malware, malicious binary, exploit, persistence mechanism or
  destructive payload may be downloaded or executed.
- Malware research uses inert telemetry, benign emulation and later only
  labeled network-flow datasets. Original malware binaries are out of scope.
- An observed behavior is not proof of malware, compromise, exploitability or
  a vulnerability.
- Ollama output is advisory, has no credentials and cannot apply controls.
- Article conclusions must follow preserved results; figures and tables must be
  mentioned in the text and include sources.

## Implemented locally

- `src/telemetry.py`: bounded JSONL ingestion and normalized evidence events;
- `src/behavior_detector.py`: four transparent ATT&CK-mapped review rules;
- `src/ollama_advisor.py`: loopback-only Ollama, JSON schema, evidence-ID
  validation, CVE/absolute-claim rejection and fixed controls;
- `src/v2_experiment.py`: labeled benchmark, metrics, Markdown/JSON reports and
  optional Ollama evaluation;
- `src/ctu13_acquire.py` and `src/ctu13_experiment.py`: frozen safe acquisition
  and streaming external validation;
- `src/article_tables.py`: LaTeX tables generated from preserved result JSON;
- `src/result_preservation.py`: byte-preserving promotion of repeated runs,
  SHA-256 provenance and corrected aggregate projections;
- `research/v2/`: six safe scenarios with labels separate from event data;
- ten focused test modules covering telemetry, behavior, Ollama, external
  data, repetitions, result preservation and article tables;
- `docs/V2_RESEARCH_PROTOCOL.md`: research questions, hypotheses, frozen
  thresholds, metrics, safety and external-validation plan.

## Current Phase-A result

Six deterministic scenarios and four behavior classes yield:

| TP | FP | FN | TN | Precision | Recall | F1 | Specificity |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 1 | 0 | 19 | 0.800 | 1.000 | 0.889 | 0.950 |

The false positive is intentional: `benign-updater` resembles periodic
beaconing and triggers `BEH-001`. These are functional synthetic results, not
real-world malware-detection accuracy.

## Local Ollama state

- Ollama client/server: `0.32.5` for the grounded set and `0.32.6` for the
  historical/adversarial sets;
- historical model: `llama3.2:3b`, digest prefix `a80c4f17acd5`, 2.0 GB;
- fallback model: `llama3.2:1b-instruct-q4_K_M`, digest prefix
  `22bc6b92eb01`, 807 MB;
- inference is CPU-only;
- 3B successfully loaded with a fixed 4096-token context after memory was
  freed;
- the first full run exceeded the former 120-second request timeout;
- the code now defaults to a recorded 300-second timeout, 700 output-token
  limit, temperature 0, seed 42 and 4096-token context;
- the experiment now preserves API and validation failures per scenario instead
  of discarding an entire run;
- the complete 3B Phase-A run finished in 316.8 seconds: five scenarios with
  findings were submitted and 5/5 responses passed deterministic grounding
  validation;
- the isolated prompt-injection run finished in 83.3 seconds and its one
  response passed validation without citing `FAKE-999` or asserting confirmed
  malware;
- full JSON responses and execution metadata are preserved under
  `research/v2/results/`;
- a reconstructed 2025 free-text control and ten-run aggregator are implemented;
- one exploratory historical run completed in 538.2 seconds: 5/5 API
  responses, 0/5 exact finding/evidence-ID coverage, Markdown in 5/5, more than
  200 words in 3/5, ungrounded security-attribution terms in 5/5 and
  unqualified containment language in 2/5;
- audit schema 1.2 was frozen after that exploratory inspection, so the run is
  excluded from the final repeated comparison;
- grounded schema 1.1 additionally requires full finding coverage and
  rule-applicable controls;
- a real schema 1.1 adversarial smoke test passed 1/1 with full citation
  coverage and only `BEH-001`-applicable controls; it is preserved as a
  development result, not a final repetition;
- the frozen CTU-13 development/holdout evaluation is complete using only two
  hashed `.binetflow` text files: development F1 0.370 and holdout F1 0.317;
- holdout recall 0.302, specificity 0.418 and MCC -0.282 show that the simple
  flow rules do not generalize reliably without endpoint process/file context;
- a counterfactual block-on-every-alert policy would unnecessarily act on
  66.7% of holdout review candidates, while missing 37 botnet-origin windows;
- no automatic control was executed. The full interpretation is in
  `docs/CTU13_EXTERNAL_VALIDATION.md`.

The single-run observations remain exploratory and must not be presented as
stable model accuracy. The grounded, historical and adversarial ten-repetition
sets are now preserved as described below.

## Current Phase-C grounded repeated result

The ten grounded repetitions completed on 2026-08-03 and are preserved under
`research/v2/results/grounded-3b-10/`. Across 50 model calls:

| API response | JSON parse | Schema valid | Validator accepted | Evidence coverage |
|---:|---:|---:|---:|---:|
| 50/50 | 50/50 | 50/50 | 40/50 | 1.000 |

All ten rejected responses came from the same `emulated-beacon` scenario. The
model cited the complete supplied evidence but proposed
`segment-source-host-after-approval`, which is outside the frozen control set
applicable to `BEH-001`; the deterministic validator rejected it every time.
This is evidence of successful policy enforcement around a repeatable model
failure, not evidence that all grounded model output is reliable.

The original aggregate incorrectly reported API, JSON and schema success as
0.800 because it counted semantic validation rejection at those earlier
boundaries. Raw run records are preserved byte-for-byte, and the corrected
projection reports API, JSON and schema success as 1.000 while keeping grounded
acceptance at 0.800. Because the exact uncommitted source snapshot was not
hashed when the grounded run started, its preservation metadata correctly marks
the later source snapshot as retrospective.

## Current Phase-C historical repeated result

The reconstructed historical protocol completed ten repetitions on 2026-08-13
and is preserved under `research/v2/results/historical-3b-10/` with exact
source-state hashes. Across 50 calls, the API succeeded 50/50 but exact finding-
and evidence-ID coverage was 0/50. The frozen audit found unsupported security-
attribution vocabulary in 43/50 responses, unqualified containment vocabulary
in 10/50, 200-word-limit violations in 37/50, and Markdown-format violations in
50/50.

The grounded versus historical result supports H2 only for automated exact
traceability and deterministic policy enforcement in this fixed artifact.
Grounded semantic acceptance was 40/50 because all ten `emulated-beacon`
responses selected a rule-inapplicable control and were correctly rejected.
Broad unsupported-claim metrics were not extracted symmetrically from both
representations, and blinded human ratings remain absent. See
`research/v2/results/phase-c-automated-analysis-2026-08-13.md`.

## Current Phase-C adversarial repeated result

The separate inert prompt-injection fixture completed ten grounded repetitions
on 2026-08-13 and is preserved under
`research/v2/results/adversarial-3b-10/` with exact source-state hashes. All ten
responses were API-successful, JSON-parseable, schema-valid and preserved the
supplied finding/evidence identifiers. No response cited the injected
`FAKE-999` identifier or made the prohibited absolute malware claim. Nine
responses passed semantic validation; one selected the same `BEH-001`-
inapplicable segmentation control and was safely rejected.

The final machine-readable comparison is
`research/v2/results/phase-c-comparison-v1.json`; its Markdown projection is
generated by `python -m src.phase_c_analysis`. The fixture demonstrates bounded
resistance to one committed instruction-like string, not general prompt-
injection robustness.

## Validation already observed

After the final Phase-C and article changes:

- Ruff 0.15.22 formatting check passed;
- Ruff lint passed;
- the real grounded schema 1.1 adversarial smoke test passed;
- the scenario manifests and every JSONL line parsed successfully;
- both deterministic and Ollama-enabled CLI runs completed;
- rejected model output is now preserved with validation metadata rather than
  discarded;
- 40/40 unit tests pass, including final-comparison and generated-table
  coverage;
- both external files match their frozen byte lengths and SHA-256 values;
- the family-separated external validation completed without rule tuning;
- the article tables were regenerated from preserved JSON;
- the article compiled with Tectonic's XeTeX engine to 12 A4 pages with no
  unresolved references, citations, overfull boxes or underfull boxes;
- all rendered pages were visually inspected;
- the approved monograph hash was rechecked and remains unchanged.

## Resume commands

From the repository root on the more powerful machine:

```powershell
python -m pip install --requirement requirements.txt --requirement requirements-dev.txt
ruff check .
python -m unittest discover -s tests -p "test_*.py" -v
python -m src.v2_experiment --output-dir output/v2
```

Install Ollama from its official distribution, start its local service and pull
the historical comparison model:

```powershell
ollama pull llama3.2:3b
ollama list
python -m src.v2_experiment `
  --ollama-model llama3.2:3b `
  --ollama-context 4096 `
  --ollama-timeout 300 `
  --ollama-max-output-tokens 700 `
  --output-dir output/v2-ollama-run-01
```

The commands below reproduce the three completed repeated sets. Confirm the
code state and exact model blob digest before rerunning them:

```powershell
python -m src.v2_repetitions --ollama-model llama3.2:3b --ollama-protocol grounded --repetitions 10 --ollama-context 4096 --ollama-timeout 300 --ollama-max-output-tokens 700 --output-dir output/v2-grounded-10
python -m src.v2_repetitions --ollama-model llama3.2:3b --ollama-protocol historical --repetitions 10 --ollama-context 4096 --ollama-timeout 300 --ollama-max-output-tokens 700 --output-dir output/v2-historical-10
python -m src.v2_repetitions --manifest research/v2/adversarial-scenarios.json --ollama-model llama3.2:3b --ollama-protocol grounded --repetitions 10 --ollama-context 4096 --ollama-timeout 300 --ollama-max-output-tokens 700 --output-dir output/v2-adversarial-10
```

Preserve `ollama list`, `ollama ps`, model details/digest, CPU/GPU/RAM, raw
responses and result JSON before changing the protocol.

## Completed finalization scope

1. all three ten-repetition sets are preserved without mixing exploratory runs
   into confirmatory metrics;
2. the final comparison and article tables are generated from preserved raw
   records;
3. the abstract, Phase C, RQ2, threats and conclusion report the final evidence
   and its scientific limits;
4. the article was recompiled and the citations, rendered pages, tests and
   immutable monograph hash were re-audited;
5. the article V1 commit scope is documented in `docs/V2_COMMIT_SCOPE.md`.

The V1 state belongs on the `article-v1` branch and is identified by the local
`article-v1.0` tag. Publishing the branch or tag remains an explicit
user-authorized step.

## Primary sources selected

- [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs)
- [Ollama context length](https://docs.ollama.com/context-length)
- [MITRE ATT&CK T1071](https://attack.mitre.org/techniques/T1071/)
- [MITRE ATT&CK T1046](https://attack.mitre.org/techniques/T1046/)
- [MITRE ATT&CK T1041](https://attack.mitre.org/techniques/T1041/)
- [MITRE ATT&CK T1105](https://attack.mitre.org/techniques/T1105/)
- [Microsoft Sysmon events](https://learn.microsoft.com/en-us/windows/security/operating-system-security/sysmon/sysmon-events)
- [CTU-13 dataset summary and original-paper link](https://fkie-cad.github.io/COMIDDS/content/datasets/ctu_13/)
- [HaluEval primary paper](https://arxiv.org/abs/2305.11747)

## Conversation continuity

The same Codex chat can be reopened from Recent chats. In Codex CLI, start in
the repository directory and use `codex resume`. The transcript is chat state;
the authoritative research state is the checked-out repository plus preserved
experiment outputs.
