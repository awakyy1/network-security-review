from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.human_evaluation import prepare_blinded_package


class HumanEvaluationTest(unittest.TestCase):
    def test_refuses_incomplete_matrix_instead_of_inventing_items(self) -> None:
        with self.assertRaisesRegex(ValueError, "nine completed"):
            prepare_blinded_package("research/v1.1", "unused.json", "unused-map.json")

    def test_recovery_outputs_complete_blinded_package_without_exposing_source(self) -> None:
        temporary_root = Path(".tmp")
        temporary_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as temporary:
            output = Path(temporary) / "reviewer.json"
            mapping_output = Path(temporary) / "mapping.json"
            package = prepare_blinded_package(
                "research/v1.1/results/llm-primary-matrix-2026-08-15",
                output,
                mapping_output,
                recovery_map="research/v1.1/human-evaluation-recovery-map-2026-08-15.json",
            )
            mapping = json.loads(mapping_output.read_text(encoding="utf-8"))

            self.assertEqual(len(package["items"]), 36)
            self.assertEqual(mapping["recovery_substitutions"], 5)
            self.assertEqual(len(mapping["mapping"]), 36)
            self.assertNotIn("response_source", package["items"][0])


if __name__ == "__main__":
    unittest.main()
