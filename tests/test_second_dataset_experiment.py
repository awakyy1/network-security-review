from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.ctu13_acquire import sha256_file
from src.second_dataset_experiment import run_second_dataset


class SecondDatasetExperimentTest(unittest.TestCase):
    def test_replays_hyphen_timestamp_profile_without_pooling_units(self) -> None:
        header = "StartTime,Dur,Proto,SrcAddr,Sport,Dir,DstAddr,Dport,State,sTos,dTos,TotPkts,TotBytes,SrcBytes,Label"
        rows = [
            "2020-01-01 00:00:00,0,tcp,10.0.0.1,1,->,192.0.2.1,443,S,0,0,1,100,50,flow=From-Botnet-Test",
            "2020-01-01 00:00:01,0,tcp,10.0.0.2,1,->,192.0.2.2,443,S,0,0,1,100,50,flow=From-Normal-Test",
            "2020-01-01 00:00:30,0,tcp,10.0.0.1,1,->,192.0.2.1,443,S,0,0,1,100,50,flow=From-Botnet-Test",
            "2020-01-01 00:01:00,0,tcp,10.0.0.1,1,->,192.0.2.1,443,S,0,0,1,100,50,flow=From-Botnet-Test",
            "2020-01-01 00:01:30,0,tcp,10.0.0.1,1,->,192.0.2.1,443,S,0,0,1,100,50,flow=From-Botnet-Test",
            "2020-01-01 00:02:00,0,tcp,10.0.0.1,1,->,192.0.2.1,443,S,0,0,1,100,50,flow=From-Botnet-Test",
            "2020-01-01 00:02:30,0,tcp,10.0.0.1,1,->,192.0.2.1,443,S,0,0,1,100,50,flow=From-Botnet-Test",
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "dataset_result.binetflow"
            source.write_text("\n".join([header, *rows, ""]), encoding="utf-8")
            selection = root / "selection.json"
            selection.write_text('{"selected":"scenario-1"}', encoding="utf-8")
            manifest = {
                "status": "frozen-before-detector-run",
                "selection_record": {"filename": selection.name, "sha256": sha256_file(selection)},
                "source": {
                    "path": source.as_posix(),
                    "bytes": source.stat().st_size,
                    "sha256": sha256_file(source),
                    "scenario": 1,
                },
                "parser_profile": {
                    "maximum_file_bytes": 1_000_000,
                    "maximum_rows": 100,
                    "timestamp_patterns": ["%Y-%m-%d %H:%M:%S"],
                    "address_namespace": "test",
                    "event_prefix": "TST",
                    "telemetry_source": "test-binetflow",
                },
                "window_seconds": 300,
                "detector_thresholds": {"beh_002_minimum_distinct_endpoints": 16},
            }
            manifest_file = root / "run.json"
            manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

            result = run_second_dataset(manifest_file, root / "output")

        self.assertEqual(result["metrics"]["true_positive"], 1)
        self.assertEqual(result["metrics"]["true_negative"], 1)
        self.assertNotIn("units", result)
        self.assertEqual(result["rule_combination_counts_by_truth"]["botnet-origin"]["BEH-001"], 1)


if __name__ == "__main__":
    unittest.main()
