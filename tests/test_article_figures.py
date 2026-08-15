from __future__ import annotations

import unittest

from src.article_figures import empirical_overlap


class ArticleFiguresTest(unittest.TestCase):
    def test_empirical_overlap_uses_exact_discrete_probability_mass(self) -> None:
        self.assertAlmostEqual(empirical_overlap([1, 1, 2, 4], [1, 2, 2, 8]), 0.5)

    def test_empirical_overlap_requires_two_samples(self) -> None:
        with self.assertRaises(ValueError):
            empirical_overlap([], [1])


if __name__ == "__main__":
    unittest.main()
