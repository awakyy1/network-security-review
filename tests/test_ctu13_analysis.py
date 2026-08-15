from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from src.ctu13_analysis import (
    _beh_001_diagnostics,
    preserve_analysis,
    summarize_distribution,
    unit_rule_features,
)
from src.telemetry import TelemetryEvent


def _connection(index: int, *, destination: str, sent: int = 100, received: int = 50) -> TelemetryEvent:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return TelemetryEvent.from_mapping(
        {
            "event_id": f"EVT-{index:03d}",
            "timestamp": (start + timedelta(seconds=index * 10)).isoformat(),
            "host": "fixture-host",
            "event_type": "network_connection",
            "source": "fixture",
            "process": "fixture-process",
            "destination_ip": destination,
            "destination_port": 443,
            "protocol": "tcp",
            "bytes_sent": sent,
            "bytes_received": received,
        }
    )


class CTU13AnalysisTest(unittest.TestCase):
    def test_extracts_rule_features_without_changing_detector_thresholds(self) -> None:
        events = [_connection(index, destination=f"198.51.100.{index}") for index in range(8)]
        events.append(_connection(20, destination="203.0.113.1", sent=2_000_000, received=100_000))

        features = unit_rule_features(events)

        self.assertEqual(features["maximum_distinct_endpoints_in_60_seconds"], 7)
        self.assertEqual(features["connections_meeting_1mb_sent"], 1)
        self.assertEqual(features["connections_meeting_10_to_1_ratio"], 1)
        self.assertEqual(features["connections_meeting_both_beh_003_thresholds"], 1)

    def test_distribution_summary_uses_deterministic_linear_quantiles(self) -> None:
        summary = summarize_distribution([1, 2, 3, 4])

        self.assertEqual(summary["count"], 4)
        self.assertEqual(summary["q1"], 1.75)
        self.assertEqual(summary["median"], 2.5)
        self.assertEqual(summary["q3"], 3.25)

    def test_beh_001_diagnostics_separates_count_interval_and_variation_failures(self) -> None:
        def record(maximum: int, eligible: int, coefficient: float | None) -> dict[str, object]:
            return {
                "truth": "botnet-origin",
                "features": {
                    "periodicity": {
                        "maximum_connections_to_one_endpoint": maximum,
                        "eligible_endpoint_groups": eligible,
                        "minimum_interval_cv": coefficient,
                    }
                },
            }

        diagnostics = _beh_001_diagnostics(
            [record(5, 0, None), record(6, 0, None), record(6, 1, 0.2), record(6, 1, 0.1)],
            "botnet-origin",
        )

        self.assertEqual(diagnostics["below_six_connections_to_one_endpoint"], 1)
        self.assertEqual(diagnostics["six_connections_but_no_eligible_mean_interval"], 1)
        self.assertEqual(diagnostics["eligible_mean_interval_but_cv_above_0_15"], 1)
        self.assertEqual(diagnostics["meets_beh_001_thresholds"], 1)

    @patch("src.ctu13_analysis.sha256_file", return_value="frozen-hash")
    def test_preservation_refuses_nonempty_destination(self, _hash: object) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "output"
            source.mkdir()
            (source / "ctu13-window-analysis.json").write_text(
                json.dumps(
                    {
                        "analysis_role": "development_and_historical_holdout_diagnostics",
                        "scientific_state": {"repository_base_commit": "abc", "files": []},
                    }
                ),
                encoding="utf-8",
            )
            (source / "ctu13-window-analysis.md").write_text("report", encoding="utf-8")
            destination = root / "preserved"
            destination.mkdir()
            (destination / "existing.json").write_text("{}", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "not empty"):
                preserve_analysis(source, destination, root)
