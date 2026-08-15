# Academic document policy

## Approved monograph

The monograph approved on 19 November 2025 is an immutable historical artifact. The repository publishes the original PDF byte for byte and does not present any post-defense rewrite as the submitted work.

- Path: `academic/monografia/monografia-aprovada-2025.pdf`
- Pages: 27
- SHA-256: `DCACE3DBCFC0B6FDD6E549B686AD76DA1C9072933DE1579E37BDF8430BCCD898`

Any local post-defense review material is kept outside Git in `.review/` and has no official academic status.

## Scientific article

The English article is a derivative research output. It may be refined to improve scientific method, evidence boundaries, reproducibility, citations, limitations and journal compliance. Refinements must:

- preserve traceability to the approved thesis and repository commits;
- distinguish reported historical results from newly reproduced results;
- avoid unsupported accuracy, scalability or exploitability claims;
- identify the thesis approval date as academic history, not journal acceptance;
- use a declared international presentation baseline without implying
  submission or peer review;
- use a sober one-column presentation with a grayscale palette and avoid em or
  en dashes in prose, citations, references, and generated tables.

V1.1 uses the international IEEE article structure and a one-column
`IEEEtran`-based preprint only as its development quality baseline. The
repository owner has no
publication submission planned for this version. UniOpet/ABNT formatting
applies only to the historical approved monograph, not to the derivative V1.1
article.

The article never replaces or retroactively modifies the approved monograph.

### Article versioning

- V1.0 was frozen on 13 August 2026 and is identified by its named PDF,
  release record, `article-v1` branch and `article-v1.0` tag;
- the V1.0 snapshot is `academic/artigo/releases/article-v1.pdf`;
- the V1.1 snapshot is `academic/artigo/releases/article-v1.1.pdf`;
- `academic/artigo/main.pdf` is the working build of the version declared in
  `VERSION`;
- `academic/artigo/VERSION` identifies the active working source and may carry
  a development suffix before the next named snapshot is frozen;
- later scientific changes must increment the version, create a new named PDF
  snapshot and retain earlier snapshots and Git history;
- a version label records an internal research-artifact state and does not
  imply journal submission, peer review or acceptance.

## Copyright boundary

All files under `academic/` are excluded from the repository's MIT License and
remain all rights reserved. The complete terms are stated in
`academic/LICENSE.md`; citation does not itself grant reuse rights.
