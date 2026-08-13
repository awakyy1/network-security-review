# V2 Run 01 environment record

Execution date: 2026-08-03 (America/Sao_Paulo)

## Code and runtime

- repository base commit: `5d93faca99803f5b1a913d422bb86b58404db255`;
- V2 code state: local, uncommitted research changes subsequently preserved in
  the same handoff set;
- operating system: Windows 11, build 26200, 64-bit;
- Python: 3.12.10;
- Requests: 2.34.2;
- Ollama: 0.32.5;
- model tag: `llama3.2:3b`;
- Ollama model-list ID: `a80c4f17acd5`;
- model blob SHA-256 reported by `ollama show --modelfile`:
  `dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff`.

## Hardware

- CPU: Intel Core i5-1335U;
- logical processors: 12;
- installed RAM observed before execution: approximately 15.7 GiB;
- graphics: Intel Iris Xe, approximately 2 GiB reported adapter memory;
- Ollama placement: 100% CPU for this model and context.

## Fixed generation parameters

- context length: 4096 tokens;
- maximum output: 700 tokens;
- temperature: 0;
- seed: 42;
- timeout: 300 seconds per request;
- endpoint: loopback Ollama API;
- response format: closed JSON schema version 1.0.

## Preserved output hashes

- `phase-a-ollama-3b-run-01.json`:
  `A7B78649B97B5E01F85D6F59A3F1B6369BA278A7064F22897394BF70409A5A78`;
- `adversarial-ollama-3b-run-01.json`:
  `00B26C770954D8C429871ABB51A5BEF3D970F94754A3C13778A7E1A79A5BE529`.

Each JSON record also contains input hashes, event-file hashes, prompt hashes,
token counts and per-call latency. The Phase-A run made five model calls and
the adversarial run made one. These are single-run observations and must not be
reported as stable model performance until the planned repetitions are made.
