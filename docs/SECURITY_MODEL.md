# Security Model and Finding Semantics

## What the tool can state

The parser can state that an Nmap document reported a live host, an open port, a service name, and optional product or version text. A review rule can explain why that observed exposure deserves manual validation.

## What the tool cannot state

The tool cannot determine internet exposure from a scan alone, verify authentication policy, prove traffic contents, confirm a product fingerprint, establish exploitability, or demonstrate compliance. It does not map CVEs because reliable mapping requires normalized product identity, affected-version evaluation, source freshness, and often configuration context.

## Severity meaning

Severity ranks review urgency, not CVSS or confirmed technical impact:

- `high`: cleartext administrative access observed.
- `medium`: remote access, file sharing, or database exposure requiring contextual validation.
- `low`: common service hardening or encrypted-transport review.

Consumers must preserve the `confirmed_vulnerability: false` field unless another controlled assessment independently confirms a vulnerability.
