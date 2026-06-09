import unittest

import numpy as np

from validation import summarize


class TestSummarize(unittest.TestCase):
    def test_known_values(self):
        v = np.array([[0.0, 0.0, 0.0], [5.0, 1.0, 0.0]])
        c = np.array([[3.0, 4.0, 0.0], [13.0, 4.0, 0.0]])
        # coords = c - v = [[3,4,0],[8,3,0]]; norms = [5, sqrt(73)]
        s = summarize(v, c, seg_size=5)
        self.assertEqual(s["n_vertices"], 2)
        self.assertEqual(s["n_captures"], 2)
        self.assertTrue(s["counts_equal"])
        self.assertAlmostEqual(s["avg_track_length"], (5.0 + np.sqrt(73)) / 2, places=6)
        np.testing.assert_allclose(s["coords_mean"], [5.5, 3.5, 0.0])
        np.testing.assert_allclose(s["coords_std"], [2.5, 0.5, 0.0])
        # r = [5, 8.544]; R = 5/sqrt(2) = 3.535; both usable -> 1.0
        self.assertAlmostEqual(s["usable_fraction"], 1.0)


if __name__ == "__main__":
    unittest.main()
