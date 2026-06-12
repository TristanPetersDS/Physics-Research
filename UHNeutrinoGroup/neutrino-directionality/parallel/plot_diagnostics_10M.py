#!/usr/bin/env python3
"""Per-point diagnostic figures on the 10M dataset. Run SINGLE-PROCESS:

    python plot_diagnostics_10M.py

Single-process on purpose: directionAlgorithm/calcUncertainty are MPI-collective,
and the native calcUncertainty(plot=True) path also calls savefig(".jpg"), which
hangs under usetex without dvipng. We avoid both pitfalls:

  * FND-vs-angle panels  -- directionAlgorithm(plot=True, save=True). This path
                            saves a PDF only (no jpg), so it renders cleanly.
                            With size==1 the bcast/gather are no-ops.
  * polar angle plots    -- rendered HERE from the 300-angle arrays the money
                            campaign already saved (data_10M_detected/
                            data_iter_dx_{dx}_n_{n}.npy). No recomputation, no
                            jpg, von Mises refit done locally.

Outputs (data_10M_diag/, 10M-tagged):
    FND_10M_n_{n}_dx_{dx}.pdf
    polar_10M_dx_{dx}_n_{n}.pdf
"""
import os

import matplotlib
matplotlib.use("pdf")  # usetex -> PDF works without dvipng
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import vonmises

from main import ParallelProcessor
from palette import OKABE_ITO

plt.rc("font", family="serif", size=16)
plt.rcParams["text.usetex"] = True
plt.rcParams["mathtext.fontset"] = "cm"

V10 = "events/fid_10M_unfiltered_vertices.npy"
C10 = "events/fid_10M_unfiltered_captures.npy"
DETECTOR_MM = 450
BD = "data_10M_diag"
DET = "data_10M_detected"  # where the campaign saved data_iter_*.npy


def round_to_nearest_odd(x):
    n = round(x)
    if n % 2 == 0:
        return n - 1 if abs(x - (n - 1)) <= abs(x - (n + 1)) else n + 1
    return n


# ---- FND panels: one cheap direction estimate each (single process) ----
FND_POINTS = [(100, 50), (1000, 50), (10000, 50), (1000, 5), (1000, 150)]

# ---- polar plots: rendered from already-saved campaign angle arrays ----
POLAR_POINTS = [(100, 50), (1000, 50), (10000, 50), (1000, 5), (1000, 150)]


def render_fnd():
    for n, dx in FND_POINTS:
        gs = round_to_nearest_odd(DETECTOR_MM / dx)
        pp = ParallelProcessor(
            n=n, dx=dx, gs=gs, cent=True,
            vertices_file=V10, captures_file=C10,
            bd=BD, process=False, load=True,
        )
        pp.directionAlgorithm(center=True, plot=True, save=True)
        src = f"FND_n_{n}_dx_{dx}.pdf"
        dst = f"{BD}/FND_10M_n_{n}_dx_{dx}.pdf"
        if os.path.exists(src):
            os.replace(src, dst)
            print(f"[fnd] -> {dst}", flush=True)
        plt.close("all")


def wrap_deg(a):
    return ((a + 180) % 360) - 180


def render_polar(n, dx):
    src = f"{DET}/data_iter_dx_{dx}_n_{n}.npy"
    if not os.path.exists(src):
        print(f"[polar] skip {src} (missing)")
        return
    thetas_deg = wrap_deg(np.load(src))
    thetas_rad = np.deg2rad(thetas_deg)

    kappa, loc, _ = vonmises.fit(thetas_rad, fscale=1)
    # circular std (deg) for the label, same definition as the analysis class.
    R = np.abs(np.mean(np.exp(1j * thetas_rad)))
    sigma_deg = np.rad2deg(np.sqrt(-2 * np.log(R))) if 0 < R <= 1 else float("nan")

    n_bins = 36
    hist, edges = np.histogram(thetas_deg, bins=n_bins, range=(-180, 180))
    centers = np.deg2rad((edges[:-1] + edges[1:]) / 2)

    theta = np.linspace(-np.pi, np.pi, 500)
    pdf = vonmises.pdf(theta, kappa, loc=loc)
    pdf_scaled = pdf / pdf.max() * hist.max() if hist.max() > 0 else pdf

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(6, 6))
    ax.set_yticklabels([])
    ax.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2])
    ax.set_xticklabels([r"$0$", r"$\pi/2$", r"$\pi$", r"$3\pi/2$"])
    ax.bar(centers, hist, width=2 * np.pi / n_bins, bottom=0,
           edgecolor=OKABE_ITO["blue"], facecolor="none", linewidth=2)
    ax.plot(theta, pdf_scaled, "-", color=OKABE_ITO["vermillion"], lw=2,
            label=(f"$\\mu={np.rad2deg(loc):.1f}^\\circ,\\ "
                   f"\\sigma={sigma_deg:.1f}^\\circ,\\ \\kappa={kappa:.2f}$"))
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_title(f"$\\Delta x={dx}$ mm, $n={n}$ (10M)", va="bottom")
    ax.legend(loc="lower left", framealpha=1.0, fontsize=11)
    out = f"{BD}/polar_10M_dx_{dx}_n_{n}.pdf"
    plt.savefig(out, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"[polar] -> {out}  (sigma={sigma_deg:.2f} deg)", flush=True)


if __name__ == "__main__":
    os.makedirs(BD, exist_ok=True)
    print("FND panels (single-process direction estimates):")
    render_fnd()
    print("\npolar plots (from saved campaign angle arrays):")
    for n, dx in POLAR_POINTS:
        render_polar(n, dx)
    print("\ndone.")
