#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: plot_sweet_10M.py
Description: Render the sweet-spot figure(s) from the 10M segment-size sweep
    (data_10M_sweet/, produced by campaign_sweet_10M.py). Mirrors the paper
    script sweet_spot_plot.py -- cubic fit, minimum of the fit gives the ideal
    segment size -- but points at the 10M sweep, uses the Okabe-Ito palette, and
    computes the average track length from the 10M events directly (rather than
    the hardcoded 1M value). Writes dataset-reflecting filenames.

    Output (this directory):
        sweet_spot_10M_detected.pdf
        sweet_spot_10M_usable.pdf   (if the usable sweep is present)

Run from neutrino-directionality/parallel with the repo .venv:
    python plot_sweet_10M.py
"""

import os

import matplotlib
matplotlib.use("pdf")  # usetex -> PDF works without dvipng

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from palette import OKABE_ITO

plt.rc("font", family="serif", size=18)
plt.rcParams["text.usetex"] = True
plt.rcParams["mathtext.fontset"] = "cm"

ITERATIONS = 300


def cubic(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d


def avg_track_length_10M():
    """3D mean capture displacement from the 10M (9M aligned) events."""
    v = np.load("events/fid_10M_unfiltered_vertices.npy")
    c = np.load("events/fid_10M_unfiltered_captures.npy")
    return float(np.mean(np.linalg.norm(c - v, axis=1)))


def make_sweet_plot(data_file, out_pdf, avg_len):
    dx, dt = [], []
    with open(data_file, "r") as f:
        for line in f:
            elems = line.split()
            if len(elems) < 2:
                continue
            dx.append(float(elems[0]))
            dt.append(float(elems[1]))
    dx = np.array(dx)
    dt = np.array(dt)
    order = np.argsort(dx)
    dx, dt = dx[order], dt[order]

    # The file's saved error column is a signed sigma/sqrt(valid_iters) and can
    # be negative; recompute a clean error bar as in sweet_spot_plot.py.
    err = dt / np.sqrt(ITERATIONS)

    params, _ = curve_fit(cubic, dx, dt)
    a, b, c, d = params

    # Minimum of the cubic: root of 3a x^2 + 2b x + c = 0 with positive curvature.
    disc = (2 * b) ** 2 - 4 * (3 * a) * c
    min_label = "cubic fit"
    minimum_loc = None
    if disc >= 0 and a != 0:
        r1 = (-2 * b + np.sqrt(disc)) / (2 * 3 * a)
        r2 = (-2 * b - np.sqrt(disc)) / (2 * 3 * a)
        # Pick the root that is a local minimum (second derivative > 0).
        cands = [r for r in (r1, r2) if (6 * a * r + 2 * b) > 0]
        if cands:
            minimum_loc = min(cands, key=lambda r: abs(r - np.median(dx)))
    plt.figure()
    x_fit = np.linspace(dx.min(), dx.max(), 200)
    y_fit = cubic(x_fit, *params)

    plt.errorbar(dx, dt, yerr=err, fmt=".", color="black", capsize=3, label="Data")
    if minimum_loc is not None and dx.min() <= minimum_loc <= dx.max():
        ratio = minimum_loc / avg_len
        min_label = f"Polyfit min at {int(round(minimum_loc))} mm"
        plt.plot(x_fit, y_fit, "-", color=OKABE_ITO["vermillion"], label=min_label)
        plt.axvline(minimum_loc, color=OKABE_ITO["vermillion"], linestyle="dashed", lw=1)
        print(f"  ideal segment size (fit min): {minimum_loc:.2f} mm")
        print(f"  avg track length (10M):       {avg_len:.2f} mm")
        print(f"  ratio min/track:              {ratio:.2f}")
    else:
        plt.plot(x_fit, y_fit, "-", color=OKABE_ITO["vermillion"], label="cubic fit")
        print("  [warn] cubic minimum not within sweep range; plotted fit only")

    plt.xlabel("Segment size $\\Delta x$ (mm)")
    plt.ylabel("Angular uncertainty $\\delta \\vartheta$ (${}^\\circ$)")
    plt.legend()
    plt.savefig(out_pdf, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"  -> wrote {out_pdf}\n")


if __name__ == "__main__":
    avg_len = avg_track_length_10M()
    print(f"avg track length (10M, 9M events): {avg_len:.5f} mm\n")
    for suffix in ("detected", "usable"):
        path = f"data_10M_sweet/func_iter_n_300_{suffix}.txt"
        if not os.path.exists(path):
            print(f"{suffix}: {path} not found, skipping")
            continue
        print(f"{suffix} (10M sweet spot):")
        make_sweet_plot(path, f"sweet_spot_10M_{suffix}.pdf", avg_len)
    print("done.")
