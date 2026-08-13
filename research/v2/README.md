# V2 research laboratory

This directory contains a safe, reproducible laboratory for the post-defense
research article. It studies **observable network and endpoint behaviors**, not
malware-family signatures.

## Safety boundary

- no malware binary, exploit, persistence mechanism or destructive payload is
  present or downloaded;
- fixtures are inert JSON Lines records generated for documentation-range
  addresses and `.test` domains;
- no fixture causes a network connection, changes the operating system or
  applies a firewall rule;
- every result is a `behavior-review` item with
  `confirmed_malware=false` and `automatic_response_authorized=false`;
- any containment proposal requires independent validation and human approval.

The scenarios model four behavior classes documented by MITRE ATT&CK:
application-layer command-and-control patterns (T1071), network service
discovery (T1046), asymmetric egress for review (T1041), and a network download
followed by file creation (T1105).

## Scenarios

| ID | Class | Purpose |
|---|---|---|
| `benign-web` | Benign | Irregular ordinary connections; expected negative |
| `benign-updater` | Benign hard negative | Regular update polling; intentionally challenges beaconing heuristics |
| `emulated-beacon` | Benign emulation | Periodic outbound connection pattern |
| `emulated-service-discovery` | Benign emulation | Rapid connections to multiple services |
| `emulated-asymmetric-egress` | Benign emulation | Large sent/received byte asymmetry |
| `emulated-tool-transfer` | Benign emulation | Download telemetry followed by inert `.bin` metadata |

Labels live in [`scenarios.json`](scenarios.json), separately from event files.
This avoids exposing expected labels to the detector or Ollama prompt.

The separate [`adversarial-scenarios.json`](adversarial-scenarios.json) manifest
contains a prompt-injection resilience case. Its process field is deliberately
prompt-like, but remains inert evidence data. Keeping this case separate avoids
changing the frozen six-scenario functional benchmark.

## Execution

From the repository root:

```sh
python -m src.v2_experiment --output-dir output/v2
```

Run the isolated adversarial case with:

```sh
python -m src.v2_experiment --manifest research/v2/adversarial-scenarios.json --output-dir output/v2-adversarial
```

To evaluate an already installed local Ollama model:

```sh
python -m src.v2_experiment --ollama-model MODEL_NAME --output-dir output/v2-ollama
```

The reconstructed free-text control is selected explicitly:

```sh
python -m src.v2_experiment --ollama-model MODEL_NAME --ollama-protocol historical --output-dir output/v2-historical
```

Final model evaluation used `python -m src.v2_repetitions` with ten
repetitions per protocol and ten repetitions of the separate adversarial
fixture. See
[`docs/REPRODUCIBILITY.md`](../../docs/REPRODUCIBILITY.md) for the frozen
commands.

The Ollama endpoint is restricted to the loopback interface. Its response must
match a JSON schema, cite committed evidence IDs, avoid unsupported CVEs and
remain within a fixed catalog of human-approved control proposals.

Reviewed synthetic-only executions that are suitable for version control are
indexed in [`results/README.md`](results/README.md). Generated files under
`output/` remain local and ignored.

## Interpretation

The committed benchmark is a functional and construct-validity test. It cannot
support a claim of real-world malware-detection accuracy because its fixtures
are synthetic and known to the authors. The completed external-validation phase
uses independently labeled CTU-13 flow records, preserves provenance and hashes,
and reports the family-separated result independently. Its negative holdout
result is retained rather than combined with the synthetic score.
