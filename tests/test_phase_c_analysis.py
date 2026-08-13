from __future__ import annotations

import json
import unittest

from src.phase_c_analysis import grounded_metrics, historical_metrics


def _finding() -> dict[str, object]:
    return {"finding_id": "BEH-001-example", "evidence_ids": ["EV-001"]}


def _grounded_output() -> dict[str, object]:
    return {
        "summary": "Review this observation.",
        "priorities": [
            {
                "finding_id": "BEH-001-example",
                "priority": "medium",
                "rationale": "Periodic behavior needs context.",
                "evidence_ids": ["EV-001"],
                "validation_steps": [],
                "control_ids": [],
            }
        ],
        "limitations": ["No compromise is confirmed."],
    }


class PhaseCAnalysisTest(unittest.TestCase):
    def test_grounded_metrics_separate_traceability_and_policy_acceptance(self) -> None:
        record = {
            "scenarios": [
                {
                    "findings": [_finding()],
                    "ollama": {
                        "status": "validation-failure",
                        "raw_response": json.dumps(_grounded_output()),
                        "error": "controlled rejection",
                    },
                }
            ]
        }

        result = grounded_metrics([record])

        self.assertEqual(result["api_responses"], 1)
        self.assertEqual(result["schema_valid"], 1)
        self.assertEqual(result["exact_evidence_coverage"], 1)
        self.assertEqual(result.get("accepted", 0), 0)
        self.assertEqual(result["policy_rejections"], 1)

    def test_historical_metrics_count_affected_responses_not_term_occurrences(self) -> None:
        audit = {
            "finding_coverage": 0.0,
            "evidence_coverage": 0.0,
            "grounding_valid": False,
            "unsupported_security_attribution_mentions": ["malware", "spyware"],
            "unqualified_containment_action": True,
            "within_200_word_limit": False,
            "markdown_marker_present": True,
        }
        record = {"scenarios": [{"ollama": {"status": "observed", "audit": audit}}]}

        result = historical_metrics([record])

        self.assertEqual(result["security_attribution_responses"], 1)
        self.assertEqual(result["unqualified_containment_responses"], 1)


if __name__ == "__main__":
    unittest.main()
