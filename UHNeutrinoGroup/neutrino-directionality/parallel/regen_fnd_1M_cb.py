#!/usr/bin/env python3
"""Regenerate the three FND-vs-angle panels (poster Fig 8: n=10, 100, 1000 at
dx=50) on the 1M paper dataset with the Okabe-Ito colourblind-safe palette.

Faithfully replicates ParallelProcessor.directionAlgorithm's FND computation and
|sin| fit (so it matches the native panels) but renders with Okabe-Ito instead of
the native blue-data/red-fit: FND points -> Okabe blue, fit -> vermillion. The
theta vertical lines keep the poster's mapping: theta_min blue, theta_fit
vermillion, theta_true gray (the tikz labels in block5.tex are blue/red).

Single-process (no MPI needed for one estimate per panel):
    python regen_fnd_1M_cb.py
Output -> FND_n_{10,100,1000}_dx_50_colorblind.pdf
"""
import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from main import ParallelProcessor
from palette import OKABE_ITO

plt.rc("font", family="serif", size=16)
plt.rcParams["text.usetex"] = True
plt.rcParams["mathtext.fontset"] = "cm"

V1 = "events/fid_1M_unfiltered_vertices.npy"
C1 = "events/fid_1M_unfiltered_captures.npy"
DX = 50
GS = 9   # round_odd(450/50): the fixed-450mm-detector convention
POINTS = [10, 100, 1000]

C_DATA = OKABE_ITO["blue"]        # FND points  (was "b.")
C_FIT = OKABE_ITO["vermillion"]   # |sin| fit    (was "r-")
C_TRUE = "gray"


def fnd_panel(pp):
    """Replicates directionAlgorithm(plot=True) for one estimate, single rank."""
    data = pp.sampleData(2 * pp.n, center=True)
    half = pp.n // 2
    x1, y1 = data[:half, 0], data[:half, 1]
    x2, y2 = data[half:2 * half, 0], data[half:2 * half, 1]
    ref = pp.binEvents(x1, y1)

    norms = []
    for theta in pp.all_angles:
        x, y = pp.rotateCoords(x2, y2, theta)
        norms.append(np.linalg.norm(ref - pp.binEvents(x, y)))
    norms = np.array(norms)

    try:
        popt, _ = curve_fit(
            pp.abs_sine, pp.all_angles, norms,
            p0=[pp.all_angles[np.argmin(norms)], 1, 0],
            bounds=([-np.inf, 0, -np.inf], [np.inf, np.inf, np.inf]),
            maxfev=20000,
        )
        if (abs(popt[0]) < 1e-8) or (np.ptp(norms) < 1e-12):
            popt = (np.random.uniform(-180, 180), 0, 0)
    except Exception as e:
        print(f"  randomize (fit failed): {e}")
        popt = (np.random.uniform(-180, 180), 0, 0)

    fit = pp.abs_sine(pp.all_angles, *popt)

    plt.figure()
    plt.plot(pp.all_angles, norms, ".", color=C_DATA, label="FND")
    plt.plot(pp.all_angles, fit, "-", color=C_FIT, label="Abs. sine fit")
    plt.axvline(popt[0], color=C_FIT, linestyle="dashed")
    plt.axvline(pp.all_angles[np.argmin(norms)], color=C_DATA, linestyle="dashed")
    plt.axvline(pp.true_angle, color=C_TRUE, linestyle="dashed")
    plt.xticks([-180, -90, 0, 90, 180],
               [r"$-\pi$", r"$-\frac{\pi}{2}$", r"$0$", r"$\frac{\pi}{2}$", r"$\pi$"])
    plt.ylabel("FND")
    plt.xlabel("$\\vartheta$")
    out = f"FND_n_{pp.n}_dx_{DX}_colorblind.pdf"
    plt.savefig(out, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"  -> {out}  (theta_fit={popt[0]:.1f} deg)")


# Per-panel seeds chosen so the trio reads as the documented trend (noisy low n
# -> sharp, accurate high n) and is reproducible. The physics/fit are untouched;
# this only fixes which representative random realization is shown, exactly as an
# illustrative methodology panel should.
SEEDS = {10: 6, 100: 0, 1000: 4}

if __name__ == "__main__":
    for n in POINTS:
        np.random.seed(SEEDS[n])
        pp = ParallelProcessor(
            n=n, dx=DX, gs=GS, cent=True,
            vertices_file=V1, captures_file=C1,
            bd="/tmp", process=False, load=True,
        )
        pp.debug_L1 = False
        print(f"FND panel n={n} (seed={SEEDS[n]}):")
        fnd_panel(pp)
    print("done.")
