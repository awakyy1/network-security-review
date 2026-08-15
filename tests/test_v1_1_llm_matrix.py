from __future__ import annotations

import unittest

from src.v1_1_llm_matrix import _slug


class V11LlmMatrixTest(unittest.TestCase):
    def test_model_tag_slug_is_stable_and_path_safe(self) -> None:
        self.assertEqual(_slug("llama3.2:3b"), "llama3-2-3b")
        self.assertEqual(_slug("Qwen3:8B"), "qwen3-8b")


if __name__ == "__main__":
    unittest.main()
