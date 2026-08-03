# Network Security Review

[![CI](https://github.com/awakyy1/TCC/actions/workflows/ci.yml/badge.svg)](https://github.com/awakyy1/TCC/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Thesis](https://img.shields.io/badge/thesis-approved-2E7D32)
[![License: MIT](https://img.shields.io/badge/code-MIT-2F74C0)](LICENSE)
![Scope](https://img.shields.io/badge/use-defensive-5B5B5B)

An academic defensive-security artifact that converts authorized Nmap XML output into a verifiable network inventory, transparent configuration-review prompts, and portable Markdown, JSON, and HTML reports. Zabbix host export is available only through an explicit command-line option.

> **Undergraduate thesis approved on 19 November 2025** in the Software Engineering program at Centro Universitário UniOpet, Curitiba, Brazil. Authors: João Vitor Ielen and Vinicius Mota Favaro.

[Português](README.md) · [Approved monograph](academic/monografia/monografia-aprovada-2025.pdf) · [Scientific article](academic/artigo/main.pdf) · [Citation metadata](CITATION.cff)

## Evidence boundary

The project deliberately separates three concepts:

1. Nmap observations become inventory records.
2. Transparent rule matches become configuration-review prompts.
3. A vulnerability requires independent, contextual confirmation.

Every generated finding contains `confirmed_vulnerability: false`. The current implementation does not run Nmap, exploit services, calculate CVSS, map CVEs, certify compliance, or change firewall rules.

## Quick start

Python 3.10 or newer is required.

```sh
python -m venv .venv
.venv/Scripts/python -m pip install --requirement requirements.txt
.venv/Scripts/python src/nmap_to_zabbix.py
```

Use `.venv/bin/python` on Linux or macOS. The default configuration processes the explicitly synthetic fixture at `examples/nmap/synthetic-enterprise.xml` and writes reports to `output/`.

```sh
python -m unittest discover -s tests -p "test_*.py" -v
```

See [Getting started](docs/GETTING_STARTED.md) for CLI and Zabbix examples.

## Research-to-code traceability

The pre-defense commit `dd63d4c` records the 2025 prototype, including optional Ollama analysis, dashboard heuristics, and optional Zabbix integration. The current hardened core, introduced in `b191269`, preserves inventory, transparent review rules, reports, and Zabbix while removing paths that lacked sufficient experimental validation.

The [academic context](docs/ACADEMIC_CONTEXT.md), [document policy](docs/DOCUMENT_POLICY.md), [methodology](docs/METHODOLOGY.md), [architecture](docs/ARCHITECTURE.md), [reproducibility guide](docs/REPRODUCIBILITY.md), and [security model](docs/SECURITY_MODEL.md) document that distinction. The approved monograph is an immutable historical artifact; only the article remains open to post-defense scientific refinement.

## Responsible use and licensing

Process only scan data collected under explicit authorization. Nmap XML and generated reports can expose sensitive infrastructure details; never publish real inventories. All repository examples are synthetic fixtures.

Source code, tests, synthetic examples, automation and technical documentation are available under the [MIT License](LICENSE). Documents under [`academic/`](academic/) are excluded and remain [all rights reserved](academic/LICENSE.md). See [LICENSING.md](LICENSING.md) for the complete boundary and [CITATION.cff](CITATION.cff) for authorship and citation guidance.
