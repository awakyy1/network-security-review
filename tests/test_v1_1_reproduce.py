from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from src.v1_1_reproduce import _non_system_path


class V11ReproduceTest(unittest.TestCase):
    def test_rejects_system_drive_on_windows(self) -> None:
        with mock.patch("src.v1_1_reproduce.os.name", "nt"):
            with mock.patch.object(Path, "resolve", return_value=Path("C:/unsafe")):
                with self.assertRaisesRegex(ValueError, "system drive"):
                    _non_system_path(Path("C:/unsafe"))

    def test_accepts_repository_drive(self) -> None:
        path = Path("E:/tcc/output") if os.name == "nt" else Path("/tmp/output")
        self.assertEqual(_non_system_path(path), path.resolve())
