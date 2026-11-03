# Scientific article

[`main.tex`](main.tex) is the English, one-column post-approval research
article derived from the undergraduate project. It does not alter the approved
monograph. Its experiments follow the preserved V2 and V1.1 protocols and
evidence in `research/v2/results/` and `research/v1.1/`.

The current source is **V1.2-dev**, an editorial revision of the preserved V1.1
evidence, and uses a sober, one-column IEEE-based preprint
(`IEEEtran`) baseline. V1.0 and V1.1 remain preserved as named PDF snapshots
under [`releases/`](releases/). The current identifier is kept in
[`VERSION`](VERSION). The working [`main.pdf`](main.pdf) now includes the
2026-11-02 editorial and figure revision of that evidence. It is not byte-identical
to the frozen V1.1 release snapshot. V1.2-dev is a working manuscript, not a new
experimental result or a frozen release.

The editorial revision clarifies the contribution, distinguishes validator
acceptance from correctness, removes unsupported cross-family improvement
language, and makes unmeasured analyst benefit explicit. All reported results,
protocol records, released PDFs, and the approved monograph remain unchanged.
See [`EDITORIAL_REVISION.md`](EDITORIAL_REVISION.md) for the scope.

Generate the result tables from the repository root before compiling:

```sh
python -m src.article_tables
python -m src.article_figures
```

The quantitative tables and figures under [`generated/`](generated/) are
projections of preserved JSON results; the two architecture/evaluation diagrams
describe the declared design. Edit the generators rather than these exports.

```sh
latexmk -pdf main.tex
```

Without `latexmk`, run `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.

Tectonic can build the working PDF with `tectonic -X compile main.tex`.
The IEEE-based layout is a presentation and quality baseline only; no venue
submission is planned or implied.

The complete V1.1 requirements and release gates are tracked in
[`../../docs/V1_1_RESEARCH_PLAN.md`](../../docs/V1_1_RESEARCH_PLAN.md).

If the scope ever changes to publication submission, that later version must
add confirmed author metadata and follow the chosen venue's current rules. The
2025 academic approval date is not a journal acceptance date.
