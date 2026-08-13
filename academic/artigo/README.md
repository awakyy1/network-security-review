# Scientific article

[`main.tex`](main.tex) is the English, single-column post-approval research
article derived from the undergraduate project. It does not alter the approved
monograph. Its claims, negative result, and limitations follow the frozen V2
protocol and preserved evidence in `research/v2/results/`.

The current article is **V1.0**, frozen on 2026-08-13. Its identifier is kept in
[`VERSION`](VERSION), printed in the document and embedded in the PDF metadata.
The named PDF snapshot under [`releases/`](releases/) remains the V1 record when
`main.tex` is later advanced to another version.

Generate the result tables from the repository root before compiling:

```sh
python -m src.article_tables
```

The six files under [`generated/`](generated/) are projections of preserved
JSON results and should not be edited manually.

```sh
latexmk -xelatex main.tex
```

Without `latexmk`, run `xelatex`, `bibtex`, `xelatex`, `xelatex`. XeLaTeX is required for Arial.

On Linux hosts without Arial, `main.tex` explicitly falls back to Liberation
Sans and Liberation Mono. Tectonic can build the audited working PDF with
`tectonic -X compile main.tex`; use the Arial/XeLaTeX submission environment
for the final journal-formatted artifact.

Before submitting to a journal, add the authors' contact details and adapt the document to the journal's template, page limit and real submission/acceptance metadata. The academic approval date is not a journal acceptance date.
