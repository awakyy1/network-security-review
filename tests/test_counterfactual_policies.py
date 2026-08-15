from __future__ import annotations

import unittest

from src.counterfactual_policies import evaluate_policies


class CounterfactualPoliciesTest(unittest.TestCase):
    def test_separates_automatic_actions_from_approval_gated_proposals(self) -> None:
        result = evaluate_policies(
            {
                "positive": 10,
                "negative": 20,
                "positive_alerted": 8,
                "negative_alerted": 4,
                "positive_multi_rule": 2,
                "negative_multi_rule": 1,
            }
        )

        self.assertEqual(result["automatic_block_on_alert"]["containment_actions"], 12)
        self.assertEqual(result["automatic_block_after_two_rules"]["containment_actions"], 3)
        self.assertEqual(result["automatic_block_after_two_rules"]["botnet_origin_without_action"], 8)
        self.assertEqual(result["analyst_approval"]["containment_actions"], 0)
        self.assertEqual(result["isolation_after_independent_confirmation"]["containment_actions"], 0)


if __name__ == "__main__":
    unittest.main()
