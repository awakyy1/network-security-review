"""Generate a self-contained HTML inventory and review dashboard."""

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


def _text(value: Any) -> str:
    return escape(str(value or ""), quote=True)


def _host_rows(hosts: list[dict[str, Any]]) -> str:
    rows = []
    for host in hosts:
        services = ", ".join(
            f"{port['port']}/{port['protocol']} {port['service']}"
            for port in host.get("ports", [])
        ) or "None observed"
        rows.append(
            "<tr>"
            f"<td><strong>{_text(host.get('hostname'))}</strong></td>"
            f"<td><code>{_text(host.get('ip'))}</code></td>"
            f"<td>{_text(host.get('os', 'Unknown'))}</td>"
            f"<td>{int(host.get('total_ports', 0))}</td>"
            f"<td>{_text(services)}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="5">No live hosts were present in the input.</td></tr>'


def _finding_rows(findings: list[dict[str, Any]]) -> str:
    rows = []
    for finding in findings:
        severity = finding.get("severity", "low")
        if severity not in {"high", "medium", "low"}:
            severity = "low"
        product = " ".join(filter(None, [finding.get("product"), finding.get("version")])) or "Not identified"
        rows.append(
            "<tr>"
            f'<td><span class="severity severity-{severity}">{_text(severity.upper())}</span></td>'
            f"<td><strong>{_text(finding.get('title'))}</strong><br><small>{_text(finding.get('evidence'))}</small></td>"
            f"<td><code>{_text(finding.get('ip'))}:{_text(finding.get('port'))}/{_text(finding.get('protocol'))}</code></td>"
            f"<td>{_text(finding.get('service'))}<br><small>{_text(product)}</small></td>"
            f"<td>{_text(finding.get('recommendation'))}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="5">No configured review rules matched the observed services.</td></tr>'


def generate_technical_dashboard(
    hosts: list[dict[str, Any]],
    finding_summary: dict[str, Any],
    *,
    output_file: str | Path = "dashboard.html",
    **_: Any,
) -> str:
    """Write a static dashboard and return its path."""
    destination = Path(output_file)
    destination.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Network Inventory and Security Review</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, system-ui, sans-serif; background: #f4f5f7; color: #202124; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; }}
    header {{ background: #202124; color: #fff; padding: 24px max(20px, calc((100vw - 1200px) / 2)); }}
    header h1 {{ margin: 0 0 6px; font-size: 26px; letter-spacing: 0; }}
    header p {{ margin: 0; color: #d7d9dd; }}
    main {{ width: min(1200px, calc(100% - 40px)); margin: 24px auto 48px; }}
    .notice {{ border-left: 4px solid #9a6700; background: #fff8c5; padding: 14px 16px; margin-bottom: 20px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 12px; margin: 20px 0 28px; }}
    .metric {{ background: #fff; border: 1px solid #d9dce1; border-radius: 6px; padding: 16px; }}
    .metric span {{ display: block; color: #5f6368; font-size: 13px; }}
    .metric strong {{ display: block; font-size: 28px; margin-top: 4px; }}
    section {{ margin-top: 30px; }}
    h2 {{ font-size: 20px; letter-spacing: 0; }}
    .table-wrap {{ overflow-x: auto; border: 1px solid #d9dce1; border-radius: 6px; background: #fff; }}
    table {{ border-collapse: collapse; width: 100%; min-width: 760px; }}
    th, td {{ border-bottom: 1px solid #e7e8eb; padding: 12px; text-align: left; vertical-align: top; }}
    th {{ background: #f0f1f3; font-size: 12px; text-transform: uppercase; }}
    tr:last-child td {{ border-bottom: 0; }}
    code {{ font-family: ui-monospace, Consolas, monospace; }}
    small {{ color: #5f6368; }}
    .severity {{ display: inline-block; border-radius: 4px; color: #fff; font-size: 11px; font-weight: 700; padding: 3px 7px; }}
    .severity-high {{ background: #b42318; }}
    .severity-medium {{ background: #9a6700; }}
    .severity-low {{ background: #39764e; }}
    footer {{ color: #5f6368; font-size: 12px; margin-top: 24px; }}
    @media (max-width: 760px) {{ .metrics {{ grid-template-columns: repeat(2, 1fr); }} main {{ width: min(100% - 24px, 1200px); }} }}
  </style>
</head>
<body>
  <header>
    <h1>Network Inventory and Security Review</h1>
    <p>Generated {_text(generated_at)}</p>
  </header>
  <main>
    <div class="notice"><strong>Interpretation boundary:</strong> these are configuration-review prompts based on observed open services. They are not confirmed vulnerabilities, CVE matches, exploitation results, or compliance determinations.</div>
    <div class="metrics" aria-label="Summary">
      <div class="metric"><span>Live hosts</span><strong>{len(hosts)}</strong></div>
      <div class="metric"><span>Review findings</span><strong>{int(finding_summary.get('total', 0))}</strong></div>
      <div class="metric"><span>High</span><strong>{int(finding_summary.get('high', 0))}</strong></div>
      <div class="metric"><span>Medium</span><strong>{int(finding_summary.get('medium', 0))}</strong></div>
      <div class="metric"><span>Low</span><strong>{int(finding_summary.get('low', 0))}</strong></div>
    </div>

    <section>
      <h2>Observed hosts and services</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>Hostname</th><th>Address</th><th>OS guess</th><th>Open ports</th><th>Services</th></tr></thead>
        <tbody>{_host_rows(hosts)}</tbody>
      </table></div>
    </section>

    <section>
      <h2>Configuration-review findings</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>Severity</th><th>Finding</th><th>Endpoint</th><th>Observed service</th><th>Recommendation</th></tr></thead>
        <tbody>{_finding_rows(finding_summary.get('findings', []))}</tbody>
      </table></div>
    </section>
    <footer>Use only with scan data collected under explicit authorization. Validate every finding against network context, service configuration, and asset ownership.</footer>
  </main>
</body>
</html>
"""
    destination.write_text(document, encoding="utf-8")
    return str(destination)


if __name__ == "__main__":
    raise SystemExit("Import generate_technical_dashboard from nmap_to_zabbix.py.")
