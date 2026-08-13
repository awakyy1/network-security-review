from __future__ import annotations

import unittest

from src.article_tables import adversarial_llm_table, external_metrics_table, phase_a_table, repeated_llm_table


class ArticleTablesTest(unittest.TestCase):
    def test_phase_a_table_uses_preserved_metrics(self) -> None:
        table = phase_a_table(
            {
                "metrics": {
                    "true_positive": 4,
                    "false_positive": 1,
                    "false_negative": 0,
                    "true_negative": 19,
                    "precision": 0.8,
                    "recall": 1.0,
                    "f1": 0.888889,
                    "specificity": 0.95,
                }
            }
        )

        self.assertIn("4 & 1 & 0 & 19 & 0.800 & 1.000 & 0.889 & 0.950", table)
        self.assertIn(r"\label{tab:phase-a}", table)

    def test_external_table_keeps_development_and_holdout_separate(self) -> None:
        metrics = {
            "true_positive": 1,
            "false_positive": 2,
            "false_negative": 3,
            "true_negative": 4,
            "precision": 0.333333,
            "recall": 0.25,
            "f1": 0.285714,
            "specificity": 0.666667,
            "matthews_correlation_coefficient": -0.1,
        }
        table = external_metrics_table(
            {
                "sources": [
                    {"role": "development", "family": "Virut", "metrics": metrics},
                    {"role": "holdout", "family": "NSIS.ay", "metrics": metrics},
                ]
            }
        )

        self.assertIn("Development & Virut", table)
        self.assertIn("Holdout & NSIS.ay", table)
        self.assertIn(r"\label{tab:ctu13-metrics}", table)

    def test_repeated_llm_table_separates_traceability_and_acceptance(self) -> None:
        table = repeated_llm_table(
            {
                "phase_a": {
                    "grounded": {
                        "calls": 50,
                        "api_responses": 50,
                        "exact_finding_coverage": 50,
                        "exact_evidence_coverage": 50,
                        "accepted": 40,
                        "policy_rejections": 10,
                    },
                    "historical": {
                        "calls": 50,
                        "api_responses": 50,
                        "exact_finding_coverage": 0,
                        "exact_evidence_coverage": 0,
                        "grounding_valid": 0,
                    },
                }
            }
        )

        self.assertIn("Grounded schema 1.1 & 50 & 50 & 50 & 50 & 40 & 10", table)
        self.assertIn("Reconstructed free text & 50 & 50 & 0 & 0 & 0 & --", table)
        self.assertIn(r"40 & 10 \\", table)

    def test_adversarial_table_reports_injection_and_policy_results(self) -> None:
        table = adversarial_llm_table(
            {
                "adversarial": {
                    "calls": 10,
                    "schema_valid": 10,
                    "exact_evidence_coverage": 10,
                    "fake_id_echo_responses": 0,
                    "absolute_assertion_responses": 0,
                    "accepted": 9,
                }
            }
        )

        self.assertIn("10 & 10 & 10 & 0 & 0 & 9", table)
        self.assertIn(r"0 & 0 & 9 \\", table)
        self.assertIn(r"\label{tab:llm-adversarial}", table)


if __name__ == "__main__":
    unittest.main()
