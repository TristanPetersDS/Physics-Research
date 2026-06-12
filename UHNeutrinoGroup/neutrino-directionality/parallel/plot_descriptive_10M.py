#!/usr/bin/env python3
"""Descriptive 10M figures, the processor/main.py DataProcessor family, rendered
from the distilled capture coordinates.

DataProcessor.setKind("capture") computes coords = (last neutron step) - (IBD
vertex) = trackPos - mcx. That is exactly captures - vertices, which the parallel
pipeline already saved to events/fid_10M_unfiltered_{captures,vertices}.npy. So
the cloud / track-length / spatial / angular / segment-colormap plots need no
re-parse of the 40 GB neutrons.txt -- only the per-step track plots do (see
plot_tracks_10M.py). Rendered here with the Okabe-Ito palette.

    python plot_descriptive_10M.py

Output -> data_10M_descriptive/*.pdf
"""
import os

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
import numpy as np

from palette import OKABE_ITO

plt.rc("font", family="serif", size=16)
plt.rcParams["text.usetex"] = True
plt.rcParams["mathtext.fontset"] = "cm"

OUT = "data_10M_descriptive"
V10 = "events/fid_10M_unfiltered_vertices.npy"
C10 = "events/fid_10M_unfiltered_captures.npy"


def load_coords():
    v = np.load(V10)
    c = np.load(C10)
    return c - v  # (N,3) capture displacement relative to the IBD vertex


def fig_track_length(coords):
    d = np.linalg.norm(coords, axis=1)
    plt.figure()
    plt.hist(d, bins=64, color=OKABE_ITO["orange"], histtype="step", linewidth=2)
    plt.axvline(d.mean(), color=OKABE_ITO["vermillion"], ls="--", lw=1.5,
                label=f"mean = {d.mean():.1f} mm")
    plt.xlabel("$d_n$ (mm)")
    plt.ylabel("Counts")
    plt.legend()
    plt.savefig(f"{OUT}/descr_10M_capture_track_length.pdf", bbox_inches="tight")
    plt.close()
    print(f"  capture track length: mean={d.mean():.2f} mm, N={len(d):,}")


def fig_cloud(coords, lim=100, n_show=120_000):
    x, y = coords[:, 0], coords[:, 1]
    idx = np.random.choice(len(x), size=min(n_show, len(x)), replace=False)
    plt.figure(figsize=(6, 6))
    plt.plot(x[idx], y[idx], ".", markersize=1, color=OKABE_ITO["blue"], alpha=0.5)
    plt.xlabel("x (mm)")
    plt.ylabel("y (mm)")
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)
    plt.gca().set_aspect("equal")
    plt.title("capture")
    plt.savefig(f"{OUT}/descr_10M_cloud_capture.pdf", bbox_inches="tight")
    plt.close()


def fig_cloud_density(coords, lim=100):
    x, y = coords[:, 0], coords[:, 1]
    m = (np.abs(x) <= lim) & (np.abs(y) <= lim)
    plt.figure(figsize=(6, 5))
    plt.hist2d(x[m], y[m], bins=200, cmap="viridis")
    plt.colorbar(label="Counts")
    plt.xlabel("x (mm)")
    plt.ylabel("y (mm)")
    plt.gca().set_aspect("equal")
    plt.title("capture density")
    plt.savefig(f"{OUT}/descr_10M_cloud_capture_density.pdf", bbox_inches="tight")
    plt.close()


def fig_spatial(coords):
    for dim, j in (("x", 0), ("y", 1), ("z", 2)):
        plt.figure()
        plt.hist(coords[:, j], bins=128, histtype="step",
                 color=OKABE_ITO["bluish_green"], linewidth=1.5)
        plt.grid(True, ls="--", lw=0.5)
        plt.title(f"{dim}-location histogram (capture)")
        plt.xlabel(f"{dim} (mm)")
        plt.ylabel("Counts")
        plt.savefig(f"{OUT}/descr_10M_spatial_{dim}.pdf", bbox_inches="tight")
        plt.close()


def fig_angular(coords):
    theta = np.arctan2(coords[:, 1], coords[:, 0])
    counts, edges = np.histogram(theta, bins=np.linspace(-np.pi, np.pi, 37))
    centers = (edges[:-1] + edges[1:]) / 2
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    ax.bar(centers, counts, width=2 * np.pi / 36, bottom=0,
           edgecolor=OKABE_ITO["blue"], facecolor="none", linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2])
    ax.set_xticklabels(["0", "$\\pi/2$", "$\\pi$", "$3\\pi/2$"])
    ax.set_title("capture azimuthal distribution", va="bottom")
    plt.savefig(f"{OUT}/descr_10M_angular_capture.pdf", bbox_inches="tight")
    plt.close()


def fig_bin_colormap(coords, cube_size=50, grid_size=9):
    half = cube_size * grid_size / 2.0
    x, y = coords[:, 0], coords[:, 1]
    # imshow row 0 = top, so histogram y reversed to match detector orientation.
    H, _, _ = np.histogram2d(x, y, bins=grid_size,
                             range=[[-half, half], [-half, half]])
    caps = H.T[::-1, :]
    plt.figure(figsize=(6.2, 5))
    im = plt.imshow(caps, cmap="viridis", extent=(-half, half, -half, half))
    cbar = plt.colorbar(im)
    cbar.set_label("Counts")
    plt.xlabel("x (mm)")
    plt.ylabel("y (mm)")
    cmax = caps.max()
    for i in range(grid_size):
        for j in range(grid_size):
            val = int(caps[i, j])
            plt.text((j - grid_size // 2) * cube_size,
                     -(i - grid_size // 2) * cube_size, f"{val}",
                     ha="center", va="center", fontsize=7,
                     color=("w" if val <= 0.6 * cmax else "k"))
    plt.title(f"capture segmentation, $\\Delta x={cube_size}$ mm", fontsize=13, pad=12)
    plt.savefig(f"{OUT}/descr_10M_bin_cmap_0deg.pdf", bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    coords = load_coords()
    print(f"loaded {len(coords):,} capture displacements")
    fig_track_length(coords)
    fig_cloud(coords)
    fig_cloud_density(coords)
    fig_spatial(coords)
    fig_angular(coords)
    fig_bin_colormap(coords)
    print(f"done -> {OUT}/")
