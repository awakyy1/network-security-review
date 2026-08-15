from __future__ import annotations

import unittest

from src.reference_audit import parse_bibliography


class ReferenceAuditTest(unittest.TestCase):
    def test_parser_preserves_keys_and_one_line_fields(self) -> None:
        entries = parse_bibliography(
            """@article{first,
  title = {A Title},
  year = {2026},
  doi = {10.1000/example}
}

@misc{second,
  title = {{CTU-13} Dataset},
  url = {https://example.test/}
}
"""
        )
        self.assertEqual([item["key"] for item in entries], ["first", "second"])
        self.assertEqual(entries[0]["doi"], "10.1000/example")
        self.assertEqual(entries[1]["title"], "{CTU-13} Dataset")


if __name__ == "__main__":
    unittest.main()
