#!/usr/bin/env python3
"""Regenerate poster Figure 2 (Paper A analytic angular-resolution curves) with
the Okabe-Ito colourblind-safe palette.

Faithfully reproduces directionality_..._PACKING_FACTOR_v2_UsefulIBDs.py (same
ares() model, log-log axes, two legends, ylim) but OVERRIDES the per-detector
colour (the original clr column has a green/red collision: DoubleChooz green vs
Checker-3D red). Detector physics params are still read from the original
DeltaPhiTable_extra_col.txt, so no Paper A data file is modified.

    python regen_fig2_colorblind.py
Output -> angular_resolution_analytic_ylog_PackFactor_v2Useful_colorblind.pdf
"""
import math

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rc("font", family="serif", size=19)
plt.rcParams["text.usetex"] = True
plt.rcParams["mathtext.fontset"] = "cm"

# Okabe-Ito assignment by detector. 7 mutually CVD-distinguishable colours;
# solid (3D) vs dashed (2D) linestyles add a second channel.
OKABE = {
    "DoubleChooz": "#009E73",  # bluish green (was green)
    "Checker-3D":  "#D55E00",  # vermillion   (was red)
    "SANTA":       "#E69F00",  # orange       (was orange)
    "NuLat5":      "#0072B2",  # blue         (was blue)
    "Checker-2D":  "#56B4E9",  # sky blue     (was red)
    "PROSPECT":    "#CC79A7",  # reddish purple (was gray)
    "SANDD-CM":    "#000000",  # black        (was black)
}

Nmax = 10000
N = np.arange(1.0, Nmax, 0.5)


def ares(P, d, N):
    return (math.atan(P / d / (N**0.5))) * 180 / math.pi


data = pd.read_csv("DeltaPhiTable_extra_col.txt", sep=r"\s+", header=0)

fig, ax = plt.subplots()
for i in range(len(data.index)):
    expr = data.Expr[i]
    ax.plot(N, np.vectorize(ares)(data.P_mm[i], data.l_mm[i], N * data.PackFactor[i]),
            color=OKABE.get(expr, "#000000"), linestyle=data.ln_style[i],
            label=expr, linewidth=1.4)

ax.set_xlabel(r"Number of Detected Useful IBDs")
ax.set_ylabel("Angular Resolution (degrees)")
ax.grid()
ax.set_xscale("log")
ax.set_xlim(10, Nmax)
ax.set_ylim(1, 100)
ax.set_yscale("log")

lines = ax.get_lines()
legend1 = plt.legend([lines[j] for j in range(0, 4)], [lines[j].get_label() for j in range(0, 4)],
                     title="3D", loc="lower left", facecolor="white", framealpha=1,
                     fontsize=12, numpoints=1, edgecolor="black", fancybox=False)
legend2 = plt.legend([lines[j] for j in range(4, 7)], [lines[j].get_label() for j in range(4, 7)],
                     title="2D", loc="upper right", facecolor="white", framealpha=1,
                     fontsize=12, numpoints=1, edgecolor="black", fancybox=False)
ax.add_artist(legend1)
ax.add_artist(legend2)

plt.tight_layout()
out = "angular_resolution_analytic_ylog_PackFactor_v2Useful_colorblind.pdf"
plt.savefig(out, bbox_inches="tight")
print(f"-> {out}")

# Print the curve vertical order at a mid N so the CVD check knows adjacencies.
order = sorted(range(len(data.index)),
               key=lambda i: ares(data.P_mm[i], data.l_mm[i], 100 * data.PackFactor[i]),
               reverse=True)
print("top->bottom @N=100:", [f"{data.Expr[i]}({OKABE[data.Expr[i]]})" for i in order])
