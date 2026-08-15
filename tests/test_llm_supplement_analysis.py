from __future__ import annotations

import unittest

from src.llm_supplement_analysis import analyze_supplement


class LlmSupplementAnalysisTest(unittest.TestCase):
    def test_preserved_supplement_denominators_and_context_fit(self) -> None:
        root = "research/v1.1/results/llm-supplement-matrix-2026-08-15"
        result = analyze_supplement(f"{root}/matrix-summary.json", root)

        self.assertEqual(result["attempts"], 9)
        self.assertEqual(result["api_responses"], 9)
        self.assertEqual(result["json_parse_valid"], 4)
        self.assertEqual(result["schema_valid"], 4)
        self.assertEqual(result["grounding_accepted"], 0)
        self.assertEqual(result["input_and_reserved_output_fit_context"], 9)
        self.assertEqual(result["output_limit_reached"], 5)
        self.assertEqual(result["automatic_actions_executed"], 0)


if __name__ == "__main__":
    unittest.main()
