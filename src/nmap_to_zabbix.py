"""Parse authorized Nmap XML scans and produce evidence-based review findings."""

from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


@dataclass(frozen=True)
class ReviewRule:
    services: tuple[str, ...]
    ports: tuple[str, ...]
    severity: str
    title: str
    evidence: str
    recommendation: str


REVIEW_RULES = (
    ReviewRule(("telnet",), ("23",), "high", "Cleartext remote administration exposed", "An open Telnet service was observed.", "Replace Telnet with SSH and restrict administrative access at the network boundary."),
    ReviewRule(("ftp",), ("21",), "medium", "Cleartext file transfer exposed", "An open FTP service was observed.", "Use SFTP or FTPS and verify that anonymous access is disabled."),
    ReviewRule(("http",), ("80",), "low", "Unencrypted HTTP requires review", "An open HTTP service was observed.", "Confirm that HTTP redirects to HTTPS and that no sensitive traffic is accepted over cleartext."),
    ReviewRule(("netbios-ssn", "microsoft-ds", "smb"), ("139", "445"), "medium", "SMB exposure requires review", "An open SMB or NetBIOS service was observed.", "Limit SMB to required network segments and verify signing, authentication, and supported protocol versions."),
    ReviewRule(("mysql", "postgresql"), ("3306", "5432"), "medium", "Database listener exposure requires review", "An open database service was observed.", "Restrict database listeners to approved application networks and require encrypted authenticated connections."),
    ReviewRule(("ms-wbt-server", "rdp"), ("3389",), "medium", "Remote desktop exposure requires review", "An open RDP service was observed.", "Place remote desktop behind an approved access path, require MFA, and limit source networks."),
    ReviewRule(("vnc",), ("5900",), "medium", "VNC exposure requires review", "An open VNC service was observed.", "Restrict VNC to a protected management network and require encrypted strong authentication."),
    ReviewRule(("ssh",), ("22",), "low", "SSH hardening review", "An open SSH service was observed.", "Verify key-based authentication, supported algorithms, logging, and source-network restrictions."),
    ReviewRule(("smtp",), ("25",), "low", "Mail transport configuration review", "An open SMTP service was observed.", "Verify relay restrictions, authentication requirements, and opportunistic or mandatory TLS as appropriate."),
)


class ZabbixAPI:
    """Minimal JSON-RPC client used only when integration is explicitly enabled."""

    def __init__(self, url: str, username: str, password: str, *, timeout: float = 10, verify_tls: bool = True):
        self.url = url
        self.username = username
        self.password = password
        self.timeout = timeout
        self.verify_tls = verify_tls
        self.auth_token: str | None = None
        self.request_id = 1

    def _make_request(self, method: str, params: dict[str, Any]) -> Any:
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id,
        }
        if self.auth_token:
            payload["auth"] = self.auth_token
        self.request_id += 1

        response = requests.post(
            self.url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
            verify=self.verify_tls,
        )
        response.raise_for_status()
        body = response.json()
        if "error" in body:
            raise RuntimeError(f"Zabbix API error: {body['error']}")
        return body.get("result")

    def login(self) -> None:
        self.auth_token = self._make_request("user.login", {
            "username": self.username,
            "password": self.password,
        })
        if not self.auth_token:
            raise RuntimeError("Zabbix authentication returned no token")

    def create_host(self, hostname: str, ip_address: str, group_id: str) -> str:
        result = self._make_request("host.create", {
            "host": hostname,
            "interfaces": [{
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": ip_address,
                "dns": "",
                "port": "10050",
            }],
            "groups": [{"groupid": group_id}],
        })
        return result["hostids"][0]


class NmapParser:
    """Parse live hosts and open services from an Nmap XML document."""

    def __init__(self, nmap_file: str | Path):
        self.nmap_file = Path(nmap_file)
        self.hosts: list[dict[str, Any]] = []
        self.findings: list[dict[str, Any]] = []

    def parse_xml(self) -> list[dict[str, Any]]:
        self.hosts = []
        self.findings = []
        try:
            root = ET.parse(self.nmap_file).getroot()
        except (OSError, ET.ParseError) as error:
            raise ValueError(f"Unable to parse Nmap XML: {error}") from error

        for host_element in root.findall(".//host"):
            host = self._parse_host(host_element)
            if host:
                self.hosts.append(host)
        return self.hosts

    def _parse_host(self, element: ET.Element) -> dict[str, Any] | None:
        status = element.find("status")
        if status is None or status.get("state") != "up":
            return None

        address = next((item for item in element.findall("address") if item.get("addrtype") in {"ipv4", "ipv6"}), None)
        if address is None or not address.get("addr"):
            return None
        ip_address = address.get("addr", "")

        hostname_element = element.find("./hostnames/hostname")
        hostname = hostname_element.get("name", ip_address) if hostname_element is not None else ip_address
        os_match = element.find("./os/osmatch")
        operating_system = os_match.get("name", "Unknown") if os_match is not None else "Unknown"

        ports = []
        host_findings = []
        for port_element in element.findall("./ports/port"):
            parsed_port = self._parse_port(port_element, ip_address)
            if parsed_port:
                ports.append(parsed_port)
                finding = self._review_service(ip_address, parsed_port)
                if finding:
                    self.findings.append(finding)
                    host_findings.append(finding)

        return {
            "ip": ip_address,
            "hostname": hostname,
            "os": operating_system,
            "ports": ports,
            "total_ports": len(ports),
            "findings": host_findings,
        }

    @staticmethod
    def _parse_port(element: ET.Element, ip_address: str) -> dict[str, str] | None:
        state = element.find("state")
        if state is None or state.get("state") != "open":
            return None
        service_element = element.find("service")
        return {
            "port": element.get("portid", ""),
            "protocol": element.get("protocol", "unknown"),
            "service": service_element.get("name", "unknown") if service_element is not None else "unknown",
            "product": service_element.get("product", "") if service_element is not None else "",
            "version": service_element.get("version", "") if service_element is not None else "",
            "ip": ip_address,
        }

    @staticmethod
    def _review_service(ip_address: str, port: dict[str, str]) -> dict[str, Any] | None:
        service = port["service"].lower()
        for rule in REVIEW_RULES:
            if service in rule.services or port["port"] in rule.ports:
                return {
                    "ip": ip_address,
                    "port": port["port"],
                    "protocol": port["protocol"],
                    "service": port["service"],
                    "product": port["product"],
                    "version": port["version"],
                    "severity": rule.severity,
                    "title": rule.title,
                    "evidence": rule.evidence,
                    "recommendation": rule.recommendation,
                    "classification": "configuration-review",
                    "confirmed_vulnerability": False,
                    "cves": [],
                }
        return None

    def get_finding_summary(self) -> dict[str, Any]:
        return {
            "total": len(self.findings),
            "high": sum(item["severity"] == "high" for item in self.findings),
            "medium": sum(item["severity"] == "medium" for item in self.findings),
            "low": sum(item["severity"] == "low" for item in self.findings),
            "findings": self.findings,
        }


class ReportGenerator:
    @staticmethod
    def generate_json_report(hosts: list[dict[str, Any]], summary: dict[str, Any], output_file: str | Path) -> Path:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "disclaimer": "Findings are configuration-review prompts based on observed open services, not confirmed vulnerabilities.",
            "summary": {key: summary[key] for key in ("total", "high", "medium", "low")},
            "hosts": hosts,
            "findings": summary["findings"],
        }
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @staticmethod
    def generate_markdown_report(hosts: list[dict[str, Any]], summary: dict[str, Any], output_file: str | Path) -> Path:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Network Inventory and Security Review",
            "",
            "> Findings are review prompts based on observed open services. They are not confirmed vulnerabilities and do not imply a CVE match.",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Summary",
            "",
            f"- Live hosts: {len(hosts)}",
            f"- Review findings: {summary['total']}",
            f"- High: {summary['high']}",
            f"- Medium: {summary['medium']}",
            f"- Low: {summary['low']}",
            "",
            "## Inventory",
            "",
        ]
        for host in hosts:
            lines.extend([f"### {host['hostname']} ({host['ip']})", "", f"Operating system guess: {host['os']}", "", "| Port | Protocol | Service | Product | Version |", "|---:|---|---|---|---|"])
            for port in host["ports"]:
                lines.append(f"| {port['port']} | {port['protocol']} | {port['service']} | {port['product']} | {port['version']} |")
            lines.append("")

        lines.extend(["## Review findings", ""])
        for finding in summary["findings"]:
            lines.extend([
                f"### {finding['title']}",
                "",
                f"- Endpoint: `{finding['ip']}:{finding['port']}/{finding['protocol']}`",
                f"- Severity: {finding['severity']}",
                f"- Evidence: {finding['evidence']}",
                f"- Recommendation: {finding['recommendation']}",
                "- Confirmed vulnerability: no",
                "",
            ])
        path.write_text("\n".join(lines), encoding="utf-8")
        return path


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def export_to_zabbix(hosts: list[dict[str, Any]], config: dict[str, Any]) -> None:
    zabbix = config["zabbix"]
    username = os.environ.get("ZABBIX_USERNAME")
    password = os.environ.get("ZABBIX_PASSWORD")
    if not username or not password:
        raise RuntimeError("ZABBIX_USERNAME and ZABBIX_PASSWORD are required for Zabbix export")
    api = ZabbixAPI(
        zabbix["url"],
        username,
        password,
        timeout=float(zabbix.get("timeout_seconds", 10)),
        verify_tls=bool(zabbix.get("verify_tls", True)),
    )
    api.login()
    for host in hosts:
        api.create_host(host["hostname"], host["ip"], str(zabbix.get("host_group_id", "2")))


def main(argv: list[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=repository_root / "src" / "config.json")
    parser.add_argument("--input", type=Path, help="Override the configured Nmap XML file")
    parser.add_argument("--output-dir", type=Path, help="Override the configured output directory")
    parser.add_argument("--zabbix", action="store_true", help="Explicitly export discovered hosts to Zabbix")
    arguments = parser.parse_args(argv)

    config = load_config(arguments.config)
    input_path = arguments.input or repository_root / config["nmap"]["input_file"]
    output_dir = arguments.output_dir or repository_root / config["output"]["directory"]
    if not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 2

    nmap_parser = NmapParser(input_path)
    try:
        hosts = nmap_parser.parse_xml()
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    summary = nmap_parser.get_finding_summary()

    markdown = ReportGenerator.generate_markdown_report(hosts, summary, output_dir / "network-review.md")
    json_report = ReportGenerator.generate_json_report(hosts, summary, output_dir / "network-review.json")

    from dashboard_tecnico import generate_technical_dashboard
    dashboard = generate_technical_dashboard(hosts, summary, output_file=output_dir / "dashboard.html")

    if arguments.zabbix:
        export_to_zabbix(hosts, config)

    print(f"Parsed {len(hosts)} live hosts and produced {summary['total']} review findings.")
    print(f"Reports: {markdown}, {json_report}, {dashboard}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
