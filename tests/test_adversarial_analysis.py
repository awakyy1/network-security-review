from __future__ import annotations

import unittest

from src.adversarial_analysis import reaggregate_adversarial


def _response(status: str, *, audit: bool = True) -> dict[str, object]:
    result: dict[str, object] = {"status": status}
    if audit:
        result["audit"] = {}
    return result


class AdversarialAnalysisTest(unittest.TestCase):
    def test_api_failure_pair_is_not_counted_as_unchanged_decision(self) -> None:
        influence = {
            "both_parseable": False,
            "accepted_status_changed": False,
            "priority_label_changed": False,
            "control_set_changed": False,
            "finding_order_changed": False,
            "cited_evidence_set_changed": False,
            "unsupported_claim_flag_changed": False,
        }
        result = reaggregate_adversarial(
            {
                "records": [
                    {
                        "model": "model-a",
                        "attack": _response("api-failure", audit=False),
                        "sanitized": _response("api-failure", audit=False),
                        "influence": influence,
                    },
                    {
                        "model": "model-a",
                        "attack": _response("accepted"),
                        "sanitized": _response("validation-failure"),
                        "influence": {**influence, "both_parseable": True, "accepted_status_changed": True},
                    },
                    {"model": "model-a", "control": _response("accepted")},
                ]
            }
        )
        self.assertEqual(result["attempted_calls"], 5)
        self.assertEqual(result["api_failures"], 2)
        self.assertEqual(result["pairs_with_both_api_responses"], 1)
        self.assertEqual(result["metrics"]["accepted_status_changed"], {"changed": 1, "eligible_pairs": 1})


if __name__ == "__main__":
    unittest.main()
