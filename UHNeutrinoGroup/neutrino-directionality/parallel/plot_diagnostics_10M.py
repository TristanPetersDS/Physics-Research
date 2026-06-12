#!/usr/bin/env python3
"""Per-point diagnostic figures on the 10M dataset, using the ParallelProcessor's
own plotting paths:

  * FND-vs-angle panels   -- directionAlgorithm(plot=True, save=True)
                             shows the binned Frobenius-norm curve and its
                             |sin| fit for a single (n, dx) estimate.
  * polar angle plots     -- calcUncertainty(plot=True, save=True)
                             shows the distribution of recovered angles over
                             ITER iterations with the fitted von Mises overlay.

Native output names don't carry the dataset, so rank 0 renames each file to a
10M-tagged name under data_10M_diag/. Run with MPI:

    mpiexec -n 10 python plot_diagnostics_10M.py

(directionAlgorithm/calcUncertainty are collective; plotting happens on rank 0.
The pdf backend renders usetex without dvipng and makes plt.show() a no-op.)
"""
import os

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt

from main import ParallelProcessor

V10 = "events/fid_10M_unfiltered_vertices.npy"
C10 = "events/fid_10M_unfiltered_captures.npy"
DETECTOR_MM = 450
BD = "data_10M_diag"
ITER = 300


def round_to_nearest_odd(x):
    n = round(x)
    if n % 2 == 0:
        return n - 1 if abs(x - (n - 1)) <= abs(x - (n + 1)) else n + 1
    return n


# (n, dx) points. FND panels are one cheap estimate each; polar plots run ITER
# iterations, so keep that list shorter and on faster (smaller-n) points.
FND_POINTS = [(100, 50), (1000, 50), (10000, 50), (1000, 5), (1000, 150)]
POLAR_POINTS = [(100, 50), (1000, 50), (10000, 50)]


def make(n, dx, do_fnd, do_polar):
    gs = round_to_nearest_odd(DETECTOR_MM / dx)
    pp = ParallelProcessor(
        n=n, dx=dx, gs=gs, cent=True,
        vertices_file=V10, captures_file=C10,
        bd=BD, process=False, load=True,
    )
    if do_fnd:
        pp.directionAlgorithm(center=True, plot=True, save=True)
        if pp.rank == 0:
            src = f"FND_n_{n}_dx_{dx}.pdf"            # native name, lands in CWD
            dst = f"{BD}/FND_10M_n_{n}_dx_{dx}.pdf"
            if os.path.exists(src):
                os.replace(src, dst)
                print(f"[fnd] -> {dst}", flush=True)
            plt.close("all")
    if do_polar:
        pp.calcUncertainty(iterations=ITER, vary="counts", center=True, plot=True, save=True)
        if pp.rank == 0:
            src = f"{BD}/polar_plot_dx_{dx}_n_{n}_i_{ITER}.pdf"
            dst = f"{BD}/polar_10M_dx_{dx}_n_{n}.pdf"
            if os.path.exists(src):
                os.replace(src, dst)
            # drop the jpg twin the method also writes
            jpg = f"{BD}/polar_plot_dx_{dx}_n_{n}_i_{ITER}.jpg"
            if os.path.exists(jpg):
                os.remove(jpg)
            print(f"[polar] -> {dst}", flush=True)
            plt.close("all")


if __name__ == "__main__":
    os.makedirs(BD, exist_ok=True)
    points = sorted(set(FND_POINTS) | set(POLAR_POINTS))
    for n, dx in points:
        make(n, dx, do_fnd=(n, dx) in FND_POINTS, do_polar=(n, dx) in POLAR_POINTS)
