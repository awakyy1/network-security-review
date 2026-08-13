# Confirmatory repetition environment

Execution date: 2026-08-13 (America/Sao_Paulo)

## Scope and code state

- repository base commit: `5d93faca99803f5b1a913d422bb86b58404db255`;
- V2 research state: local and uncommitted;
- exact per-file source, dependency, manifest and fixture hashes are generated
  by `src.result_preservation` immediately after each new run;
- the source tree must not be changed between launch and preservation;
- grounded repetitions from 2026-08-03 have retrospective source provenance;
- historical repetitions launched from this state use exact source provenance.

Key pre-launch hashes:

| Artifact | SHA-256 |
|---|---|
| `research/v2/scenarios.json` | `260a470889db54a8a317492d08a9f8bf69cfbb5c247500de025e6bb75a0958a6` |
| `examples/nmap/synthetic-enterprise.xml` | `a7d083fbe22e3f415765a66df95e9c63441189f9481b269fa810aa4e71472762` |
| `src/ollama_baseline.py` | `9cb919df3b739ce8cd2a15cc7db094aca3d003d59d4ae5e62462f188dab1e909` |
| `src/v2_experiment.py` | `72813b72e91ea6825c67528b6ce26a89445c54c819e189e058591d377ea01cb5` |
| `src/v2_repetitions.py` | `6e2f95ded958327b2ae24bb4e3ddee4a9d49ce1c1f32d193fc1a512c63e3b433` |
| `src/result_preservation.py` | `437b36e6c7682a12d9634fe33e47dc4f9157be85d17900226180e877b3c6fedb` |

## Runtime and hardware

- operating system: Debian GNU/Linux, kernel
  `6.12.101+deb13-amd64`, x86-64;
- Python: 3.13.5;
- Requests: 2.32.3;
- CPU: 13th Gen Intel Core i5-1335U, 10 cores, 12 logical processors;
- installed RAM: 16,486,330,368 bytes;
- configured swap: 13,211,004,928 bytes;
- inference device: CPU; `ollama ps` is captured while the model is loaded.

## Ollama model identity

- Ollama client/server version: 0.32.6;
- model tag: `llama3.2:3b`;
- model-list ID: `a80c4f17acd5`;
- architecture and size: Llama 3.2B, Q4_K_M;
- model blob SHA-256 reported by `ollama show --modelfile`:
  `dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff`.

## Frozen historical protocol command

```sh
python3 -m src.v2_repetitions \
  --ollama-model llama3.2:3b \
  --ollama-protocol historical \
  --repetitions 10 \
  --ollama-context 4096 \
  --ollama-timeout 300 \
  --ollama-max-output-tokens 512 \
  --output-dir output/v2-historical-10
```

The reconstructed historical protocol uses temperature 0.7, `top_p` 0.9, no
system prompt and no output schema. It receives the same Phase-A evidence pack
as the grounded protocol. The added context, timeout and output ceiling are
reproducibility bounds, so this is not a byte-exact replay of the 2025 system.
