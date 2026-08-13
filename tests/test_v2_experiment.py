from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

from src.ollama_advisor import OllamaOutputError
from src.v2_experiment import run_benchmark


class V2ExperimentTest(unittest.TestCase):
    def test_benchmark_preserves_the_intentional_hard_negative(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result = run_benchmark("research/v2/scenarios.json", output)

            self.assertEqual(result["metrics"]["true_positive"], 4)
            self.assertEqual(result["metrics"]["false_positive"], 1)
            self.assertEqual(result["metrics"]["false_negative"], 0)
            self.assertEqual(result["metrics"]["true_negative"], 19)
            self.assertEqual(result["metrics"]["precision"], 0.8)
            self.assertEqual(result["metrics"]["recall"], 1.0)
            self.assertEqual(result["metrics"]["f1"], 0.888889)
            self.assertEqual(result["metrics"]["specificity"], 0.95)

            updater = next(item for item in result["scenarios"] if item["id"] == "benign-updater")
            self.assertEqual(updater["false_positive"], ["BEH-001"])
            self.assertTrue((output / "benchmark.md").is_file())
            json_report = json.loads((output / "benchmark.json").read_text(encoding="utf-8"))
            self.assertEqual(json_report["metrics"], result["metrics"])
            self.assertIn("does not execute malware", (output / "benchmark.md").read_text(encoding="utf-8"))

    @patch("src.v2_experiment.OllamaAdvisor.analyze", side_effect=requests.Timeout("controlled timeout"))
    def test_benchmark_preserves_per_scenario_ollama_failures(self, _analyze: object) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_benchmark("research/v2/scenarios.json", directory, ollama_model="test-model")

        evaluation = result["ollama_evaluation"]
        self.assertEqual(evaluation["attempts"], 5)
        self.assertEqual(evaluation["accepted"], 0)
        self.assertEqual(evaluation["api_failures"], 5)
        self.assertEqual(evaluation["accepted_grounding_rate"], 0.0)

    @patch(
        "src.v2_experiment.OllamaAdvisor.analyze",
        side_effect=OllamaOutputError(
            "unknown evidence",
            raw_response='{"evidence_ids":["FAKE-999"]}',
            metadata={"grounding_valid": False},
        ),
    )
    def test_benchmark_preserves_rejected_raw_model_output(self, _analyze: object) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_benchmark(
                "research/v2/adversarial-scenarios.json",
                directory,
                ollama_model="test-model",
            )

        ollama = result["scenarios"][0]["ollama"]
        evaluation = result["ollama_evaluation"]
        self.assertEqual(ollama["status"], "validation-failure")
        self.assertEqual(ollama["raw_response"], '{"evidence_ids":["FAKE-999"]}')
        self.assertFalse(ollama["metadata"]["grounding_valid"])
        self.assertEqual(evaluation["api_successes"], 1)
        self.assertEqual(evaluation["accepted"], 0)

    def test_adversarial_manifest_is_separate_and_detectable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_benchmark("research/v2/adversarial-scenarios.json", directory)

        self.assertEqual(len(result["scenarios"]), 1)
        scenario = result["scenarios"][0]
        self.assertEqual(scenario["predicted_rule_ids"], ["BEH-001"])
        self.assertEqual(result["metrics"]["true_positive"], 1)
        self.assertEqual(result["metrics"]["false_positive"], 0)


if __name__ == "__main__":
    unittest.main()
