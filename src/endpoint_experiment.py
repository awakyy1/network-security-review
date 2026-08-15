"""Evaluate BEH-004 on frozen inert endpoint-lineage fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .behavior_detector import BehaviorDetector, inventory_context
from .ctu13_acquire import sha256_file
from .nmap_to_zabbix import NmapParser
from .telemetry import load_telemetry


def run_endpoint_experiment(manifest_path: str | Path, output_directory: str | Path) -> dict[str, Any]:
    manifest_file = Path(manifest_path).resolve()
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if manifest.get("status") != "frozen-functional-fixtures":
        raise ValueError("Endpoint manifest must be frozen functional fixtures")
    nmap_file = (manifest_file.parent / manifest["nmap_input"]).resolve()
    inventory = inventory_context(NmapParser(nmap_file).parse_xml())
    with_inventory = BehaviorDetector(inventory)
    without_inventory = BehaviorDetector()

    rows = []
    confusion = {"true_positive": 0, "false_positive": 0, "false_negative": 0, "true_negative": 0}
    for scenario in manifest["scenarios"]:
        telemetry_file = (manifest_file.parent / scenario["telemetry"]).resolve()
        events = load_telemetry(telemetry_file)
        contextual = [item for item in with_inventory.analyze(events) if item.rule_id == "BEH-004"]
        context_free = [item for item in without_inventory.analyze(events) if item.rule_id == "BEH-004"]
        contextual_ids = [item.finding_id for item in contextual]
        context_free_ids = [item.finding_id for item in context_free]
        if contextual_ids != context_free_ids:
            raise ValueError(f"Nmap inventory changed BEH-004 predictions for {scenario['id']}")
        expected = bool(scenario["expected_beh_004"])
        predicted = bool(contextual)
        outcome = (
            "true_positive"
            if expected and predicted
            else "false_negative"
            if expected
            else "false_positive"
            if predicted
            else "true_negative"
        )
        confusion[outcome] += 1
        rows.append(
            {
                "id": scenario["id"],
                "telemetry_sha256": sha256_file(telemetry_file),
                "event_count": len(events),
                "expected_beh_004": expected,
                "predicted_beh_004": predicted,
                "outcome": outcome,
                "finding_ids": contextual_ids,
                "evidence_ids": [event_id for item in contextual for event_id in item.evidence_ids],
                "inventory_known_asset_with_nmap": (
                    contextual[0].asset_context["known_asset"] if contextual else events[0].host in inventory
                ),
                "inventory_known_asset_without_nmap": (
                    context_free[0].asset_context["known_asset"] if context_free else False
                ),
            }
        )

    result = {
        "schema_version": "1.0",
        "evidence_role": "functional-endpoint-lineage-validation",
        "manifest": manifest_file.name,
        "manifest_sha256": sha256_file(manifest_file),
        "nmap_sha256": sha256_file(nmap_file),
        "truth_matrix": rows,
        "confusion": confusion,
        "inventory_ablation": {
            "predictions_identical": True,
            "known_asset_context_added": sum(item["inventory_known_asset_with_nmap"] for item in rows),
            "interpretation": (
                "Nmap enriched asset context but did not create, remove, or reclassify a BEH-004 finding."
            ),
        },
        "automatic_actions_executed": 0,
        "claim_boundary": (
            "Constructed inert fixtures validate rule logic and evidence lineage, not endpoint detection accuracy."
        ),
    }
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    (output / "endpoint-beh004.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (output / "endpoint-beh004.md").write_text(_markdown(result), encoding="utf-8")
    return result


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        "# BEH-004 endpoint truth matrix",
        "",
        "| Scenario | Expected | Predicted | Outcome |",
        "|---|---:|---:|---|",
    ]
    for item in result["truth_matrix"]:
        lines.append(
            f"| {item['id']} | {str(item['expected_beh_004']).lower()} | "
            f"{str(item['predicted_beh_004']).lower()} | {item['outcome']} |"
        )
    lines.extend(["", result["claim_boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        result = run_endpoint_experiment(arguments.manifest, arguments.output_dir)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(json.dumps(result["confusion"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
