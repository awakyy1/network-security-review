from __future__ import annotations

import unittest

from src.v1_1_ablation_matrix import REDUCED_SYSTEM_PROMPT, _request_payload


class V11AblationMatrixTest(unittest.TestCase):
    def test_temperature_condition_changes_only_temperature(self) -> None:
        payload = _request_payload(
            model="model:test",
            prompt="evidence",
            condition="temperature-0.7",
            context_length=4096,
            maximum_output_tokens=700,
        )
        self.assertEqual(payload["options"]["temperature"], 0.7)
        self.assertIn("format", payload)

    def test_api_format_condition_omits_format(self) -> None:
        payload = _request_payload(
            model="model:test",
            prompt="evidence",
            condition="api-format-removed",
            context_length=4096,
            maximum_output_tokens=700,
        )
        self.assertNotIn("format", payload)
        self.assertEqual(payload["options"]["temperature"], 0)

    def test_reduced_grounding_selects_reduced_system_text(self) -> None:
        payload = _request_payload(
            model="model:test",
            prompt="evidence",
            condition="grounding-language-reduced",
            context_length=4096,
            maximum_output_tokens=700,
        )
        self.assertEqual(payload["system"], REDUCED_SYSTEM_PROMPT)
        self.assertIn("format", payload)


if __name__ == "__main__":
    unittest.main()
