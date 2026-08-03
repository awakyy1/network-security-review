# Tests

The unit suite uses only synthetic, in-memory XML and mocked HTTP calls. It validates parsing semantics, malformed-input errors, report disclaimers, HTML escaping and Zabbix TLS/timeout behavior.

```sh
python -m unittest discover -s tests -p "test_*.py" -v
```

Files under `fixtures/` are synthetic academic scenarios and contain no real infrastructure data.
