#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: plot_10M.py
Description: Render the money-plot figures from the 10M-dataset campaign
    (data_10M_detected/, data_10M_usable/) with the Okabe-Ito colourblind-safe
    palette. Faithfully mirrors the canonical paper-figure scripts -- the
    detected plot reuses the weighted arctan-in-log fit from uncertainty_plot.py;
    the usable plot is errorbars-only like usable_uncertainty_plot.py -- but
    points at the 10M data and writes dataset-reflecting filenames so nothing
    overwrites the 1M paper figures.

    Output (this directory):
        money_plot_10M_detected.pdf   (detected events, with arctan fits)
        money_plot_10M_usable.pdf     (usable events, errorbars only)

Run from neutrino-directionality/parallel with the repo .venv:
    python plot_10M.py
usetex renders fine through matplotlib's pdf backend (dvips/gs/pdflatex);
it does NOT need dvipng, so we force that backend up front.
"""

import matplotlib
matplotlib.use("pdf")  # usetex -> PDF works without dvipng; show() becomes a no-op

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from palette import SEG_COLOR

plt.rc("font", family="serif", size=16)
plt.rcParams["text.usetex"] = True
plt.rcParams["mathtext.fontset"] = "cm"


# Chosen model to fit to the uncertainty data (matches uncertainty_plot.py).
def model_arctan_4p(n, a, b, c, d):
    return a - d * np.arctan(np.log10((n + b)) / c)


def load_series(path):
    """Read a func_iter file (cols: n, sigma_deg, sigma_err), dropping the
    first row whose error bar is too large (same convention as the paper
    scripts)."""
    n, sig, err = [], [], []
    with open(path, "r") as f:
        for line in f:
            elems = line.split()
            if len(elems) < 3:
                continue
            n.append(float(elems[0]))
            sig.append(float(elems[1]))
            err.append(float(elems[2]))
    return np.array(n[1:]), np.array(sig[1:]), np.array(err[1:])


def fit_arctan(n, sig, err):
    """Weighted arctan-in-log-space fit, as in uncertainty_plot.py. Returns
    (x_fit, y_fit) sampling curves, or (None, None) if the fit fails."""
    y_log = np.log10(sig)
    yerr_log = err / (sig * np.log(10))
    try:
        popt, _ = curve_fit(
            model_arctan_4p, n, y_log, p0=[1, 1, 1, 1],
            sigma=yerr_log, absolute_sigma=True, maxfev=20000,
        )
    except Exception as e:
        print(f"  [warn] arctan fit failed: {e}")
        return None, None
    x_fit = np.logspace(np.log10(n[0]), np.log10(n[-1]), 128)
    y_fit = 10 ** model_arctan_4p(x_fit, *popt)
    return x_fit, y_fit


DX_LIST = [5, 50, 150]


def make_plot(base_dir, suffix, with_fits, out_pdf):
    """Render one money plot. suffix is 'detected' or 'usable'."""
    plt.figure()
    series = {}
    for dx in DX_LIST:
        path = f"{base_dir}/func_iter_dx_{dx}_{suffix}.txt"
        n, sig, err = load_series(path)
        series[dx] = (n, sig, err)
        print(f"  dx={dx:>3}: {len(n)} points, n={int(n[0])}..{int(n[-1])}, "
              f"sigma {sig[0]:.2f} -> {sig[-1]:.3f} deg")

    # Raw data: detected uses dashed connectors (fit lines carry the eye),
    # usable uses solid connectors and is the only line (errorbars-only plot).
    fmt = ".--" if with_fits else ".-"
    label = None if with_fits else True
    for dx in DX_LIST:
        n, sig, err = series[dx]
        kw = {} if with_fits else {"label": f"$\\Delta x$ = {dx} mm"}
        plt.errorbar(n, sig, yerr=err, fmt=fmt, color=SEG_COLOR[dx], capsize=3, **kw)

    if with_fits:
        for dx in DX_LIST:
            n, sig, err = series[dx]
            x_fit, y_fit = fit_arctan(n, sig, err)
            if x_fit is not None:
                plt.plot(x_fit, y_fit, "-", color=SEG_COLOR[dx], lw=2,
                         label=f"$\\Delta x = {dx} \\,\\mathrm{{mm}}$")

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel(("C" if suffix == "detected" else "Usable c") + "ounts $n$")
    plt.ylabel("Angular uncertainty $\\delta \\vartheta$ (${}^\\circ$)")
    plt.legend(framealpha=1.0)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.savefig(out_pdf, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"  -> wrote {out_pdf}\n")


if __name__ == "__main__":
    print("detected (10M):")
    make_plot("data_10M_detected", "detected", with_fits=True,
              out_pdf="money_plot_10M_detected.pdf")
    print("usable (10M):")
    make_plot("data_10M_usable", "usable", with_fits=False,
              out_pdf="money_plot_10M_usable.pdf")
    print("done.")
