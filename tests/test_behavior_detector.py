from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.behavior_detector import BehaviorDetector, inventory_context
from src.nmap_to_zabbix import NmapParser
from src.telemetry import load_telemetry


class BehaviorDetectorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        manifest_path = Path("research/v2/scenarios.json")
        cls.base_directory = manifest_path.parent
        cls.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        nmap_path = (cls.base_directory / cls.manifest["nmap_input"]).resolve()
        parser = NmapParser(nmap_path)
        cls.detector = BehaviorDetector(inventory_context(parser.parse_xml()))

    def test_scenarios_match_the_expected_transparent_rules(self) -> None:
        expected_predictions = {
            "benign-web": set(),
            "benign-updater": {"BEH-001"},
            "emulated-beacon": {"BEH-001"},
            "emulated-service-discovery": {"BEH-002"},
            "emulated-asymmetric-egress": {"BEH-003"},
            "emulated-tool-transfer": {"BEH-004"},
        }
        for scenario in self.manifest["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                events = load_telemetry(self.base_directory / scenario["telemetry"])
                findings = self.detector.analyze(events)
                self.assertEqual({item.rule_id for item in findings}, expected_predictions[scenario["id"]])
                for finding in findings:
                    self.assertFalse(finding.confirmed_malware)
                    self.assertFalse(finding.confirmed_vulnerability)
                    self.assertFalse(finding.automatic_response_authorized)
                    self.assertTrue(finding.evidence_ids)

    def test_correlates_behavior_with_observed_nmap_asset_context(self) -> None:
        events = load_telemetry(self.base_directory / "fixtures/emulated-beacon.jsonl")
        finding = self.detector.analyze(events)[0]

        self.assertTrue(finding.asset_context["known_asset"])
        self.assertEqual(finding.asset_context["hostname"], "servidor-web.empresa.local")
        self.assertGreater(len(finding.asset_context["observed_services"]), 0)


if __name__ == "__main__":
    unittest.main()
