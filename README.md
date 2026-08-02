# Nmap Inventory and Security Review

A defensive Python tool that parses authorized Nmap XML output, inventories live hosts and open services, produces evidence-based configuration-review findings, and optionally registers discovered hosts in Zabbix.

## Interpretation boundary

An open port is not automatically a vulnerability. This tool does not claim exploitability, assign CVEs, calculate CVSS, certify compliance, or prove that a service is exposed to the public internet. Every generated item is explicitly marked as a review prompt and must be validated against asset ownership, network position, product identity, version evidence, and actual configuration.

## Features

- Parses live hosts, hostnames, OS guesses, open ports, and Nmap service fingerprints
- Flags a small documented set of services for configuration review
- Generates English Markdown, JSON, and self-contained HTML output
- Escapes Nmap-controlled text before rendering HTML
- Supports optional, explicit Zabbix host export
- Keeps Zabbix credentials in environment variables
- Includes deterministic unit tests with no live scanning or Zabbix requirement

## Quick start

Requirements: Python 3.10 or newer.

```sh
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python src/nmap_to_zabbix.py
```

On Unix-like systems, use `.venv/bin/python`. The default configuration reads `data/scan_result.xml` and writes generated files under `output/`.

See [QUICKSTART.md](QUICKSTART.md) for scan and command examples.

## Zabbix export

Zabbix integration is disabled unless `--zabbix` is passed. Configure the endpoint and TLS behavior in `src/config.json`, then set credentials in the process environment:

```powershell
$env:ZABBIX_USERNAME = 'api-user'
$env:ZABBIX_PASSWORD = 'replace-me'
python src/nmap_to_zabbix.py --zabbix
```

Use a least-privilege Zabbix API account. TLS certificate verification is enabled by default, and requests have a finite timeout.

## Test

```sh
python -m unittest discover -s tests -p "test_*.py" -v
```

## Responsible use

Only process scans collected with explicit authorization. Nmap output can reveal sensitive infrastructure details; keep raw XML and generated reports out of public repositories unless the data is intentionally synthetic and reviewed.

## Limitations

- Rules are service-exposure review heuristics, not vulnerability detection.
- Nmap product and OS fingerprints can be incomplete or incorrect.
- No external vulnerability database matching is implemented.
- Zabbix export creates hosts but does not reconcile or delete existing objects.
- The tool does not run Nmap, exploit services, or perform authenticated configuration checks.
