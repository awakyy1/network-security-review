# V2 V1 release scope

Prepared on 2026-08-13. This checklist defines the reviewed content of the
article V1 commit and remains useful for later version comparisons.

## V1 commit

Suggested message:

```text
Complete V2 validation and evidence-grounded article
```

The V1 scope includes the implementation and tests under `src/` and `tests/`, the frozen
protocol and safe manifests under `research/v2/`, all reviewed evidence under
`research/v2/results/`, the article source/generated tables/PDF, and the V2
documentation and repository metadata already modified for this study.

Before publishing this branch or any later version, review `git diff`, verify
that no raw production telemetry or real scan XML is present, and repeat:

```sh
python -m src.phase_c_analysis
python -m src.article_tables
ruff check .
ruff format --check .
python -m unittest discover -s tests -p "test_*.py" -v
sha256sum academic/monografia/monografia-aprovada-2025.pdf
```

Expected immutable monograph SHA-256:
`dcace3dbcfc0b6fdd6e549b686ad76da1c9072933de1579e37bdf8430bccd898`.

Explicitly exclude ignored execution scratch data under `output/`, local model
files, external CTU-13 source files, credentials and editor/OS artifacts.
