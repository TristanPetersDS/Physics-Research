import os
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


if __name__ == "__main__":
    unittest.main()
