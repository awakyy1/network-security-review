# Reproducibility

## Reproduction levels

| Level | Available | Procedure |
|---|---|---|
| Static inspection | Yes | Review source, tests, commit history and academic documents |
| Deterministic unit tests | Yes | Run the standard-library test suite |
| Synthetic end-to-end report generation | Yes | Process `examples/nmap/synthetic-enterprise.xml` |
| V2 synthetic behavior benchmark | Yes | Run the committed inert telemetry scenarios and compare against separate labels |
| CTU-13 external flow validation | Yes | Verify the frozen manifest and hashes, then run the streaming evaluator |
| Grounded Ollama evaluation | Yes, automated scope | Ten repetitions and all raw responses are preserved; independent human ratings remain future work |
| Grounded versus historical comparison | Yes, automated scope | All three frozen ten-repetition sets, raw responses, provenance and the generated comparison are preserved; blinded human ratings remain future work |
| Original 2025 experiment | Partial | Scenario totals are documented, but complete raw evidence was not preserved |
| Original 2025 LLM evaluation | No | Exact prompts, model/hardware state, outputs and independent ratings are incomplete |

## Environment

- Python 3.10 or newer;
- dependencies pinned in `requirements.txt`;
- no live Nmap or Zabbix instance required for unit tests;
- LaTeX, BibTeX and the one-column `IEEEtran`-based preprint class are the V1.1
  development-document environment. If publication is ever pursued, the
  chosen venue's exact template will supersede this generic layout.

## Software verification

For V1.1, the default one-command verification runs tests and static checks,
regenerates inert deterministic outputs, tables and figures, and compiles the
development PDF. It reads preserved LLM results and performs no model inference:

```powershell
python -m src.v1_1_reproduce
```

The command creates a new timestamped directory under `output/` and writes a
machine-readable `verification-report.json`; it never overwrites
`research/v1.1/`. To verify/download the frozen CTU-13 text flows and replay the
large deterministic sources, use explicit options:

```powershell
python -m src.v1_1_reproduce --download-ctu13 --run-ctu13 --run-second-dataset
```

On Windows the command refuses data and output roots on `C:`. Confirmatory
holdout and LLM calls are intentionally not rerun by this release verifier;
their frozen manifests, raw outputs and validation tests are checked instead.

```sh
python -m pip install --requirement requirements.txt --requirement requirements-dev.txt
ruff check .
ruff format --check .
python -m unittest discover -s tests -p "test_*.py" -v
python src/nmap_to_zabbix.py --input examples/nmap/synthetic-enterprise.xml --output-dir output/reproduction
python -m src.v2_experiment --output-dir output/v2
```

Expected artifacts are `network-review.md`, `network-review.json` and `dashboard.html`. Timestamps make byte-for-byte comparison inappropriate; compare structure, counts and finding semantics.

The V2 command additionally produces `benchmark.md` and `benchmark.json`.
Its committed fixtures execute no network activity or malware. To enable the
optional local advisor, append `--ollama-model MODEL_NAME`; the model must
already be installed in a loopback Ollama instance. See the
[V2 protocol](V2_RESEARCH_PROTOCOL.md) before interpreting its metrics.

After acquiring and verifying the frozen CTU-13 text flows, the V1.1
retrospective detector diagnostics can be generated entirely on `E:`:

```powershell
python -m src.ctu13_acquire --data-dir E:\tcc\data\ctu13 --download
python -m src.ctu13_analysis --data-dir E:\tcc\data\ctu13 --output-dir E:\tcc\output\v1.1-ctu13-analysis --window-seconds 60 300 600
```

Scenario 12 is an inspected historical holdout in this diagnostic command; the
output must not be described as a new confirmatory holdout result.

For the protocol comparison, run both configurations with the same model and
manifest. The repetition runner preserves every per-run JSON response and
creates aggregate `summary.json` and `summary.md` files. Promote completed runs
from the ignored `output/` tree into versionable research evidence with hashes:

```powershell
python -m src.v2_repetitions --ollama-model llama3.2:3b --ollama-protocol grounded --repetitions 10 --output-dir output/v2-grounded-10
python -m src.v2_repetitions --ollama-model llama3.2:3b --ollama-protocol historical --repetitions 10 --output-dir output/v2-historical-10
python -m src.result_preservation output/v2-grounded-10 research/v2/results/grounded-3b-10 --execution-source-state retrospective
python -m src.result_preservation output/v2-historical-10 research/v2/results/historical-3b-10 --execution-source-state exact
```

Use `retrospective` only when the exact source snapshot was not captured at
launch. New frozen runs must use `exact` and must not be followed by source-code
changes before preservation. The preservation command refuses to overwrite an
existing evidence directory.

Use the separate adversarial manifest for prompt-injection resilience and do
not merge its detector counts into the frozen Phase-A functional benchmark:

```powershell
python -m src.v2_repetitions --manifest research/v2/adversarial-scenarios.json --ollama-model llama3.2:3b --ollama-protocol grounded --repetitions 10 --output-dir output/v2-adversarial-10
python -m src.result_preservation output/v2-adversarial-10 research/v2/results/adversarial-3b-10 --execution-source-state exact
python -m src.phase_c_analysis
python -m src.article_tables
```

## Document verification

The approved monograph is verified as an immutable archival file:

```text
academic/monografia/monografia-aprovada-2025.pdf
SHA-256: DCACE3DBCFC0B6FDD6E549B686AD76DA1C9072933DE1579E37BDF8430BCCD898
```

Generate the tables from the repository root, then compile the refinable
article from `academic/artigo/`:

```sh
python -m src.article_tables
cd academic/artigo
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Run the table generator from the repository root, or pass the repository root
explicitly. The official monograph contains 27 pages and must not change. The
V1.0 contains 12 pages. V1.1 pagination can change under the IEEE development
class and again when the selected periodical's exact template is applied.

## Data policy

Only synthetic fixtures belong in Git. Real scan XML and generated reports must remain in controlled storage. The repository-wide `.gitignore` blocks XML by default and explicitly allows only files under `examples/` and `tests/fixtures/`.
