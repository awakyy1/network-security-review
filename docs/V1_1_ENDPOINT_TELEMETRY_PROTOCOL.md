# V1.1 endpoint telemetry and privacy protocol

## Purpose and boundary

The endpoint schema exists to evaluate evidence lineage, especially BEH-004.
It is not an endpoint agent specification and it does not authorize collection
from a production host. V1.1 uses only synthetic, inert, repository-preserved
fixtures unless a separately approved and documented source is added.

## Normalized fields

Every event requires an opaque `event_id`, timezone-aware `timestamp`, `host`,
`event_type`, `source`, and `process`. Optional endpoint context comprises
`executable_path`, `signer`, `parent_process`, `user_context`, `command_line`,
and `file_hash_sha256`. Network observations may include destination address or
domain, port, protocol, and byte counts. File creation requires `path`; DNS
requires `destination_domain`.

The SHA-256 field is accepted only as 64 hexadecimal characters. Text fields
are capped at 1,024 characters, files at 20 MiB, and inputs at 100,000 events.
Unknown event types, duplicate evidence IDs, naive timestamps, malformed hashes
and missing type-specific fields are rejected before analysis.

## Privacy review

The schema intentionally excludes passwords, tokens, cookies, message bodies,
keystrokes, full file contents and packet payloads. User context must be a
pseudonymous laboratory role, never a personal account. Command lines in the
fixtures contain inert placeholders and no secrets. Paths and hostnames use
documentation-only namespaces or reserved addresses. Raw telemetry must remain
on the non-system research drive and access must be limited to the project.

## BEH-004 truth condition

BEH-004 fires only when the same host and process have (1) a network event with
at least the configured received-byte threshold and (2) creation of a file with
an executable-like suffix within the configured delay. This is temporal
correlation, not proof that the bytes became the file, that the file executed,
or that either artifact is malicious. Process lineage, signer, hash and user
context support analyst validation but do not alter the frozen rule.

## Inventory role

Nmap contributes asset inventory context only. It neither creates BEH-004 nor
confirms a vulnerability. A with/without-inventory comparison must therefore
measure review-context changes separately from detector predictions.
