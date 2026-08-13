# CTU-13 external validation

## Purpose and boundary

This evaluation tests whether the frozen transparent behavior rules generalize
from the inert laboratory fixtures to independently labeled network flows. It
does not execute or acquire malware, classify malware families, inspect packet
payloads, prove compromise or measure real containment effectiveness.

Only the publisher-recommended bidirectional `.binetflow` text files were
acquired. Executables, ZIP archives, `.pcap`, `.biargus` and packet payloads are
blocked by the acquisition code. Raw external data remains under the ignored
`data/` directory and is not published in the repository.

## Frozen data selection

Selection was frozen before complete-label inspection. Scenario 5/Virut is the
development source; scenario 12/NSIS.ay is the family-separated holdout.

| Role | Scenario | Family | File | Bytes | SHA-256 |
|---|---:|---|---|---:|---|
| Development | 5 | Virut | `capture20110815-2.binetflow` | 17,766,203 | `ef5c9ed6895d4ca5aec723449dae30054ccd1f6b091713a52ffcb681ff78a02c` |
| Holdout | 12 | NSIS.ay | `capture20110819.binetflow` | 44,718,958 | `1098f0addacedc321c7baefad63ef0d9a0f26630d0155087d37e8da770dd9f2e` |

The exact URLs, HTTP metadata, label policy and hashes are in
[`research/v2/ctu13_manifest.json`](../research/v2/ctu13_manifest.json). The
publisher describes CTU-13 as thirteen scenarios mixing botnet, normal and
background traffic, recommends the detailed bidirectional flows, and publishes
the dataset under CC BY:

- [official CTU-13 dataset page](https://www.stratosphereips.org/datasets-ctu13);
- [official dataset overview and license](https://www.stratosphereips.org/datasets-overview);
- [scenario 5 provenance](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-46/);
- [scenario 12 provenance](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-53/).

## Unit of analysis and labels

The unit is an anonymized source host in a non-overlapping five-minute window,
based on flow start time. Addresses are irreversibly replaced with stable
scenario-local SHA-256 tokens before detector execution. Labels are retained
outside the detector input.

- positive: source flows whose label starts with `From-Botnet`;
- negative: source flows whose label starts with `From-Normal`;
- excluded: `Background`, `From-Background` and every `To-*` label.

This follows the publisher's warning that `To-Botnet` means traffic sent by an
unknown computer and is not malicious per se. Background traffic is also not a
verified normal class. Mixed-truth host windows would be excluded and counted;
none occurred in the frozen sources.

The flow adapter maps source bytes and reverse bytes to normalized connection
events. No process identity exists in NetFlow, so every event explicitly uses
`network-flow-no-process-context`. Only `BEH-001` through `BEH-003` can be
tested. `BEH-004` needs endpoint file-creation telemetry and is not evaluated.

## Results

| Role | Units | TP | FP | FN | TN | Precision | Recall | F1 | Specificity | MCC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Development | 31 | 5 | 17 | 0 | 9 | 0.227 | 1.000 | 0.370 | 0.346 | 0.280 |
| Holdout | 108 | 16 | 32 | 37 | 23 | 0.333 | 0.302 | 0.317 | 0.418 | -0.282 |

Wilson 95% intervals are wide. Development precision is 0.101--0.434, recall
0.566--1.000 and specificity 0.194--0.538. Holdout precision is 0.217--0.475,
recall 0.195--0.435 and specificity 0.297--0.550. The negative holdout MCC is
evidence against reliable generalization in this setup.

The files contained 129,832 development rows and 325,471 holdout rows. Clean
binary scoring retained 5,558 and 9,755 rows respectively; most discarded rows
were publisher-labeled background or inbound/ambiguous traffic. Processing the
two files took approximately 14.4 and 37.9 seconds, with less than 1.3 MiB peak
Python memory traced by the streaming evaluator.

## Error analysis

| Rule | Development botnet/normal findings | Holdout botnet/normal findings |
|---|---:|---:|
| `BEH-001` periodic communication | 1 / 7 | 0 / 15 |
| `BEH-002` rapid distinct endpoints | 5 / 17 | 16 / 32 |
| `BEH-003` asymmetric egress | 0 / 0 | 0 / 0 |

Rapid distinct destinations and periodic connections were common in verified
normal traffic. The holdout lost 37 of 53 botnet-origin windows, while 32 of 55
normal-origin windows alerted. This supports a concrete systems-security
conclusion: network-flow timing alone lacks the process ownership, file lineage
and execution context needed to distinguish routine applications from
malware-like behavior.

## Defensive-response interpretation

The implementation executed zero automatic actions. If every alert had caused
a block, 17 of 22 development actions (77.3%) and 32 of 48 holdout actions
(66.7%) would have targeted verified normal-origin windows. At the same time,
37 holdout botnet-origin windows would remain unaddressed.

Therefore, the evaluated rules are suitable only for producing review
candidates. The system can help an analyst preserve evidence, correlate an
alert with an authorized asset inventory and request endpoint context. It
cannot responsibly claim malware prevention from these observations, and it
must not block, isolate or quarantine without independent confirmation and a
human-authorized response procedure.

## Reproduction

```powershell
python -m src.ctu13_acquire --download
python -m src.ctu13_acquire
python -m src.ctu13_experiment --output-dir output/ctu13-frozen-v1
```

The preserved aggregate and anonymized unit results are indexed under
[`research/v2/results/`](../research/v2/results/README.md). Development and
holdout metrics must remain separate; thresholds must not be changed and then
re-reported against this already inspected holdout as if it were untouched.
