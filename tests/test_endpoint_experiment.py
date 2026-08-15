from __future__ import annotations

import tempfile
import unittest

from src.endpoint_experiment import run_endpoint_experiment


class EndpointExperimentTest(unittest.TestCase):
    def test_frozen_truth_matrix_and_inventory_ablation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_endpoint_experiment("research/v1.1/endpoint-scenarios.json", directory)

        self.assertEqual(result["confusion"]["true_positive"], 1)
        self.assertEqual(result["confusion"]["true_negative"], 4)
        self.assertEqual(result["confusion"]["false_positive"], 0)
        self.assertEqual(result["confusion"]["false_negative"], 0)
        self.assertTrue(result["inventory_ablation"]["predictions_identical"])
        self.assertEqual(result["inventory_ablation"]["known_asset_context_added"], 5)
        positive = next(item for item in result["truth_matrix"] if item["expected_beh_004"])
        self.assertEqual(positive["evidence_ids"], ["EPT-P01", "EPT-P02"])


if __name__ == "__main__":
    unittest.main()
