from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.telemetry import TelemetryEvent, load_telemetry


class TelemetryTest(unittest.TestCase):
    def test_loads_normalized_timezone_aware_events(self) -> None:
        fixture = Path("research/v2/fixtures/emulated-tool-transfer.jsonl")
        events = load_telemetry(fixture)

        self.assertEqual([item.event_id for item in events], ["DWN-001", "DWN-002"])
        self.assertIsNotNone(events[0].timestamp.tzinfo)
        self.assertEqual(events[0].bytes_received, 600_000)
        self.assertEqual(events[1].event_type, "file_create")

    def test_rejects_duplicate_evidence_identifiers(self) -> None:
        line = (
            '{"event_id":"DUP-1","timestamp":"2026-01-15T12:00:00Z","host":"lab-host",'
            '"event_type":"dns_query","source":"lab","process":"test.exe",'
            '"destination_domain":"example.test"}'
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.jsonl"
            path.write_text(f"{line}\n{line}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate telemetry event_id"):
                load_telemetry(path)

    def test_rejects_network_events_without_a_destination(self) -> None:
        mapping = {
            "event_id": "BAD-1",
            "timestamp": "2026-01-15T12:00:00Z",
            "host": "lab-host",
            "event_type": "network_connection",
            "source": "lab",
            "process": "test.exe",
            "destination_port": 443,
        }
        with self.assertRaisesRegex(ValueError, "destination_ip or destination_domain"):
            TelemetryEvent.from_mapping(mapping)


if __name__ == "__main__":
    unittest.main()
