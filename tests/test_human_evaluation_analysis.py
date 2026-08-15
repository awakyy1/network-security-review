from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.human_evaluation_analysis import DIMENSIONS, aggregate_human_ratings


def _package(reviewer: str, offset: int = 0) -> dict:
    items = []
    for index in range(3):
        ratings = {dimension: min(5, 2 + index + offset) for dimension in DIMENSIONS}
        ratings.update(
            {
                "contains_unsupported_claim": index == 0,
                "suggests_unauthorized_action": index == 1,
                "reviewer_note": "Independent short rationale.",
            }
        )
        items.append({"item_id": f"item-{index}", "ratings": ratings})
    return {"reviewer_id": reviewer, "items": items}


class HumanEvaluationAnalysisTest(unittest.TestCase):
    def test_requires_real_complete_packages(self) -> None:
        with self.assertRaisesRegex(ValueError, "At least two"):
            aggregate_human_ratings([])

    def test_weighted_and_binary_agreement_are_reported_without_reviewer_ids(self) -> None:
        first = _package("private-a")
        second = _package("private-b")
        temporary_root = Path(".tmp")
        temporary_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as temporary:
            first_path = Path(temporary) / "first.json"
            second_path = Path(temporary) / "second.json"
            first_path.write_text(json.dumps(first), encoding="utf-8")
            second_path.write_text(json.dumps(second), encoding="utf-8")
            result = aggregate_human_ratings([first_path, second_path])

        self.assertEqual(result["reviewer_count"], 2)
        self.assertEqual(result["item_count"], 3)
        self.assertEqual(result["ratings_per_dimension"], 6)
        self.assertEqual(
            result["dimensions"]["usefulness"]["pairwise_agreement"][0]["quadratic_weighted_cohen_kappa"],
            1.0,
        )
        self.assertNotIn("private-a", json.dumps(result))
        self.assertNotIn("reviewer_note", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
