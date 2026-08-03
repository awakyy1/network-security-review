# Reproducibility

## Reproduction levels

| Level | Available | Procedure |
|---|---|---|
| Static inspection | Yes | Review source, tests, commit history and academic documents |
| Deterministic unit tests | Yes | Run the standard-library test suite |
| Synthetic end-to-end report generation | Yes | Process `examples/nmap/synthetic-enterprise.xml` |
| Original 2025 experiment | Partial | Scenario totals are documented, but complete raw evidence was not preserved |
| LLM evaluation | No | Exact prompts, model/hardware state, outputs and independent ratings are incomplete |

## Environment

- Python 3.10 or newer;
- dependencies pinned in `requirements.txt`;
- no live Nmap or Zabbix instance required for unit tests;
- XeLaTeX, BibTeX, Arial and `abntex2` required for academic PDFs.

## Software verification

```sh
python -m pip install --requirement requirements.txt --requirement requirements-dev.txt
ruff check .
python -m unittest discover -s tests -p "test_*.py" -v
python src/nmap_to_zabbix.py --input examples/nmap/synthetic-enterprise.xml --output-dir output/reproduction
```

Expected artifacts are `network-review.md`, `network-review.json` and `dashboard.html`. Timestamps make byte-for-byte comparison inappropriate; compare structure, counts and finding semantics.

## Document verification

The approved monograph is verified as an immutable archival file:

```text
academic/monografia/monografia-aprovada-2025.pdf
SHA-256: DCACE3DBCFC0B6FDD6E549B686AD76DA1C9072933DE1579E37BDF8430BCCD898
```

To compile the refinable article, run the following from `academic/artigo/`:

```sh
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

The official monograph contains 27 pages and must not change. The current article contains 9 pages; its pagination can change when a journal template is applied.

## Data policy

Only synthetic fixtures belong in Git. Real scan XML and generated reports must remain in controlled storage. The repository-wide `.gitignore` blocks XML by default and explicitly allows only files under `examples/` and `tests/fixtures/`.
