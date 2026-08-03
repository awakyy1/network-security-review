# Synthetic examples

All XML files in this directory are intentionally synthetic fixtures for demonstration and CI. Hostnames, addresses, products and versions do not describe a real organization.

- `nmap/synthetic-enterprise.xml`: multi-host example used by the default configuration and CI smoke test;
- `nmap/synthetic-lab.xml`: smaller laboratory-style example.

Never replace these files with raw production scans. Use `--input` with a secure path outside the repository when processing authorized real data.
