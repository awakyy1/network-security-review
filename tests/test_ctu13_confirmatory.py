from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.ctu13_acquire import sha256_file
from src.ctu13_confirmatory import GRID_FIELDS, _grid_candidates, run_holdout, selection_sort_key, tune_development

HEADER = "StartTime,Dur,Proto,SrcAddr,Sport,Dir,DstAddr,Dport,State,sTos,dTos,TotPkts,TotBytes,SrcBytes,Label"


def _fixture_rows(source: str, truth: str) -> str:
    rows = [HEADER]
    for index in range(8):
        rows.append(
            f"2011/08/15 16:50:{index:02d}.000000,0.1,tcp,{source},50000,->,"
            f"service-{index},{1000 + index},CON,0,0,2,150,100,flow={truth}-TCP-Established"
        )
    return "\n".join(rows) + "\n"


class CTU13ConfirmatoryTest(unittest.TestCase):
    def test_grid_cardinality_and_defaults_are_frozen(self) -> None:
        grid = {
            "beh_001_minimum_connections": [4, 6, 8],
            "beh_001_maximum_interval_cv": [0.15, 0.3, 0.5],
            "beh_001_minimum_mean_interval_seconds": [5],
            "beh_001_maximum_mean_interval_seconds": [900],
            "beh_002_minimum_distinct_endpoints": [8, 16, 32],
            "beh_002_interval_seconds": [60],
            "beh_003_minimum_bytes_sent": [65536, 262144, 1000000],
            "beh_003_minimum_sent_received_ratio": [5, 10, 20],
        }
        selection = {
            "threshold_selection": {
                "candidate_grid": grid,
                "candidate_configurations": 243,
            }
        }

        candidates = _grid_candidates(selection)

        self.assertEqual(tuple(grid), GRID_FIELDS)
        self.assertEqual(len(candidates), 243)
        self.assertEqual(candidates[0].beh_004_minimum_bytes_received, 32_768)

    def test_selection_tie_break_prefers_closer_then_fewer_alerts(self) -> None:
        thresholds = {field: 1 for field in GRID_FIELDS}
        metrics = {
            "matthews_correlation_coefficient": 0.5,
            "balanced_accuracy": 0.75,
            "f1": 0.7,
            "specificity": 0.8,
        }
        closer = {
            "thresholds": thresholds,
            "metrics": metrics,
            "grid_distance_from_v1_0": 0,
            "alerted_units": 10,
        }
        farther = closer | {"grid_distance_from_v1_0": 1, "alerted_units": 1}
        equally_close_but_more_alerts = closer | {"alerted_units": 11}

        self.assertGreater(selection_sort_key(closer), selection_sort_key(farther))
        self.assertGreater(selection_sort_key(closer), selection_sort_key(equally_close_but_more_alerts))

    def test_end_to_end_development_freeze_gates_holdout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "data"
            data.mkdir()
            development_path = data / "development.binetflow"
            holdout_path = data / "holdout.binetflow"
            development_path.write_text(_fixture_rows("development", "From-Normal"), encoding="utf-8")
            holdout_path.write_text(_fixture_rows("holdout", "From-Botnet"), encoding="utf-8")
            grid = {
                "beh_001_minimum_connections": [6],
                "beh_001_maximum_interval_cv": [0.15],
                "beh_001_minimum_mean_interval_seconds": [5],
                "beh_001_maximum_mean_interval_seconds": [900],
                "beh_002_minimum_distinct_endpoints": [8],
                "beh_002_interval_seconds": [60],
                "beh_003_minimum_bytes_sent": [1000000],
                "beh_003_minimum_sent_received_ratio": [10],
            }
            source_specs = [
                ("development", development_path, 11, "FixtureDev"),
                ("holdout", holdout_path, 6, "FixtureHoldout"),
            ]
            selected_sources = []
            for role, path, scenario, family in source_specs:
                selected_sources.append(
                    {
                        "scenario": scenario,
                        "family": family,
                        "role": role,
                        "filename": path.name,
                        "url": f"https://mcfp.felk.cvut.cz/{path.name}",
                        "content_length": path.stat().st_size,
                        "etag": f'"{role}"',
                        "last_modified": "Fri, 15 Aug 2026 00:00:00 GMT",
                    }
                )
            selection = {
                "primary_window_seconds": 300,
                "threshold_selection": {
                    "candidate_grid": grid,
                    "candidate_configurations": 1,
                    "v1_0_reference": {field: values[0] for field, values in grid.items()},
                },
                "sources": selected_sources,
            }
            selection_path = root / "selection.json"
            selection_path.write_text(json.dumps(selection), encoding="utf-8")
            acquisition = {
                "selection_record_corrected_sha256": sha256_file(selection_path),
                "sources": [
                    {
                        "scenario": scenario,
                        "family": family,
                        "role": role,
                        "filename": path.name,
                        "url": f"https://mcfp.felk.cvut.cz/{path.name}",
                        "expected_bytes": path.stat().st_size,
                        "observed_bytes": path.stat().st_size,
                        "etag": f'"{role}"',
                        "last_modified": "Fri, 15 Aug 2026 00:00:00 GMT",
                        "sha256": sha256_file(path),
                    }
                    for role, path, scenario, family in source_specs
                ],
            }
            acquisition_path = root / "acquisition.json"
            acquisition_path.write_text(json.dumps(acquisition), encoding="utf-8")

            development = tune_development(
                repository_root=Path.cwd(),
                selection_path=selection_path,
                acquisition_path=acquisition_path,
                data_directory=data,
            )
            development_result_path = root / "development-result.json"
            development_result_path.write_text(json.dumps(development), encoding="utf-8")
            holdout = run_holdout(
                repository_root=Path.cwd(),
                selection_path=selection_path,
                acquisition_path=acquisition_path,
                data_directory=data,
                development_result_path=development_result_path,
            )

        self.assertFalse(development["holdout_accessed"])
        self.assertEqual(development["selected"]["metrics"]["false_positive"], 1)
        self.assertEqual(holdout["evidence_role"], "single_confirmatory_holdout_run")
        self.assertEqual(holdout["evaluation"]["metrics"]["true_positive"], 1)


if __name__ == "__main__":
    unittest.main()
