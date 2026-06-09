#!/usr/bin/env python3
"""Process the 10M merged RATPAC2 bundle into events/fid_10M_unfiltered_*.npy
and validate it against the existing 1M arrays.

Prereq: extract truth.txt and neutrons.txt into RAW (see the implementation
plan / spec). Run from neutrino-directionality/parallel with the repo .venv:
    /.../.venv/bin/python process_10M.py
"""

import os
import sys

import numpy as np

from mpi4py import MPI

from main import ParallelProcessor
from validation import summarize, format_table

RAW = "/home/beefboi/Desktop/Research/Physics-Research/10M_raw"
V10 = "events/fid_10M_unfiltered_vertices.npy"
C10 = "events/fid_10M_unfiltered_captures.npy"
V1 = "events/fid_1M_unfiltered_vertices.npy"
C1 = "events/fid_1M_unfiltered_captures.npy"


def main():
    if MPI.COMM_WORLD.Get_size() > 1:
        sys.exit("ERROR: run process_10M.py single-process (python process_10M.py), not under mpiexec.")

    truth = os.path.join(RAW, "truth.txt")
    neutrons = os.path.join(RAW, "neutrons.txt")
    for p in (truth, neutrons):
        if not os.path.exists(p):
            sys.exit(f"ERROR: {p} not found. Extract the tarball first (see plan Task 6).")
    for p in (V1, C1):
        if not os.path.exists(p):
            sys.exit(f"ERROR: 1M reference array {p} not found. Run the 1M analysis first.")

    # process=True runs the parser; load=False skips readData (10M npy doesn't exist yet).
    ParallelProcessor(
        n=1000, dx=50, gs=9,
        positron_file=truth, neutron_file=neutrons,
        vertices_file=V10, captures_file=C10,
        process=True, load=False,
    )

    s10 = summarize(np.load(V10), np.load(C10), seg_size=50)
    s1 = summarize(np.load(V1), np.load(C1), seg_size=50)
    print(format_table(s1, s10))

    assert s10["counts_equal"], "10M vertex/capture counts differ"
    assert s10["n_vertices"] > s1["n_vertices"], (
        f"10M dataset ({s10['n_vertices']} events) is not larger than 1M "
        f"({s1['n_vertices']} events)"
    )
    rel = abs(s10["avg_track_length"] - s1["avg_track_length"]) / s1["avg_track_length"]
    assert rel < 0.05, (
        f"avg track length deviates {rel:.1%} from 1M baseline "
        f"(10M={s10['avg_track_length']:.2f} mm, 1M={s1['avg_track_length']:.2f} mm, threshold=5%)"
    )
    print("\nVALIDATION PASSED")


if __name__ == "__main__":
    main()
