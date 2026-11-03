# Editorial and figure revision — 2026-11-02

This working revision uses the existing V1.1 evidence. It does not introduce
new experiments, alter results, or supersede the named release snapshots.

## Argument and interpretation

- Reframe the contribution around auditable integration and observed failure
  modes, rather than a demonstrated improvement in security or analyst work.
- Clarify the research-question wording around the measurements actually
  reported; preserve the original experimental protocols and records.
- Define acceptance as passing the implemented output contract, not independent
  confirmation of semantic correctness or compromise.
- State that historical NSIS.ay and prospective DonBot results use different
  families and do not estimate a causal threshold-selection improvement.
- Delimit the historical grounded/free-text comparison: instructions, format,
  and decoding differ; exact-ID retention is not an analyst-benefit measure.
- Discuss complex-output generation caps without attributing all failures to
  truncation: complete uncapped Llama outputs still chose inapplicable controls.
- State the absence of a deterministic-report baseline and blinded analyst-task
  outcomes; keep these as unmeasured questions.
- Interpret response-policy counts as source-window exposure under dataset
  labels, not unique disrupted hosts or observed business harm.
- Scope response restrictions to this artifact and its evidence.
- Identify dependence between source-windows as an interval-interpretation limit.

## Visual presentation

- Replace rounded block diagrams with a restrained vector architecture schematic
  and a tabular evaluation map that does not imply sequential evidence flow.
- Use direct labels and point plots for metrics and historical traceability;
  retain every numerical value and distinguish protocol/evaluation roles.
- Standardize typography, thin rules, line styles, and grayscale contrast.
- Reflow the environment table into wrapped comparison columns, avoiding the
  previous whole-table shrinkage.

## Preservation boundary

Do not modify `research/`, the approved monograph, or PDFs under `releases/`
to make this revision appear to have been part of a frozen experiment.
`VERSION` is 1.2-dev to distinguish the revised working manuscript from the
frozen V1.1 snapshot, following the document policy. No new experimental result
or frozen release is declared. The original V1.1 PDF remains under `releases/`.

## Working-build verification

- All 84 existing unit tests passed; Ruff lint and generator formatting passed.
- Tectonic compiled the revised manuscript without LaTeX warnings, missing
  references, missing characters, or overflowing boxes.
- The 18-page PDF contains the original 16 result tables and five redesigned
  figures. Every page was rendered and visually inspected.
- No text span extends outside a page; no nontrivial text span is below 7.5 pt.
- Only the environment table's layout changed; other generated result tables
  remain byte-identical to their prior versions.
- Frozen research records, release snapshots, and the approved monograph were
  checked for changes and remain intact. No model inference was run.
