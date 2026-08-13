from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from src.ollama_baseline import HistoricalOllamaAdvisor, audit_free_text
from src.telemetry import TelemetryEvent


def _finding() -> dict[str, object]:
    return {
        "finding_id": "BEH-001-example",
        "rule_id": "BEH-001",
        "evidence_ids": ["EVT-001"],
    }


def _event() -> TelemetryEvent:
    return TelemetryEvent.from_mapping(
        {
            "event_id": "EVT-001",
            "timestamp": "2026-01-15T12:00:00Z",
            "host": "10.0.1.10",
            "event_type": "network_connection",
            "source": "lab",
            "process": "lab.exe",
            "destination_domain": "example.test",
            "destination_port": 443,
            "protocol": "tcp",
        }
    )


class HistoricalOllamaAdvisorTest(unittest.TestCase):
    def test_audits_known_unknown_and_unsupported_claims(self) -> None:
        response = (
            "BEH-001-example cites EVT-001 and FAKE-999. Possible malware is present. "
            "The host is compromised through CVE-2099-99999."
        )

        audit = audit_free_text(response, [_finding()])

        self.assertEqual(audit["known_finding_citations"], ["BEH-001-example"])
        self.assertEqual(audit["known_evidence_citations"], ["EVT-001"])
        self.assertEqual(audit["unknown_evidence_citations"], ["FAKE-999"])
        self.assertEqual(audit["unsupported_cve_mentions"], ["CVE-2099-99999"])
        self.assertEqual(audit["absolute_assertions"], ["host is compromised"])
        self.assertEqual(audit["unsupported_security_attribution_mentions"], ["malware"])
        self.assertFalse(audit["json_parse_valid"])

    def test_flags_unqualified_containment_recommendation(self) -> None:
        audit = audit_free_text("Isolar a máquina e segmentar a rede.", [_finding()])

        self.assertTrue(audit["unqualified_containment_action"])
        self.assertFalse(audit["human_approval_qualifier_present"])

        qualified = audit_free_text("Isolar após confirmação e aprovação humana.", [_finding()])
        self.assertFalse(qualified["unqualified_containment_action"])

    def test_measures_historical_format_instruction_adherence(self) -> None:
        audit = audit_free_text("**ANÁLISE**\n\n" + "palavra " * 201, [_finding()])

        self.assertTrue(audit["markdown_marker_present"])
        self.assertFalse(audit["within_200_word_limit"])

    @patch("src.ollama_baseline.requests.post")
    def test_reconstructs_free_text_protocol_without_schema_or_system_prompt(self, post: Mock) -> None:
        response = Mock()
        response.json.return_value = {
            "model": "research-model",
            "response": "Review BEH-001-example using EVT-001.",
            "total_duration": 123,
        }
        post.return_value = response

        result = HistoricalOllamaAdvisor("research-model").analyze([_finding()], [_event()])

        payload = post.call_args.kwargs["json"]
        self.assertNotIn("format", payload)
        self.assertNotIn("system", payload)
        self.assertEqual(payload["options"]["temperature"], 0.7)
        self.assertEqual(payload["options"]["top_p"], 0.9)
        self.assertEqual(result["audit"]["finding_coverage"], 1.0)
        self.assertEqual(result["audit"]["evidence_coverage"], 1.0)

    def test_validates_loopback_endpoint(self) -> None:
        with self.assertRaisesRegex(ValueError, "local loopback"):
            HistoricalOllamaAdvisor("research-model", base_url="https://external.example.test")


if __name__ == "__main__":
    unittest.main()
