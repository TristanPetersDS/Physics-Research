#!/usr/bin/env python3
"""CVD-validate the regenerated poster figure palettes.

For each figure, simulate normal vision plus protanopia / deuteranopia /
tritanopia (Machado et al. 2009 severity-1.0 matrices, applied in linear RGB),
convert to CIELAB, and report the minimum pairwise CIE76 Delta-E. A pair stays
discriminable if Delta-E is comfortably above ~10; we flag anything < 10.

    python cvd_validate.py
"""
import itertools

import numpy as np

# Machado et al. 2009, severity 1.0 (operate on linear RGB).
CVD = {
    "protanopia": np.array([[0.152286, 1.052583, -0.204868],
                            [0.114503, 0.786281, 0.099216],
                            [-0.003882, -0.048116, 1.051998]]),
    "deuteranopia": np.array([[0.367322, 0.860646, -0.227968],
                              [0.280085, 0.672501, 0.047413],
                              [-0.011820, 0.042940, 0.968881]]),
    "tritanopia": np.array([[1.255528, -0.076749, -0.178779],
                            [-0.078411, 0.930809, 0.147602],
                            [0.004733, 0.691367, 0.303900]]),
}


def hex2srgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def srgb2lin(c):
    return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)


def lin2srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c > 0.0031308, 1.055 * c ** (1 / 2.4) - 0.055, 12.92 * c)


def srgb2lab(srgb):
    lin = srgb2lin(srgb)
    M = np.array([[0.4124, 0.3576, 0.1805],
                  [0.2126, 0.7152, 0.0722],
                  [0.0193, 0.1192, 0.9505]])
    xyz = M @ lin
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])  # D65 white

    def f(t):
        return np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    fx, fy, fz = f(xyz[0]), f(xyz[1]), f(xyz[2])
    return np.array([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)])


def simulate(srgb, kind):
    if kind == "normal":
        return srgb
    return lin2srgb(CVD[kind] @ srgb2lin(srgb))


def min_deltaE(palette):
    """Returns (min_dE_overall, {kind: (min_dE, worst_pair)})."""
    names = list(palette)
    out = {}
    overall = np.inf
    for kind in ("normal", "protanopia", "deuteranopia", "tritanopia"):
        labs = {n: srgb2lab(simulate(hex2srgb(palette[n]), kind)) for n in names}
        worst, wp = np.inf, None
        for a, b in itertools.combinations(names, 2):
            dE = float(np.linalg.norm(labs[a] - labs[b]))
            if dE < worst:
                worst, wp = dE, (a, b)
        out[kind] = (worst, wp)
        overall = min(overall, worst)
    return overall, out


# Palettes actually used in each regenerated figure.
FIGS = {
    "Fig 2  old-method (7 detector curves)": {
        "DoubleChooz": "#009E73", "Checker-3D": "#D55E00", "SANTA": "#E69F00",
        "NuLat5": "#0072B2", "Checker-2D": "#56B4E9", "PROSPECT": "#CC79A7",
        "SANDD-CM": "#000000",
    },
    "Fig 6  money plot (segment sizes)": {
        "5mm": "#D55E00", "50mm": "#009E73", "150mm": "#0072B2",
    },
    "Fig 7.b sweet spot": {
        "data(black)": "#000000", "fit(vermillion)": "#D55E00",
    },
    "Fig 8  FND panels": {
        "FND(blue)": "#0072B2", "fit(vermillion)": "#D55E00", "true(gray)": "#808080",
    },
}

# Spatially-adjacent curve pairs in Fig 2 (top->bottom @N=100) -- the pairs that
# most need to stay distinct; same-linestyle adjacencies matter most.
FIG2_ADJ = [("DoubleChooz", "Checker-3D"), ("Checker-3D", "PROSPECT"),
            ("PROSPECT", "SANTA"), ("SANTA", "Checker-2D"),
            ("Checker-2D", "NuLat5"), ("NuLat5", "SANDD-CM")]

if __name__ == "__main__":
    print("CIE76 Delta-E, minimum over all colour pairs (flag < 10):\n")
    for fig, pal in FIGS.items():
        overall, out = min_deltaE(pal)
        flag = "  <-- FLAG" if overall < 10 else ""
        print(f"{fig}{flag}")
        for kind, (dE, pair) in out.items():
            mark = " !" if dE < 10 else ""
            print(f"    {kind:13s} min dE = {dE:5.1f}  ({pair[0]} vs {pair[1]}){mark}")
        print()

    print("Fig 2 spatially-adjacent curve pairs (worst CVD case each):")
    pal2 = FIGS["Fig 2  old-method (7 detector curves)"]
    for a, b in FIG2_ADJ:
        worst, wk = np.inf, None
        for kind in ("normal", "protanopia", "deuteranopia", "tritanopia"):
            la = srgb2lab(simulate(hex2srgb(pal2[a]), kind))
            lb = srgb2lab(simulate(hex2srgb(pal2[b]), kind))
            dE = float(np.linalg.norm(la - lb))
            if dE < worst:
                worst, wk = dE, kind
        mark = " !FLAG" if worst < 10 else ""
        print(f"    {a:12s} vs {b:12s} worst dE = {worst:5.1f} ({wk}){mark}")
