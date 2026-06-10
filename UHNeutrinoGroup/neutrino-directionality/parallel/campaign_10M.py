#!/usr/bin/env python3
"""Regenerate the money-plot curves on the 10M dataset (res_10M, 9M aligned
events) by running calcUncertainty over the segment-size x counts grid, for
both detected and usable events.

Outputs accumulate (append mode) into:
    data_10M_detected/func_iter_dx_{5,50,150}_detected.txt
    data_10M_usable/func_iter_dx_{5,50,150}_usable.txt
each row: n  sigma_deg  sigma_err   (one row per (dx, n) point).

Run from neutrino-directionality/parallel with the repo .venv:
    mpiexec -n 10 python campaign_10M.py
(The number of ranks only slices the [-180,180) angle search; results are
identical regardless of -n. Single-process also works, just slower.)
"""
import os

from main import ParallelProcessor

V10 = "events/fid_10M_unfiltered_vertices.npy"
C10 = "events/fid_10M_unfiltered_captures.npy"

# The detector is a FIXED physical size; the segment count scales with the
# segment size so every dx models the same ~450 mm detector. grid_size must be
# odd (clearly defined centre segment). This matches the paper generation
# driver (Nu2026/.../uncert_parallel_ratpac.py: gs = round_odd(450/dx)):
#   dx=5 -> gs=89, dx=50 -> gs=9, dx=150 -> gs=3.
DETECTOR_MM = 450


def round_to_nearest_odd(x):
    n = round(x)
    if n % 2 == 0:
        return n - 1 if abs(x - (n - 1)) <= abs(x - (n + 1)) else n + 1
    return n


# Paper grid (n up to 1e5) extended a decade to 1e6 to use the 9M statistics.
N_GRID = [1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000, 300000, 1000000]
DX_LIST = [5, 50, 150]
ITERATIONS = 300

for center, bd in [(True, "data_10M_detected"), (False, "data_10M_usable")]:
    os.makedirs(bd, exist_ok=True)
    for dx in DX_LIST:
        gs = round_to_nearest_odd(DETECTOR_MM / dx)
        for n in N_GRID:
            pp = ParallelProcessor(
                n=n, dx=dx, gs=gs, cent=center,
                vertices_file=V10, captures_file=C10,
                bd=bd, process=False, load=True,
            )
            pp.calcUncertainty(iterations=ITERATIONS, vary="counts", center=center)
            if pp.rank == 0:
                print(f"[done] {bd} dx={dx} gs={gs} n={n}", flush=True)
