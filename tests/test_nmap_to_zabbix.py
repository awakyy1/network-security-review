from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.dashboard_tecnico import generate_technical_dashboard
from src.nmap_to_zabbix import NmapParser, ReportGenerator, ZabbixAPI


SAMPLE_XML = """<?xml version="1.0"?>
<nmaprun>
  <host>
    <status state="up"/>
    <address addr="192.0.2.10" addrtype="ipv4"/>
    <hostnames><hostname name="example&lt;host&gt;"/></hostnames>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open"/>
        <service name="ssh" product="OpenSSH" version="9.3"/>
      </port>
      <port protocol="tcp" portid="443">
        <state state="open"/>
        <service name="https" product="Example Server" version="1.0"/>
      </port>
      <port protocol="tcp" portid="23">
        <state state="closed"/>
        <service name="telnet"/>
      </port>
    </ports>
  </host>
</nmaprun>
"""


class NmapParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.input_file = self.directory / "scan.xml"
        self.input_file.write_text(SAMPLE_XML, encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_parser_inventory_and_findings_are_evidence_based(self) -> None:
        parser = NmapParser(self.input_file)
        hosts = parser.parse_xml()
        summary = parser.get_finding_summary()

        self.assertEqual(len(hosts), 1)
        self.assertEqual(hosts[0]["total_ports"], 2)
        self.assertEqual(summary["total"], 1)
        finding = summary["findings"][0]
        self.assertEqual(finding["title"], "SSH hardening review")
        self.assertFalse(finding["confirmed_vulnerability"])
        self.assertEqual(finding["cves"], [])

    def test_malformed_xml_raises_a_clear_error(self) -> None:
        self.input_file.write_text("<nmaprun>", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unable to parse Nmap XML"):
            NmapParser(self.input_file).parse_xml()

    def test_reports_preserve_the_interpretation_boundary(self) -> None:
        parser = NmapParser(self.input_file)
        hosts = parser.parse_xml()
        summary = parser.get_finding_summary()

        markdown = ReportGenerator.generate_markdown_report(hosts, summary, self.directory / "report.md")
        json_path = ReportGenerator.generate_json_report(hosts, summary, self.directory / "report.json")
        dashboard = Path(generate_technical_dashboard(hosts, summary, output_file=self.directory / "dashboard.html"))

        self.assertIn("not confirmed vulnerabilities", markdown.read_text(encoding="utf-8"))
        report = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertIn("not confirmed vulnerabilities", report["disclaimer"])
        dashboard_text = dashboard.read_text(encoding="utf-8")
        self.assertIn("not confirmed vulnerabilities", dashboard_text)
        self.assertIn("example&lt;host&gt;", dashboard_text)
        self.assertNotIn("example<host>", dashboard_text)


class ZabbixApiTest(unittest.TestCase):
    @patch("src.nmap_to_zabbix.requests.post")
    def test_request_uses_tls_verification_and_timeout(self, post: Mock) -> None:
        response = Mock()
        response.json.return_value = {"jsonrpc": "2.0", "result": "token", "id": 1}
        post.return_value = response

        api = ZabbixAPI(
            "https://zabbix.example/api_jsonrpc.php",
            "api-user",
            "secret",
            timeout=4,
            verify_tls=True,
        )
        api.login()

        post.assert_called_once()
        self.assertEqual(post.call_args.kwargs["timeout"], 4)
        self.assertTrue(post.call_args.kwargs["verify"])
        self.assertNotIn("secret", json.dumps(post.call_args.kwargs["headers"]))


if __name__ == "__main__":
    unittest.main()
