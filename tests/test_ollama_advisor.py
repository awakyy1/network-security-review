from __future__ import annotations

import json
import unittest
from unittest.mock import Mock, patch

from src.ollama_advisor import OUTPUT_SCHEMA, OllamaAdvisor, OllamaOutputError, validate_grounded_output
from src.telemetry import TelemetryEvent


def _event() -> TelemetryEvent:
    return TelemetryEvent.from_mapping(
        {
            "event_id": "EV-001",
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


def _finding(finding_id: str = "BEH-001-example") -> dict[str, object]:
    return {
        "finding_id": finding_id,
        "rule_id": "BEH-001",
        "title": "Periodic outbound communication requires review",
        "evidence_ids": ["EV-001"],
        "confirmed_malware": False,
        "automatic_response_authorized": False,
    }


def _valid_output() -> dict[str, object]:
    return {
        "summary": "Periodic traffic requires contextual validation.",
        "priorities": [
            {
                "finding_id": "BEH-001-example",
                "priority": "medium",
                "rationale": "The periodic observation may also represent approved software.",
                "evidence_ids": ["EV-001"],
                "validation_steps": ["Confirm the process owner and update schedule."],
                "control_ids": ["collect-more-telemetry", "validate-process-owner"],
            }
        ],
        "limitations": ["One event is insufficient to confirm malicious activity."],
    }


class OllamaAdvisorTest(unittest.TestCase):
    @patch("src.ollama_advisor.requests.post")
    def test_uses_schema_constrained_local_generation(self, post: Mock) -> None:
        response = Mock()
        response.json.return_value = {
            "model": "research-model",
            "response": json.dumps(_valid_output()),
            "total_duration": 123,
            "prompt_eval_count": 20,
            "eval_count": 10,
        }
        post.return_value = response

        result = OllamaAdvisor("research-model").analyze([_finding()], [_event()])

        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["format"], OUTPUT_SCHEMA)
        self.assertEqual(payload["options"]["temperature"], 0)
        self.assertEqual(payload["options"]["seed"], 42)
        self.assertEqual(payload["options"]["num_ctx"], 4096)
        self.assertEqual(payload["options"]["num_predict"], 700)
        self.assertIn("<UNTRUSTED_EVIDENCE>", payload["prompt"])
        self.assertEqual(post.call_args.args[0], "http://127.0.0.1:11434/api/generate")
        self.assertTrue(result["metadata"]["grounding_valid"])
        self.assertEqual(result["raw_response"], json.dumps(_valid_output()))

    def test_rejects_unknown_evidence_citations(self) -> None:
        output = _valid_output()
        output["priorities"][0]["evidence_ids"] = ["INVENTED-999"]

        with self.assertRaisesRegex(ValueError, "evidence not attached"):
            validate_grounded_output(output, [_finding()])

    def test_rejects_invented_cves(self) -> None:
        output = _valid_output()
        output["summary"] = "The evidence proves CVE-2099-99999."

        with self.assertRaisesRegex(ValueError, "introduced a CVE"):
            validate_grounded_output(output, [_finding()])

    def test_requires_every_finding_exactly_once(self) -> None:
        output = _valid_output()

        with self.assertRaisesRegex(ValueError, "every supplied finding exactly once"):
            validate_grounded_output(output, [_finding(), _finding("BEH-001-second")])

    def test_rejects_empty_priority_array_at_schema_boundary(self) -> None:
        output = _valid_output()
        output["priorities"] = []

        with self.assertRaisesRegex(ValueError, "at least one priority"):
            validate_grounded_output(output, [_finding()])

    def test_rejects_control_irrelevant_to_behavior_rule(self) -> None:
        output = _valid_output()
        output["priorities"][0]["control_ids"] = ["quarantine-file-after-validation"]

        with self.assertRaisesRegex(ValueError, "not applicable to rule BEH-001"):
            validate_grounded_output(output, [_finding()])

    @patch("src.ollama_advisor.requests.post")
    def test_preserves_raw_response_when_model_output_is_rejected(self, post: Mock) -> None:
        response = Mock()
        rejected = _valid_output()
        rejected["priorities"][0]["evidence_ids"] = ["INVENTED-999"]
        response.json.return_value = {
            "model": "research-model",
            "response": json.dumps(rejected),
            "total_duration": 123,
        }
        post.return_value = response

        with self.assertRaises(OllamaOutputError) as raised:
            OllamaAdvisor("research-model").analyze([_finding()], [_event()])

        self.assertEqual(raised.exception.raw_response, json.dumps(rejected))
        self.assertFalse(raised.exception.metadata["grounding_valid"])

    def test_restricts_ollama_to_loopback(self) -> None:
        with self.assertRaisesRegex(ValueError, "local loopback"):
            OllamaAdvisor("research-model", base_url="https://ollama.example.test")


if __name__ == "__main__":
    unittest.main()
