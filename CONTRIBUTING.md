# Contributing

Thank you for improving this academic defensive-security project. Contributions should remain reproducible, evidence-based and safe for public review.

## Development setup

1. Use Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install `requirements.txt` and `requirements-dev.txt`.
4. Run the checks below before opening a pull request.

```sh
python -m pip install --requirement requirements.txt --requirement requirements-dev.txt
ruff check .
python -m unittest discover -s tests -p "test_*.py" -v
python src/nmap_to_zabbix.py --input examples/nmap/synthetic-enterprise.xml --output-dir output/local
```

## Contribution rules

- Use only synthetic, reserved or demonstrably sanitized network data.
- Never commit credentials, tokens, personal data or real infrastructure inventories.
- Preserve the distinction between observed service, review finding and confirmed vulnerability.
- Add a test for behavior changes and explain the evidence behind new review rules.
- Update documentation and academic traceability when implementation claims change.
- Keep Zabbix or future firewall mutations explicit, least-privileged and disabled by default.

## Pull requests

Keep each pull request focused. Describe the motivation, implementation, validation and any effect on scientific claims. The checklist in the pull request template is part of the review.

Security vulnerabilities must follow [SECURITY.md](SECURITY.md) and should not be disclosed in a public issue.
