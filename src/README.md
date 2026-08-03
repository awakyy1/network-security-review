# Source modules

| Module | Purpose |
|---|---|
| `nmap_to_zabbix.py` | Parser, transparent review rules, report generation, Zabbix client and CLI orchestration |
| `dashboard.py` | Escaped, self-contained HTML dashboard renderer |

The code intentionally remains small and direct for academic auditability. Behavioral boundaries are documented in [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) and [`docs/SECURITY_MODEL.md`](../docs/SECURITY_MODEL.md).
