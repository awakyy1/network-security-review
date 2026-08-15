"""Validate and aggregate genuine blinded V1.1 human-rating packages."""

from __future__ import annotations

import argparse
import json
import statistics
from itertools import combinations
from pathlib import Path
from typing import Any

DIMENSIONS = (
    "usefulness",
    "clarity",
    "evidence_fidelity",
    "misinterpretation_risk",
    "recommendation_quality",
)
BINARY_FIELDS = ("contains_unsupported_claim", "suggests_unauthorized_action")


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _weighted_kappa(first: list[int], second: list[int], *, maximum: int, quadratic: bool) -> float | None:
    if len(first) != len(second) or not first:
        raise ValueError("Agreement vectors must be non-empty and equally sized")
    categories = range(0 if maximum == 1 else 1, maximum + 1)

    def weight(left: int, right: int) -> float:
        distance = abs(left - right) / max(maximum - (0 if maximum == 1 else 1), 1)
        return distance * distance if quadratic else float(distance > 0)

    observed = sum(weight(left, right) for left, right in zip(first, second)) / len(first)
    first_counts = {value: first.count(value) / len(first) for value in categories}
    second_counts = {value: second.count(value) / len(second) for value in categories}
    expected = sum(
        first_counts[left] * second_counts[right] * weight(left, right) for left in categories for right in categories
    )
    if expected == 0:
        return 1.0 if observed == 0 else None
    return round(1 - observed / expected, 6)


def _load_and_validate(path: Path) -> tuple[str, dict[str, dict[str, Any]]]:
    package = json.loads(path.read_text(encoding="utf-8"))
    reviewer_id = package.get("reviewer_id")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ValueError(f"Reviewer package lacks a pseudonymous reviewer_id: {path}")
    items = package.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError(f"Reviewer package contains no items: {path}")
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get("item_id")
        ratings = item.get("ratings")
        if not isinstance(item_id, str) or not item_id or item_id in indexed:
            raise ValueError(f"Reviewer package contains an invalid or duplicate item_id: {path}")
        if not isinstance(ratings, dict):
            raise ValueError(f"Item {item_id} lacks ratings")
        for dimension in DIMENSIONS:
            value = ratings.get(dimension)
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
                raise ValueError(f"Item {item_id} has invalid {dimension} rating")
        for field in BINARY_FIELDS:
            if not isinstance(ratings.get(field), bool):
                raise ValueError(f"Item {item_id} has invalid {field} rating")
        note = ratings.get("reviewer_note")
        if not isinstance(note, str) or not note.strip():
            raise ValueError(f"Item {item_id} requires a short reviewer_note")
        indexed[item_id] = ratings
    return reviewer_id.strip(), indexed


def aggregate_human_ratings(package_paths: list[str | Path]) -> dict[str, Any]:
    if len(package_paths) < 2:
        raise ValueError("At least two independent reviewer packages are required")
    loaded = [_load_and_validate(Path(path)) for path in package_paths]
    reviewer_ids = [item[0] for item in loaded]
    if len(reviewer_ids) != len(set(reviewer_ids)):
        raise ValueError("Reviewer IDs must be unique pseudonyms")

    item_sets = [set(item[1]) for item in loaded]
    if any(item_set != item_sets[0] for item_set in item_sets[1:]):
        raise ValueError("Every reviewer must rate the same item IDs")
    item_ids = sorted(item_sets[0])
    reviewer_labels = {reviewer_id: f"reviewer-{index:02d}" for index, reviewer_id in enumerate(reviewer_ids, 1)}

    dimension_results = {}
    for dimension in DIMENSIONS:
        values = [ratings[item_id][dimension] for _, ratings in loaded for item_id in item_ids]
        agreements = []
        for (first_id, first), (second_id, second) in combinations(loaded, 2):
            agreements.append(
                {
                    "reviewers": [reviewer_labels[first_id], reviewer_labels[second_id]],
                    "quadratic_weighted_cohen_kappa": _weighted_kappa(
                        [first[item_id][dimension] for item_id in item_ids],
                        [second[item_id][dimension] for item_id in item_ids],
                        maximum=5,
                        quadratic=True,
                    ),
                }
            )
        dimension_results[dimension] = {
            "ratings": len(values),
            "median": statistics.median(values),
            "q1": round(_percentile(values, 0.25), 6),
            "q3": round(_percentile(values, 0.75), 6),
            "minimum": min(values),
            "maximum": max(values),
            "pairwise_agreement": agreements,
        }

    binary_results = {}
    for field in BINARY_FIELDS:
        values = [int(ratings[item_id][field]) for _, ratings in loaded for item_id in item_ids]
        agreements = []
        for (first_id, first), (second_id, second) in combinations(loaded, 2):
            agreements.append(
                {
                    "reviewers": [reviewer_labels[first_id], reviewer_labels[second_id]],
                    "unweighted_cohen_kappa": _weighted_kappa(
                        [int(first[item_id][field]) for item_id in item_ids],
                        [int(second[item_id][field]) for item_id in item_ids],
                        maximum=1,
                        quadratic=False,
                    ),
                }
            )
        binary_results[field] = {
            "ratings": len(values),
            "positive": sum(values),
            "positive_rate": round(sum(values) / len(values), 6),
            "pairwise_agreement": agreements,
        }

    per_item = []
    for item_id in item_ids:
        per_item.append(
            {
                "item_id": item_id,
                "dimension_medians": {
                    dimension: statistics.median(ratings[item_id][dimension] for _, ratings in loaded)
                    for dimension in DIMENSIONS
                },
                "unsupported_claim_votes": sum(
                    int(ratings[item_id]["contains_unsupported_claim"]) for _, ratings in loaded
                ),
                "unauthorized_action_votes": sum(
                    int(ratings[item_id]["suggests_unauthorized_action"]) for _, ratings in loaded
                ),
                "reviewer_count": len(loaded),
            }
        )

    return {
        "schema_version": "1.0",
        "status": "blinded-ratings-aggregated",
        "reviewer_count": len(loaded),
        "item_count": len(item_ids),
        "ratings_per_dimension": len(loaded) * len(item_ids),
        "dimensions": dimension_results,
        "binary_checks": binary_results,
        "per_item": per_item,
        "privacy": "Reviewer pseudonyms and free-text notes are excluded from this aggregate.",
        "interpretation_boundary": "Ratings assess review quality, not malware truth or operational effectiveness.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-package", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        result = aggregate_human_ratings(arguments.reviewer_package)
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(
        f"Human ratings: reviewers={result['reviewer_count']} items={result['item_count']} "
        f"ratings_per_dimension={result['ratings_per_dimension']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
