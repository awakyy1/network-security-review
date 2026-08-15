# V1.1 CTU-13 confirmatory protocol

Status: frozen before downloading or parsing the selected flow files on
2026-08-15. The original record contains a disclosed timestamp transcription
error; the machine-readable corrected selection is
`research/v1.1/ctu13-confirmatory-selection-2026-08-15-corrected.json`, with
the chronology documented in `research/v1.1/CTU13_SELECTION_ERRATUM.md`.

## Boundary

Scenario 11 (RBot) is the sole development source. Scenario 6 (DonBot) is the
sole confirmatory holdout. Their roles were selected from official dataset
metadata and HTTP headers only. Neither file had been downloaded, parsed, or
submitted to the detector when the selection record was written.

The project may inspect labels and rule features from Scenario 11 to choose one
configuration from the frozen 243-member grid. Selection maximizes development
MCC, with the tie-break order recorded in the JSON. The chosen parameters and
all development results must then be preserved before Scenario 6 is parsed.
After that freeze, no code, adapter, threshold, window, label policy, or metric
may change before the holdout run.

## Acquisition gate

Only the official `.binetflow` text files may be downloaded. Executables,
packet captures and compressed archives are prohibited. Acquisition records
the byte count, HTTP metadata and SHA-256 of each local file in a separate
manifest linked to the pre-selection record's SHA-256.

The holdout can be downloaded and hashed at acquisition time, but its content
must not be parsed before the development configuration is frozen. Downloading
bytes and computing their cryptographic digest do not expose labels to the
selection procedure.

## Primary analysis

- Unit: source host within a non-overlapping 300-second start-time window.
- Positive: a unit containing only retained `From-Botnet` source flows.
- Negative: a unit containing only retained `From-Normal` source flows.
- Excluded: background, all `To-*` labels and ambiguous/mixed units.
- Rules: BEH-001 through BEH-003; BEH-004 remains unevaluable in NetFlow.
- Primary metric: MCC; also report TP, FP, FN, TN, precision, recall, F1,
  specificity, balanced accuracy and Wilson intervals where defined.
- The final holdout is executed exactly once after the development freeze.

The older Virut/NSIS.ay files remain retrospective diagnostics and must not be
combined with the new confirmatory result as if all sources had the same role.
