# Security Model and Finding Semantics

## Security objective

The artifact should preserve scanner evidence without turning incomplete observations into unsupported vulnerability claims. It is a review aid, not an exploitation framework or compliance authority.

## Finding states

| State | Meaning | Supported by this tool |
|---|---|---|
| Observation | Nmap reported a host, port or fingerprint | Yes |
| Review finding | A transparent rule explains why the observation deserves validation | Yes |
| Confirmed vulnerability | Independent evidence establishes an actual weakness and context | No |
| Remediation action | An authorized change is approved, executed and audited | No |

Consumers must preserve `confirmed_vulnerability: false` unless a separate controlled assessment supplies independent confirmation.

## Severity semantics

Severity ranks review urgency, not CVSS or confirmed impact:

- `high`: cleartext administrative access was observed;
- `medium`: remote access, file sharing or database exposure requires contextual validation;
- `low`: common service-hardening or encrypted-transport review.

## Threats and controls

| Threat | Existing control | Residual risk |
|---|---|---|
| Malicious XML text rendered in HTML | Contextual HTML escaping | Reports still disclose sensitive inventory |
| Credential exposure | Zabbix credentials only in environment variables | Process and CI environments must be protected |
| Accidental remote mutation | Zabbix disabled unless `--zabbix` is passed | Export is not idempotent and can create duplicates |
| Unsupported scientific claim | Explicit evidence boundary and deterministic rules | Operators can still misinterpret output externally |
| Sensitive scan committed to Git | Raw XML ignored; only reviewed fixtures allowed | Human review is still required before commits |

The parser cannot determine public exposure from one scan, verify authentication policy, confirm product identity, establish exploitability or demonstrate compliance. See [SECURITY.md](../SECURITY.md) for responsible disclosure.
