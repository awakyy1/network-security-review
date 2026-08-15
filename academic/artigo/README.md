# Scientific article

[`main.tex`](main.tex) is the English, one-column post-approval research
article derived from the undergraduate project. It does not alter the approved
monograph. Its claims, negative result, and limitations follow the frozen V2
protocol and preserved evidence in `research/v2/results/`.

The current source is **V1.1** and uses a sober, one-column IEEE-based preprint
(`IEEEtran`) baseline. V1.0 and V1.1 remain preserved as named PDF snapshots
under [`releases/`](releases/). The current identifier is kept in
[`VERSION`](VERSION), and [`main.pdf`](main.pdf) is the verified V1.1 build.

Generate the result tables from the repository root before compiling:

```sh
python -m src.article_tables
```

The files under [`generated/`](generated/) are projections of preserved
JSON results and should not be edited manually.

```sh
latexmk -pdf main.tex
```

Without `latexmk`, run `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.

Tectonic can build the audited PDF with `tectonic -X compile main.tex`.
The IEEE-based layout is a presentation and quality baseline only; no venue
submission is planned or implied.

The complete V1.1 requirements and release gates are tracked in
[`../../docs/V1_1_RESEARCH_PLAN.md`](../../docs/V1_1_RESEARCH_PLAN.md).

If the scope ever changes to publication submission, that later version must
add confirmed author metadata and follow the chosen venue's current rules. The
2025 academic approval date is not a journal acceptance date.
