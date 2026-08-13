from __future__ import annotations

import json
import unittest

from src.v2_repetitions import aggregate_results


def _result(*, elapsed_ms: float, accepted: int = 1) -> dict[str, object]:
    analysis = {
        "summary": "Review the supplied evidence.",
        "priorities": [
            {
                "finding_id": "BEH-002-example",
                "priority": "high",
                "rationale": "Observed behavior.",
                "evidence_ids": ["EV-002"],
                "validation_steps": [],
                "control_ids": [],
            },
            {
                "finding_id": "BEH-001-example",
                "priority": "medium",
                "rationale": "Observed behavior.",
                "evidence_ids": ["EV-001"],
                "validation_steps": [],
                "control_ids": [],
            },
        ],
        "limitations": ["No confirmation."],
    }
    ollama = {
        "status": "accepted",
        "metadata": {"elapsed_ms": elapsed_ms},
        "analysis": analysis,
    }
    if not accepted:
        ollama = {
            "status": "validation-failure",
            "metadata": {
                "elapsed_ms": elapsed_ms,
                "api_response_received": True,
                "json_parse_valid": True,
                "schema_valid": True,
                "grounding_valid": False,
            },
            "raw_response": json.dumps(analysis),
            "error": "Control is not applicable to the supplied rule.",
        }
    return {
        "metrics": {"true_positive": 1},
        "ollama_evaluation": {
            "protocol": "grounded",
            "attempts": 1,
            "api_successes": 1,
            "accepted": accepted,
            "api_failures": 0,
            "validation_failures": 1 - accepted,
            "json_parse_valid": 1,
            "schema_valid": accepted,
            "unknown_finding_citations": 0,
            "unknown_evidence_citations": 0,
            "unsupported_cve_mentions": 0,
            "absolute_assertions": 0,
            "unsupported_security_attribution_mentions": 0,
            "containment_action_mentions": 0,
            "unqualified_containment_actions": 0,
            "word_limit_violations": 0,
            "markdown_format_violations": 0,
            "mean_finding_coverage": float(accepted),
            "mean_evidence_coverage": float(accepted),
        },
        "scenarios": [
            {
                "id": "multi-finding",
                "findings": [
                    {"finding_id": "BEH-002-example", "evidence_ids": ["EV-002"]},
                    {"finding_id": "BEH-001-example", "evidence_ids": ["EV-001"]},
                ],
                "ollama": ollama,
            }
        ],
    }


class V2RepetitionsTest(unittest.TestCase):
    def test_aggregates_rates_latency_and_ranking_stability(self) -> None:
        summary = aggregate_results([_result(elapsed_ms=100), _result(elapsed_ms=300, accepted=0)])

        self.assertTrue(summary["detector_stable_across_repetitions"])
        self.assertEqual(summary["ollama"]["api_success_rate"], 1.0)
        self.assertEqual(summary["ollama"]["json_parse_rate"], 1.0)
        self.assertEqual(summary["ollama"]["schema_valid_rate"], 1.0)
        self.assertEqual(summary["ollama"]["accepted_grounding_rate"], 0.5)
        self.assertEqual(summary["ollama"]["latency_ms"]["median"], 200.0)
        ranking = summary["ollama"]["ranking_stability"]["multi-finding"]
        self.assertEqual(ranking["distinct_rankings"], 1)
        self.assertEqual(ranking["exact_agreement_with_mode"], 1.0)

    def test_rejects_mixed_protocols(self) -> None:
        first = _result(elapsed_ms=100)
        second = _result(elapsed_ms=100)
        second["ollama_evaluation"]["protocol"] = "historical"

        with self.assertRaisesRegex(ValueError, "one Ollama protocol"):
            aggregate_results([first, second])


if __name__ == "__main__":
    unittest.main()
