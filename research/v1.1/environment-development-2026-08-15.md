# V1.1 development environment

Observation date: 2026-08-15 (America/Sao_Paulo)

This is a development-environment record, not a confirmatory run record. No
V1.1 detector test, model call or experiment had been executed when it was
created.

## V1.0 and V1.1 hardware context

| Research state | Operating system | CPU | Memory | Graphics / inference |
|---|---|---|---:|---|
| V1.0 initial run, 2026-08-03 | Windows 11, build 26200 | Intel Core i5-1335U, 12 logical processors | approximately 15.7 GiB | Intel Iris Xe; `llama3.2:3b` ran 100% on CPU |
| V1.0 confirmatory repetitions, 2026-08-13 | Debian GNU/Linux, kernel 6.12.101 | Intel Core i5-1335U, 10 cores / 12 logical processors | 16,486,330,368 bytes plus 13,211,004,928 bytes swap | CPU inference |
| V1.1 development machine | Windows 10 Pro 22H2, build 19045 | AMD Ryzen 5 5600, 6 cores / 12 logical processors | approximately 31.9 GiB | NVIDIA GeForce RTX 3060, 12,288 MiB VRAM, driver 581.80 |

The V1.0 rows are transcribed from the preserved
`research/v2/results/environment-run-01.md` and
`research/v2/results/environment-confirmatory-2026-08-13.md` records. The V1.1
row was collected from Windows system inventory and `nvidia-smi`.

Differences in latency between V1.0 and V1.1 would confound CPU/GPU placement,
memory, operating system, driver, Ollama version and potentially model runtime.
Cross-machine latency is descriptive environment context only. It must not be
used as a causal protocol-speed comparison. Comparisons intended to isolate a
model or protocol effect must run on the same frozen V1.1 environment.

## Runtime preparation

- Python: 3.12.10;
- Python base location: `E:\Programs\Python312`;
- Python executable SHA-256:
  `4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a`;
- virtual environment: `E:\tcc\.venv`;
- dependency check after migration: no broken requirements;
- Ollama standalone client: 0.32.13;
- Ollama executable: `E:\Ollama\App\ollama.exe`;
- Ollama executable SHA-256:
  `bb2e912cdd9e78107793fa94471e40d1054550e54ee00532f43f953081ba7f79`;
- Ollama distribution ZIP SHA-256:
  `20d61a8075038694f5b6db1e937551dbc79d470e85217003facf6ecaac394258`;
- model storage: `E:\Ollama\Models` through the user `OLLAMA_MODELS`
  environment variable;
- locally available models: none at observation time;
- Ollama server: not started at observation time.

## Storage boundary

New runtimes, virtual environments, datasets, model blobs, caches, temporary
files and raw results for V1.1 must use `E:` or another explicitly selected
non-system drive. Commands that may create large temporary files must override
their cache and temporary directories rather than relying on the Windows
system-drive defaults.
