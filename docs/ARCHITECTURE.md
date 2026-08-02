# Architecture

## Processing flow

1. `NmapParser` reads a local Nmap XML document with Python's standard XML parser.
2. Live hosts and ports in the `open` state become inventory records.
3. `REVIEW_RULES` matches selected service names or conventional ports.
4. Matches become configuration-review findings with observed evidence and a validation recommendation.
5. `ReportGenerator` writes Markdown and JSON.
6. `generate_technical_dashboard` writes escaped, self-contained HTML.
7. Zabbix export runs only when the operator passes `--zabbix`.

## Trust boundaries

Nmap XML is untrusted input. Values are treated as text, never executed, and escaped before HTML rendering. Generated Markdown and JSON may still contain sensitive network identifiers and should be protected accordingly.

Zabbix is an external privileged system. Credentials come only from environment variables, TLS verification defaults to enabled, and requests use a configured timeout. The integration creates objects and therefore requires explicit command-line activation.

## Extension points

Add review rules only when the observable evidence supports the wording. A rule may recommend validation, but it must not name a CVE or claim a vulnerable version without a separate authoritative matching process using normalized product identifiers and version ranges.
