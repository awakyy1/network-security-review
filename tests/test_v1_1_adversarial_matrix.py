from __future__ import annotations

import unittest

from src.v1_1_adversarial_matrix import compare_pair


def _result(priority: str, control: str) -> dict[str, object]:
    return {
        "status": "accepted",
        "analysis": {
            "priorities": [
                {
                    "finding_id": "BEH-001-example",
                    "priority": priority,
                    "control_ids": [control],
                    "evidence_ids": ["EV-001"],
                }
            ]
        },
        "audit": {"unsupported_claim_flag": False, "unsupported_claim_categories": []},
    }


class V11AdversarialMatrixTest(unittest.TestCase):
    def test_pair_comparison_measures_decisions_not_literal_echo_only(self) -> None:
        influence = compare_pair(
            _result("high", "collect-more-telemetry"),
            _result("medium", "validate-process-owner"),
        )

        self.assertTrue(influence["priority_label_changed"])
        self.assertTrue(influence["control_set_changed"])
        self.assertFalse(influence["cited_evidence_set_changed"])
        self.assertFalse(influence["finding_order_changed"])


if __name__ == "__main__":
    unittest.main()
