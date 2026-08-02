# Quick Start

## 1. Create an authorized Nmap XML scan

Run scans only against assets you own or have explicit permission to assess.

```sh
nmap -sV -O -oX data/scan_result.xml 192.0.2.0/28
```

`-sV` requests service fingerprinting, `-O` requests an OS guess, and `-oX` writes XML for the parser. Results remain observations and can contain false or incomplete fingerprints.

## 2. Install dependencies

```sh
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

Use `.venv/bin/python` on Unix-like systems.

## 3. Generate reports

```sh
.venv/Scripts/python src/nmap_to_zabbix.py
```

Generated files:

- `output/network-review.md`
- `output/network-review.json`
- `output/dashboard.html`

## Command options

```text
--config PATH       Use another JSON configuration file
--input PATH        Override the Nmap XML input
--output-dir PATH   Override the output directory
--zabbix            Explicitly enable Zabbix host export
```

Example with isolated test data:

```sh
python src/nmap_to_zabbix.py --input tests/test_cenario2.xml --output-dir output/test
```

## Validate findings

For each review item, confirm the asset owner, exposure boundary, business requirement, actual product and version, authentication and encryption configuration, and compensating controls. Only then should a qualified analyst decide whether a vulnerability record or remediation ticket is justified.
