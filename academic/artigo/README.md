# Scientific article

[`main.tex`](main.tex) is the English, single-column scientific article derived from the undergraduate thesis. Its scope, results and limitations follow the audited evidence boundary documented in the repository.

```sh
latexmk -xelatex main.tex
```

Without `latexmk`, run `xelatex`, `bibtex`, `xelatex`, `xelatex`. XeLaTeX is required for Arial.

Before submitting to a journal, add the authors' contact details and adapt the document to the journal's template, page limit and real submission/acceptance metadata. The academic approval date is not a journal acceptance date.
