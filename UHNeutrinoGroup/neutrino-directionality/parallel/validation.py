"""Numpy-only descriptive-stats helpers for validating processed IBD datasets.

`summarize` reduces a (vertices, captures) pair to the handful of numbers we
compare between the 1M and 10M runs; `format_table` renders two summaries
side by side. No dependency on main.py / mpi4py.
"""

import numpy as np


def summarize(vertices, captures, seg_size=50):
    vertices = np.asarray(vertices, dtype=float)
    captures = np.asarray(captures, dtype=float)
    coords = captures - vertices
    norms = np.linalg.norm(coords, axis=1)
    r = np.hypot(coords[:, 0], coords[:, 1])
    R = seg_size / np.sqrt(2)
    return {
        "n_vertices": len(vertices),
        "n_captures": len(captures),
        "counts_equal": len(vertices) == len(captures),
        "avg_track_length": float(np.mean(norms)),
        "coords_mean": np.mean(coords, axis=0),
        "coords_std": np.std(coords, axis=0),
        "usable_fraction": float(np.mean(r > R)),
    }


def format_table(s1, s10):
    rows = []
    rows.append(f"{'metric':<24}{'1M':>16}{'10M':>16}")
    rows.append("-" * 56)
    rows.append(f"{'n_vertices':<24}{s1['n_vertices']:>16}{s10['n_vertices']:>16}")
    rows.append(f"{'n_captures':<24}{s1['n_captures']:>16}{s10['n_captures']:>16}")
    rows.append(f"{'counts_equal':<24}{str(s1['counts_equal']):>16}{str(s10['counts_equal']):>16}")
    rows.append(f"{'avg_track_length(mm)':<24}{s1['avg_track_length']:>16.4f}{s10['avg_track_length']:>16.4f}")
    for i, ax in enumerate("xyz"):
        rows.append(f"{'coords_mean_' + ax:<24}{s1['coords_mean'][i]:>16.4f}{s10['coords_mean'][i]:>16.4f}")
    for i, ax in enumerate("xyz"):
        rows.append(f"{'coords_std_' + ax:<24}{s1['coords_std'][i]:>16.4f}{s10['coords_std'][i]:>16.4f}")
    rows.append(f"{'usable_frac(dx=50)':<24}{s1['usable_fraction']:>16.4f}{s10['usable_fraction']:>16.4f}")
    return "\n".join(rows)
