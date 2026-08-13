from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.result_preservation import preserve_repeated_results


def _analysis() -> dict[str, object]:
    return {
        "summary": "Review supplied evidence.",
        "priorities": [
            {
                "finding_id": "BEH-001-example",
                "priority": "medium",
                "rationale": "Periodic behavior is reviewable.",
                "evidence_ids": ["EV-001"],
                "validation_steps": [],
                "control_ids": [],
            }
        ],
        "limitations": ["No malicious activity is confirmed."],
    }


class ResultPreservationTest(unittest.TestCase):
    @patch("src.result_preservation._base_commit", return_value="abc123")
    def test_preserves_raw_run_and_corrects_accounting(self, _commit: object) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "output" / "repetitions"
            run = source / "run-001"
            run.mkdir(parents=True)
            analysis = _analysis()
            record = {
                "metrics": {"true_positive": 1},
                "ollama_evaluation": {
                    "protocol": "grounded",
                    "attempts": 1,
                    "api_successes": 0,
                    "accepted": 0,
                    "api_failures": 0,
                    "validation_failures": 1,
                    "json_parse_valid": 0,
                    "schema_valid": 0,
                    "unknown_finding_citations": 0,
                    "unknown_evidence_citations": 0,
                    "unsupported_cve_mentions": 0,
                    "absolute_assertions": 0,
                    "unsupported_security_attribution_mentions": 0,
                    "containment_action_mentions": 0,
                    "unqualified_containment_actions": 0,
                    "word_limit_violations": 0,
                    "markdown_format_violations": 0,
                    "mean_finding_coverage": 0.0,
                    "mean_evidence_coverage": 0.0,
                },
                "scenarios": [
                    {
                        "id": "example",
                        "findings": [{"finding_id": "BEH-001-example", "evidence_ids": ["EV-001"]}],
                        "ollama": {
                            "status": "validation-failure",
                            "raw_response": json.dumps(analysis),
                            "metadata": {
                                "elapsed_ms": 100,
                                "api_response_received": True,
                                "json_parse_valid": True,
                                "schema_valid": True,
                                "grounding_valid": False,
                            },
                        },
                    }
                ],
            }
            original = json.dumps(record, indent=2)
            (run / "benchmark.json").write_text(original, encoding="utf-8")
            (run / "benchmark.md").write_text("original projection\n", encoding="utf-8")
            (source / "summary.json").write_text(
                json.dumps({"repetitions": 1, "model": "model", "manifest": "manifest.json"}), encoding="utf-8"
            )
            (source / "summary.md").write_text("original summary\n", encoding="utf-8")

            destination = root / "research" / "v2" / "results" / "preserved"
            summary = preserve_repeated_results(source, destination, root, execution_source_state="retrospective")

            self.assertEqual((destination / "runs" / "run-001.json").read_text(encoding="utf-8"), original)
            self.assertEqual(summary["ollama"]["api_success_rate"], 1.0)
            self.assertEqual(summary["ollama"]["schema_valid_rate"], 1.0)
            self.assertEqual(summary["ollama"]["accepted_grounding_rate"], 0.0)
            provenance = json.loads((destination / "provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(provenance["execution_source_state"], "retrospective")

    @patch("src.result_preservation._base_commit", return_value="abc123")
    def test_refuses_to_overwrite_preserved_evidence(self, _commit: object) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            destination = root / "destination"
            destination.mkdir()
            (destination / "evidence.json").write_text("{}", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "not empty"):
                preserve_repeated_results(source, destination, root, execution_source_state="exact")


if __name__ == "__main__":
    unittest.main()
