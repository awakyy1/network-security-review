# V1.1 verification records

- `v1-baseline-2026-08-15.json` records the frozen V1.0 deterministic baseline.
- `full-reproduction-2026-08-15.json` records ten successful commands: tests,
  lint, format check, inert functional executions, table/figure regeneration,
  and PDF compilation. It performed no LLM inference.
- `external-reproduction-2026-08-15.json` records the deterministic CTU-13
  retrospective and second-dataset replays. Excluding timestamps, runtime, and
  expected scientific-source hashes changed by the V1.1 code revision, CTU-13
  analytical output was unchanged; the second-dataset output matched the
  preserved result exactly.
- `final-candidate-2026-08-15.json` records the final pre-commit verification:
  84 tests and 6 subtests, Ruff lint/format checks, deterministic fixture and
  endpoint runs, regenerated tables/figures, and the final PDF build. It
  performed no LLM inference.
- `one-column-final-2026-08-15.json` records the same complete verification
  after the final one-column and neutral-palette presentation pass. It also
  performed no LLM inference.
- `clean-title-final-2026-08-15.json` records the final verification after
  removing editorial workflow language from the visible author block and PDF
  metadata. It performed no LLM inference.
- `grounded-layout-final-2026-08-15.json` records the complete reproduction
  after the grayscale figure redesign, compact table pass, prose review, and
  final bibliography correction. It performed no LLM inference.
- `release-final-2026-08-15.json` records the ten-command release reproduction
  used to freeze the named V1.1 PDF. It performed no LLM inference.

The final V1.1 PDF produced by the grounded-layout run has
SHA-256
`36cc38f3f32add6830da88ca55702c299b3b24af2f45c838ea8053ee12918ba1`.
The earlier full-reproduction report retains its own historical PDF hash.
The frozen V1.0 PDF and approved monograph hashes were independently rechecked
against their release records.
