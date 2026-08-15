from __future__ import annotations

import unittest

from src.article_tables import (
    adversarial_llm_table,
    adversarial_matrix_table,
    confirmatory_ctu13_table,
    counterfactual_policy_table,
    endpoint_truth_table,
    environment_comparison_table,
    external_metrics_table,
    llm_ablation_table,
    llm_supplement_table,
    phase_a_table,
    primary_llm_matrix_table,
    repeated_llm_table,
    retrospective_error_examples_table,
    retrospective_threshold_table,
    retrospective_window_table,
    second_dataset_table,
)


class ArticleTablesTest(unittest.TestCase):
    def test_environment_table_marks_v1_1_as_development_context(self) -> None:
        table = environment_comparison_table(
            {
                "environments": [
                    {
                        "research_state": "V1.0 initial run",
                        "operating_system": "Windows 11",
                        "cpu": "Intel CPU",
                        "cpu_topology": "12 logical processors",
                        "memory_gib": 15.7,
                        "inference_device": "CPU",
                    },
                    {
                        "research_state": "V1.1 development environment",
                        "operating_system": "Windows 10",
                        "cpu": "AMD Ryzen 5 5600",
                        "cpu_topology": "6 cores / 12 logical processors",
                        "memory_gib": 31.9,
                        "inference_device": "NVIDIA RTX 3060, 12 GiB VRAM",
                    },
                ]
            }
        )

        self.assertIn("V1.0 initial run", table)
        self.assertIn("V1.1 development environment", table)
        self.assertIn("not evidence that a V1.1 experiment had already run", table)
        self.assertIn(r"\label{tab:environment-comparison}", table)

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
        self.assertIn("Reconstructed free text & 50 & 50 & 0 & 0 & 0 & N/A", table)
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

    def test_retrospective_tables_keep_diagnostic_boundary_and_examples(self) -> None:
        metrics = {
            "true_positive": 3,
            "false_positive": 2,
            "false_negative": 1,
            "true_negative": 4,
            "f1": 0.666667,
            "specificity": 0.666667,
            "matthews_correlation_coefficient": 0.408248,
        }
        diagnostics = {
            "botnet-origin": {
                "units": 4,
                "below_six_connections_to_one_endpoint": 2,
                "six_connections_but_no_eligible_mean_interval": 1,
                "eligible_mean_interval_but_cv_above_0_15": 1,
                "meets_beh_001_thresholds": 0,
            },
            "normal-origin": {
                "units": 6,
                "below_six_connections_to_one_endpoint": 1,
                "six_connections_but_no_eligible_mean_interval": 1,
                "eligible_mean_interval_but_cv_above_0_15": 1,
                "meets_beh_001_thresholds": 3,
            },
        }
        beh_003 = {
            truth: {
                "units_meeting_1mb_sent": 0,
                "units_meeting_10_to_1_ratio": count,
                "units_meeting_both_thresholds": 0,
            }
            for truth, count in (("botnet-origin", 2), ("normal-origin", 1))
        }
        distributions = {
            truth: {"maximum_distinct_endpoints_in_60_seconds": {"median": median, "maximum": maximum}}
            for truth, median, maximum in (("botnet-origin", 2, 9), ("normal-origin", 5, 11))
        }
        examples = {
            "true_positive": {
                "rule_ids": ["BEH-002"],
                "evidence_ids": ["E1", "E2"],
                "features": {
                    "event_count": 8,
                    "maximum_distinct_endpoints_in_60_seconds": 9,
                    "maximum_bytes_sent_on_one_connection": 2048,
                    "maximum_sent_received_ratio": 12.0,
                },
            },
            "false_positive": {
                "rule_ids": ["BEH-001"],
                "evidence_ids": ["E3"],
                "features": {
                    "event_count": 6,
                    "maximum_distinct_endpoints_in_60_seconds": 1,
                    "maximum_bytes_sent_on_one_connection": 1024,
                    "maximum_sent_received_ratio": 2.0,
                },
            },
            "false_negative": {
                "rule_ids": [],
                "evidence_ids": ["E4"],
                "features": {
                    "event_count": 1,
                    "maximum_distinct_endpoints_in_60_seconds": 1,
                    "maximum_bytes_sent_on_one_connection": 512,
                    "maximum_sent_received_ratio": 0.5,
                },
            },
        }
        result = {
            "analyses": [
                {
                    "role": "holdout",
                    "family": "NSIS.ay",
                    "window_seconds": 300,
                    "metrics": metrics,
                    "beh_001_threshold_diagnostics": diagnostics,
                    "beh_003_threshold_diagnostics": beh_003,
                    "feature_distributions": distributions,
                    "examples": examples,
                }
            ]
        }

        window_table = retrospective_window_table(result)
        threshold_table = retrospective_threshold_table(result)
        examples_table = retrospective_error_examples_table(result)

        self.assertIn("Holdout & NSIS.ay & 300 & 10 & 3 & 2 & 1 & 4", window_table)
        self.assertIn("diagnostic rather than confirmatory", window_table)
        self.assertIn("Holdout & botnet-origin & 4 & 2 & 1 & 1 & 0 & 2 & 9 & 0 & 2 & 0", threshold_table)
        self.assertIn("TP & BEH-002 & 8 & 2 & 9 & 2.0 & 12.000", examples_table)
        self.assertIn("FN & N/A & 1 & 1 & 1 & 0.5 & 0.500", examples_table)

    def test_confirmatory_table_never_pools_development_and_holdout(self) -> None:
        development_metrics = {
            "true_positive": 0,
            "false_positive": 2,
            "false_negative": 3,
            "true_negative": 13,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "specificity": 0.866667,
            "matthews_correlation_coefficient": -0.158114,
        }
        holdout_metrics = {
            "true_positive": 24,
            "false_positive": 29,
            "false_negative": 3,
            "true_negative": 49,
            "precision": 0.45283,
            "recall": 0.888889,
            "f1": 0.6,
            "specificity": 0.628205,
            "matthews_correlation_coefficient": 0.452021,
        }
        table = confirmatory_ctu13_table(
            {"source": {"family": "RBot"}, "selected": {"metrics": development_metrics}},
            {"evaluation": {"family": "DonBot", "metrics": holdout_metrics}},
        )

        self.assertIn("Development & RBot & 18 & 0 & 2 & 3 & 13", table)
        self.assertIn("Confirmatory holdout & DonBot & 105 & 24 & 29 & 3 & 49", table)
        self.assertIn("metrics are not pooled", table)

    def test_second_dataset_table_marks_construct_boundary(self) -> None:
        table = second_dataset_table(
            {
                "metrics": {
                    "true_positive": 96,
                    "false_positive": 48,
                    "false_negative": 1,
                    "true_negative": 384,
                    "precision": 0.666667,
                    "recall": 0.989691,
                    "f1": 0.79668,
                    "specificity": 0.888889,
                    "matthews_correlation_coefficient": 0.763831,
                }
            }
        )

        self.assertIn("Implementation transfer & 529 & 96 & 48 & 1 & 384", table)
        self.assertIn("not independent", table)
        self.assertIn("not pooled with CTU-13", table)

    def test_endpoint_table_separates_inventory_context_from_prediction(self) -> None:
        table = endpoint_truth_table(
            {
                "truth_matrix": [
                    {
                        "id": "same-process-within-window",
                        "expected_beh_004": True,
                        "predicted_beh_004": True,
                        "outcome": "true_positive",
                    }
                ]
            }
        )

        self.assertIn("Same process within window & Yes & Yes & TRUE POSITIVE", table)
        self.assertIn("decisions were identical without inventory", table)
        self.assertIn("not endpoint accuracy", table)

    def test_counterfactual_table_exposes_two_rule_tradeoff(self) -> None:
        policy = {
            "automatic_block_on_alert": {
                "containment_actions": 12,
                "normal_origin_actions": 4,
                "botnet_origin_without_action": 2,
            },
            "automatic_block_after_two_rules": {
                "containment_actions": 3,
                "normal_origin_actions": 1,
                "botnet_origin_without_action": 8,
            },
        }
        result = {
            "datasets": {
                "historical-nsis-ay": {"policies": policy},
                "confirmatory-donbot": {"policies": policy},
                "synthetic-implementation-transfer": {"policies": policy},
            }
        }

        table = counterfactual_policy_table(result)

        self.assertIn("Historical NSIS.ay & 12 & 4 & 2 & 3 & 1 & 8", table)
        self.assertIn("zero actions", table)

    def test_primary_matrix_table_preserves_api_and_validator_failures(self) -> None:
        table = primary_llm_matrix_table(
            {
                "cells": [
                    {
                        "model": "qwen3:8b",
                        "prompt_variant": "checklist-v1",
                        "ollama": {
                            "attempts": 20,
                            "api_successes": 0,
                            "json_parse_valid": 0,
                            "schema_valid": 0,
                            "accepted": 0,
                            "mean_finding_coverage": 0.0,
                            "mean_evidence_coverage": 0.0,
                        },
                    }
                ]
            }
        )

        self.assertIn("qwen3:8b & checklist-v1 & 20 & 0 & 0 & 0 & 0 & 0.000 & 0.000", table)
        self.assertIn("API failures contribute zero", table)

    def test_ablation_table_distinguishes_new_and_reused_calls(self) -> None:
        condition = {
            "condition": "api-format-removed",
            "new_calls": 12,
            "ollama": {
                "attempts": 12,
                "api_successes": 12,
                "json_parse_valid": 0,
                "schema_valid": 0,
                "accepted": 0,
                "mean_finding_coverage": 0.0,
                "mean_evidence_coverage": 0.0,
            },
        }
        table = llm_ablation_table({"conditions": [condition]})
        self.assertIn("API format removed & 12 & 12 & 12 & 0 & 0 & 0 & 0.000 & 0.000", table)
        self.assertIn("descriptive sensitivity only", table)

    def test_supplement_table_separates_compliance_and_ranking_estimability(self) -> None:
        table = llm_supplement_table(
            {
                "per_model": [
                    {
                        "model": "llama3-2-3b",
                        "attempts": 3,
                        "api_responses": 3,
                        "json_parse_valid": 3,
                        "schema_valid": 3,
                        "grounding_accepted": 0,
                        "output_limit_reached": 0,
                        "complete_known_finding_rankings": 3,
                        "ranking_exact_agreement_with_mode": 1.0,
                    }
                ]
            }
        )
        self.assertIn("llama3-2-3b & 3 & 3 & 3 & 3 & 0 & 0 & 3 & 1.000", table)
        self.assertIn("repeatability is not semantic correctness", table)

    def test_adversarial_table_uses_corrected_eligible_denominators(self) -> None:
        table = adversarial_matrix_table(
            {
                "models": {
                    "model-a": {
                        "attempted_calls": 15,
                        "api_responses": 3,
                        "api_failures": 12,
                        "pairs_with_both_api_responses": 1,
                        "pairs_with_both_parseable": 1,
                    }
                },
                "metrics": {
                    "accepted_status_changed": {"changed": 1, "eligible_pairs": 1},
                    "priority_label_changed": {"changed": 0, "eligible_pairs": 1},
                    "control_set_changed": {"changed": 0, "eligible_pairs": 1},
                    "finding_order_changed": {"changed": 0, "eligible_pairs": 1},
                    "cited_evidence_set_changed": {"changed": 0, "eligible_pairs": 1},
                    "unsupported_claim_flag_changed": {"changed": 0, "eligible_pairs": 1},
                },
            }
        )
        self.assertIn("model-a & 15 & 3 & 12 & 1 & 1", table)
        self.assertIn("Two API failures are not treated as an unchanged decision", table)


if __name__ == "__main__":
    unittest.main()
