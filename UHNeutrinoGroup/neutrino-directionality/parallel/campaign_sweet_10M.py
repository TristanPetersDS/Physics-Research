#!/usr/bin/env python3
"""Sweet-spot sweep on the 10M dataset: fix the count n and vary the segment
size dx, so the cubic-fit minimum gives the ideal segment size of a fixed
~450 mm detector. Mirrors the poster generation driver
(Nu2026/.../uncert_parallel_ratpac.py): gs = round_odd(450/dx), n=300,
vary="seg-size", 300 iterations. Run for both detected and usable events.

Outputs (append mode) into:
    data_10M_sweet/func_iter_n_300_detected.txt
    data_10M_sweet/func_iter_n_300_usable.txt
each row: dx  sigma_deg  sigma_err.

Run from neutrino-directionality/parallel with the repo .venv:
    mpiexec -n 10 python campaign_sweet_10M.py
"""
import os

from main import ParallelProcessor

V10 = "events/fid_10M_unfiltered_vertices.npy"
C10 = "events/fid_10M_unfiltered_captures.npy"
DETECTOR_MM = 450
BD = "data_10M_sweet"


def round_to_nearest_odd(x):
    n = round(x)
    if n % 2 == 0:
        return n - 1 if abs(x - (n - 1)) <= abs(x - (n + 1)) else n + 1
    return n


# dx 5..175 in steps of 5 (the poster sweep: linspace(5,150,30) + 155..175).
SEG_SIZES = list(range(5, 176, 5))
N_FIXED = 300
ITERATIONS = 300

os.makedirs(BD, exist_ok=True)
for center, suffix in [(True, "detected"), (False, "usable")]:
    for dx in SEG_SIZES:
        gs = round_to_nearest_odd(DETECTOR_MM / dx)
        pp = ParallelProcessor(
            n=N_FIXED, dx=dx, gs=gs, cent=center,
            vertices_file=V10, captures_file=C10,
            bd=BD, process=False, load=True,
        )
        # Pool guard (2n distinct draws). self.data is loaded by readData()
        # which runs ONLY on rank 0, so the check must happen there and the
        # skip decision be broadcast -- otherwise non-root ranks raise
        # AttributeError, then rank 0 deadlocks alone in the directionAlgorithm
        # bcast. (At n=300 this never trips, but keep it collective and correct.)
        k = "detected" if center else "usable"
        if pp.rank == 0:
            pool = len(pp.data[k]["main"]) + len(pp.data[k]["buffer"])
            skip = 2 * N_FIXED > pool
        else:
            pool, skip = None, None
        skip = pp.comm.bcast(skip, root=0)
        if skip:
            if pp.rank == 0:
                print(f"[skip] {suffix} dx={dx}: needs 2n={2 * N_FIXED} > pool {pool:,}", flush=True)
            continue
        pp.calcUncertainty(iterations=ITERATIONS, vary="seg-size", center=center)
        if pp.rank == 0:
            print(f"[done] {suffix} dx={dx} gs={gs}", flush=True)
