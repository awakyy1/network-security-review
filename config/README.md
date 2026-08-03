# Configuration

`default.json` contains safe repository defaults and no credentials. It points to a synthetic Nmap fixture and enables TLS verification for the placeholder Zabbix endpoint.

For local use, copy it to the ignored path `local.json` and pass `--config config/local.json`. Store `ZABBIX_USERNAME` and `ZABBIX_PASSWORD` only in the process environment or an approved secret manager.
