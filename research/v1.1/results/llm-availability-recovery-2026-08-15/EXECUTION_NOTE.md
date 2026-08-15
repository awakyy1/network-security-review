# V1.1 Qwen availability-recovery execution note

The primary matrix remains immutable at 145 API responses in 180 attempts and
73 validator-accepted outputs. This recovery was created only because the
prospectively defined first-repetition human sample contained missing response
bodies.

## First recovery attempt

The frozen four-call recovery attempted the four
`qwen3:8b/checklist-v1/run-001` finding-bearing scenarios. All four calls
returned HTTP 500 and no response body. The failed benchmark SHA-256 is
`d3fe996b589263d6ff5905081c64c91161dc87d2eecdd8afcd5b3199e11bf1de`;
its summary SHA-256 is
`538f3117486a4fcf760b74eee0b14bb22f2956363a2a17249aeba43f9e6c3ab4`.

The contemporaneous Ollama log reported `cudaMalloc failed: out of memory`
while allocating the Qwen model buffer. Read-only process inspection identified
two `E:\Ollama\App\lib\ollama\llama-server.exe` processes (PIDs 8432 and
31064) created at 17:32 and 17:39. Both referenced models in
`E:\Ollama\Models`, both named absent parent PID 33780, and one retained about
5.7 GiB of working set. Before cleanup, NVIDIA telemetry reported 7,088 MiB
used/5,028 MiB free and Windows reported 3.64 GiB free physical memory.

Only those two verified orphaned processes were terminated. No editor, Codex,
browser or unrelated process was stopped. After cleanup, NVIDIA telemetry
reported 2,731 MiB used/9,385 MiB free and Windows reported 12.36 GiB free
physical memory.

## Declared retry

The cleanup and one-retry limit were frozen in
`llm-availability-recovery-retry1-2026-08-15.json` before the retry. The retry
received 4/4 response bodies: one passed the full validator and three were
preserved validation failures. The retry benchmark SHA-256 is
`370b8a169ebfd7168e0da57b1c0153af99690f423a7e393d622cd97e590b423d`;
the summary SHA-256 is
`c96ec52c112d8932785dd093e0141bb9fc00e8b3452af00cc19525459ece2c73`.

This diagnosis applies to the recovery attempt. Because the primary-run server
log was not preserved, it must not be retroactively asserted as the cause of
the original 35 primary availability failures.
