from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.behavior_detector import DetectorThresholds
from src.ctu13_experiment import ParseCounters, evaluate_binetflow, iter_labeled_windows

HEADER = "StartTime,Dur,Proto,SrcAddr,Sport,Dir,DstAddr,Dport,State,sTos,dTos,TotPkts,TotBytes,SrcBytes,Label"


def _row(timestamp: str, src: str, dst: str, dport: int, label: str, *, sent: int = 100) -> str:
    return f"{timestamp},0.1,tcp,{src},50000,->,{dst},{dport},CON,0,0,2,{sent + 50},{sent},{label}"


class CTU13ExperimentTest(unittest.TestCase):
    def test_streams_clean_labeled_windows_and_excludes_ambiguous_labels(self) -> None:
        lines = [HEADER]
        for index in range(6):
            lines.append(
                _row(
                    f"2011/08/15 16:5{index}:00.000000",
                    "infected",
                    "command",
                    443,
                    "flow=From-Botnet-TCP-Established",
                )
            )
        lines.append(
            _row(
                "2011/08/15 16:55:30.000000",
                "unknown",
                "infected",
                443,
                "flow=To-Botnet-TCP-Established",
            )
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.binetflow"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            counters = ParseCounters()
            windows = list(iter_labeled_windows(path, scenario=5, window_seconds=300, counters=counters))

        self.assertEqual(len(windows), 2)
        self.assertTrue(all(window.truth == "botnet-origin" for window in windows))
        self.assertEqual(counters.scored_rows, 6)
        self.assertEqual(counters.excluded_background_or_to, 1)
        self.assertTrue(all("infected" not in window.host for window in windows))

    def test_evaluates_botnet_true_positive_and_normal_false_positive(self) -> None:
        lines = [HEADER]
        for index in range(6):
            lines.append(
                _row(
                    f"2011/08/15 16:50:{index * 10:02d}.000000",
                    "infected",
                    "command",
                    443,
                    "flow=From-Botnet-TCP-Established",
                )
            )
        for index in range(8):
            lines.append(
                _row(
                    f"2011/08/15 16:51:{index:02d}.000000",
                    "normal",
                    f"service-{index}",
                    1000 + index,
                    "flow=From-Normal-TCP-Established",
                )
            )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.binetflow"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            result = evaluate_binetflow(
                path,
                scenario=5,
                family="fixture",
                role="development",
                window_seconds=300,
            )

        metrics = result["metrics"]
        self.assertEqual(metrics["true_positive"], 1)
        self.assertEqual(metrics["false_positive"], 1)
        self.assertEqual(metrics["false_negative"], 0)
        self.assertEqual(metrics["true_negative"], 0)
        self.assertEqual(result["rule_finding_counts"]["BEH-001"]["botnet_origin"], 1)
        self.assertEqual(result["rule_finding_counts"]["BEH-002"]["normal_origin"], 1)
        self.assertEqual(result["response_simulation"]["automatic_actions_executed"], 0)
        self.assertEqual(
            result["response_simulation"]["counterfactual_unnecessary_action_rate_if_every_alert_were_blocked"],
            0.5,
        )

    def test_evaluation_records_and_applies_explicit_thresholds(self) -> None:
        lines = [HEADER]
        for index in range(8):
            lines.append(
                _row(
                    f"2011/08/15 16:51:{index:02d}.000000",
                    "normal",
                    f"service-{index}",
                    1000 + index,
                    "flow=From-Normal-TCP-Established",
                )
            )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.binetflow"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            thresholds = DetectorThresholds(beh_002_minimum_distinct_endpoints=16)
            result = evaluate_binetflow(
                path,
                scenario=11,
                family="fixture",
                role="development",
                window_seconds=300,
                thresholds=thresholds,
            )

        self.assertEqual(result["metrics"]["false_positive"], 0)
        self.assertEqual(result["metrics"]["true_negative"], 1)
        self.assertEqual(result["detector_thresholds"]["beh_002_minimum_distinct_endpoints"], 16)


if __name__ == "__main__":
    unittest.main()
