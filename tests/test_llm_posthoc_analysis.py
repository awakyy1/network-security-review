from __future__ import annotations

import unittest

from src.ollama_advisor import OUTPUT_SCHEMA, validate_grounded_schema


class LlmPosthocAnalysisTest(unittest.TestCase):
    def test_schema_validator_accepts_priority_order_for_posthoc_ranking(self) -> None:
        priority = {
            "finding_id": "BEH-001-example",
            "priority": "low",
            "rationale": "Observed evidence only.",
            "evidence_ids": ["EVT-001"],
            "validation_steps": [],
            "control_ids": [],
        }
        output = {"summary": "Review.", "priorities": [priority], "limitations": ["Not confirmed."]}
        self.assertIs(validate_grounded_schema(output), output)
        self.assertEqual(OUTPUT_SCHEMA["required"], ["summary", "priorities", "limitations"])


if __name__ == "__main__":
    unittest.main()
