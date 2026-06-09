import os
import shutil
import tempfile
import unittest

import numpy as np

from main import ParallelProcessor

TRUTH = """Row Instance trackPDG trackProcess evid mcx mcy mcz mcu mcv mcw mcpdg
0 0 -11 0 0 0.0 0.0 0.0 0 0 0 -11
0 1 22 1 0 0.5 0.0 0.0 0 0 0 22
1 0 -11 0 1 5.0 1.0 0.0 0 0 0 -11
"""

NEUTRONS = """Row Instance trackPDG trackPosX trackPosY trackPosZ trackTime trackMomX trackMomY trackMomZ trackKE trackProcess
0 0 2112 1.0 0.0 0.0 0 0 0 0 0.01 0
0 1 2112 2.0 0.0 0.0 0.1 0 0 0 0.005 1
0 2 2112 3.0 4.0 0.0 0.2 0 0 0 0.001 1
1 0 2112 10.0 0.0 0.0 0 0 0 0 0.01 0
1 1 2112 13.0 4.0 0.0 0.1 0 0 0 0.001 1
"""


class TestProcessData(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.truth = os.path.join(self.d, "truth.txt")
        self.neut = os.path.join(self.d, "neutrons.txt")
        self.vfile = os.path.join(self.d, "v.npy")
        self.cfile = os.path.join(self.d, "c.npy")
        with open(self.truth, "w") as f:
            f.write(TRUTH)
        with open(self.neut, "w") as f:
            f.write(NEUTRONS)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def _make(self):
        return ParallelProcessor(
            n=10, dx=50, gs=9,
            positron_file=self.truth, neutron_file=self.neut,
            vertices_file=self.vfile, captures_file=self.cfile,
            process=False, load=False,
        )

    def test_constructor_accepts_overrides_without_loading(self):
        pp = self._make()
        self.assertEqual(pp.vertices_file, self.vfile)
        self.assertEqual(pp.positron_file, self.truth)
        self.assertFalse(hasattr(pp, "coords"))  # load=False => readData() not run
        self.assertEqual(pp.captures_file, self.cfile)
        self.assertEqual(pp.neutron_file, self.neut)


    def test_processdata_equal_counts_and_values(self):
        pp = self._make()
        pp.processData()
        v = np.load(self.vfile)
        c = np.load(self.cfile)
        # Header is a single line here; both files describe 2 events.
        self.assertEqual(len(v), 2, "expected 2 vertices")
        self.assertEqual(len(c), 2, "expected 2 captures")
        self.assertEqual(len(v), len(c), "vertex/capture counts must match")
        # vertices = mc{x,y,z} of each Instance==0 positron row
        np.testing.assert_allclose(v, [[0.0, 0.0, 0.0], [5.0, 1.0, 0.0]])
        # captures = last track step of each event (3,4,0) and (13,4,0)
        np.testing.assert_allclose(c, [[3.0, 4.0, 0.0], [13.0, 4.0, 0.0]])


    def test_processdata_aligns_mismatched_counts(self):
        # truth has 2 events, neutrons has 3 -> align to common prefix of 2.
        truth = """Row Instance trackPDG trackProcess evid mcx mcy mcz mcu mcv mcw mcpdg
0 0 -11 0 0 0.0 0.0 0.0 0 0 0 -11
1 0 -11 0 1 5.0 1.0 0.0 0 0 0 -11
"""
        neutrons = """Row Instance trackPDG trackPosX trackPosY trackPosZ trackTime trackMomX trackMomY trackMomZ trackKE trackProcess
0 0 2112 1.0 0.0 0.0 0 0 0 0 0.01 0
0 1 2112 3.0 4.0 0.0 0.2 0 0 0 0.001 1
1 0 2112 10.0 0.0 0.0 0 0 0 0 0.01 0
1 1 2112 13.0 4.0 0.0 0.1 0 0 0 0.001 1
2 0 2112 20.0 0.0 0.0 0 0 0 0 0.01 0
2 1 2112 25.0 7.0 0.0 0.1 0 0 0 0.001 1
"""
        with open(self.truth, "w") as f:
            f.write(truth)
        with open(self.neut, "w") as f:
            f.write(neutrons)
        pp = self._make()
        pp.processData()
        v = np.load(self.vfile)
        c = np.load(self.cfile)
        self.assertEqual(len(v), 2)
        self.assertEqual(len(c), 2)  # neutrons truncated 3 -> 2 (common prefix)
        np.testing.assert_allclose(v, [[0.0, 0.0, 0.0], [5.0, 1.0, 0.0]])
        np.testing.assert_allclose(c, [[3.0, 4.0, 0.0], [13.0, 4.0, 0.0]])


if __name__ == "__main__":
    unittest.main()
