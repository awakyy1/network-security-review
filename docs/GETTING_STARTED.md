# Getting started

## 1. Prepare Python

Python 3.10 or newer is required.

```sh
python -m venv .venv
.venv/Scripts/python -m pip install --requirement requirements.txt
```

Use `.venv/bin/python` on Linux or macOS.

## 2. Run the synthetic demonstration

The default configuration uses a reviewed synthetic fixture and does not perform a live scan.

```sh
.venv/Scripts/python src/nmap_to_zabbix.py
```

Generated files:

- `output/network-review.md`
- `output/network-review.json`
- `output/dashboard.html`

## 3. Process an authorized scan

Only scan assets you own or are explicitly authorized to assess. Store real XML outside the repository.

```sh
nmap -sV -O -oX C:/secure-location/authorized-scan.xml 192.0.2.0/28
python src/nmap_to_zabbix.py --input C:/secure-location/authorized-scan.xml --output-dir output/authorized-review
```

`-sV` requests service fingerprinting, `-O` requests an OS guess and `-oX` writes XML. Fingerprints remain observations and can be incomplete or incorrect.

## CLI options

```text
--config PATH       Use another JSON configuration file
--input PATH        Override the configured Nmap XML input
--output-dir PATH   Override the configured output directory
--zabbix            Explicitly enable Zabbix host export
```

## Optional Zabbix export

Copy `config/default.json` to the ignored path `config/local.json`, then configure only the endpoint, group and TLS behavior. Keep credentials in environment variables.

```powershell
$env:ZABBIX_USERNAME = 'least-privilege-api-user'
$env:ZABBIX_PASSWORD = 'replace-me'
python src/nmap_to_zabbix.py --config config/local.json --input C:/secure-location/authorized-scan.xml --zabbix
```

The integration is not a dry run: it can create Zabbix hosts. Use a test environment first and review [SECURITY.md](../SECURITY.md).

## Validate findings

For each item, confirm asset ownership, exposure boundary, business requirement, actual product/version, authentication, encryption and compensating controls. Only a qualified assessment may promote a review item to a confirmed vulnerability or remediation record.
