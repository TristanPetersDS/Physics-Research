# Colourblind-friendly poster figure regeneration — report

**Date:** 2026-06-12
**Scope:** Regenerate the requested poster data figures from the **1M** dataset
with the **Okabe-Ito** colourblind-safe palette, validate colourblind-safety,
and swap them into the poster without altering any layout/formatting.

## Figures regenerated

Figure numbers are the compiled poster numbers (from `poster.aux`). Each new
file carries a `_colorblind` suffix so the palette is obvious from the filename.

| Fig | Content | Source script (1M data) | New file |
|-----|---------|-------------------------|----------|
| **2** | Old-method ("Chooz") analytic angular resolution, 7 detectors | `…/money_plot_paperA_code/regen_fig2_colorblind.py` | `fig/angular_resolution_analytic_ylog_PackFactor_v2Useful_colorblind.pdf` |
| **6** | Money plot — δϑ vs n for Δx = 5/50/150 mm | `parallel/uncertainty_plot.py` (data30) | `fig/parallel/06_money_plot_fit_arctan_log_4p_colorblind.pdf` |
| **7.b** | Sweet spot — δϑ vs segment size (ideal Δx ≈ 73 mm) | `parallel/sweet_spot_plot.py` (data14) | `fig/parallel/sweet_spot_final_colorblind.pdf` |
| **8 (a,b,c)** | FND vs angle at n = 10/100/1000, Δx = 50 mm | `parallel/regen_fnd_1M_cb.py` (fid_1M) | `fig/parallel/FND_n_{10,100,1000}_dx_50_colorblind.pdf` |

### Note on the "6.a" reference
Compiled Fig 6 (money plot) is a **single panel** — it has no sub-panel "a". The
only (a)/(b) figure in that region is **Fig 7**: 7.a = binning-distribution
colormap (`bin_dist_rot0_001wt.pdf`), 7.b = sweet spot. Fig 7.a uses the
**viridis** sequential colormap, which is already colourblind-safe by design
(Okabe-Ito is a *categorical* palette and does not apply to a continuous
heat-map), so it was left unchanged. If "6.a" was intended to mean the binning
colormap, no change is needed — it already passes. Regenerated: Fig 2, 6, 7.b,
and all three Fig 8 panels.

## Palette

Okabe-Ito (centralised in `parallel/palette.py`). Segment-size mapping
(Figs 6, 8 and the sweet-spot fit): **5 mm → vermillion `#D55E00`,
50 mm → bluish-green `#009E73`, 150 mm → blue `#0072B2`**.

Fig 2's seven detector curves were reassigned from the original
green/red/orange/blue/red/gray/black (which had a green–red collision between
DoubleChooz and Checker-3D) to seven distinct Okabe-Ito colours, keeping the
solid = 3D / dashed = 2D linestyle channel:

| Detector | line | old → new |
|----------|------|-----------|
| DoubleChooz | solid (3D) | green → bluish-green `#009E73` |
| Checker-3D | solid (3D) | red → vermillion `#D55E00` |
| SANTA | solid (3D) | orange → orange `#E69F00` |
| NuLat5 | solid (3D) | blue → blue `#0072B2` |
| Checker-2D | dashed (2D) | red → sky-blue `#56B4E9` |
| PROSPECT | dashed (2D) | gray → reddish-purple `#CC79A7` |
| SANDD-CM | dashed (2D) | black → black `#000000` |

## Colourblind validation

`parallel/cvd_validate.py` simulates protanopia / deuteranopia / tritanopia
(Machado et al. 2009, severity 1.0, applied in linear RGB), converts to CIELAB,
and reports the minimum pairwise CIE76 ΔE. A pair is comfortably discriminable
above ΔE ≈ 10; **every figure clears that in every CVD type** (min ΔE):

| Figure | normal | protanopia | deuteranopia | tritanopia |
|--------|:------:|:----------:|:------------:|:----------:|
| Fig 2 (7 curves) | 26.4 | 20.7 | 17.9 | **16.1** |
| Fig 6 (money) | 70.1 | 37.2 | 53.4 | 17.0 |
| Fig 7.b (sweet spot) | 93.9 | 71.7 | 85.3 | 89.9 |
| Fig 8 (FND) | 42.2 | 38.5 | 46.1 | 29.8 |

Fig 2's spatially-adjacent curve pairs were checked separately; the closest is
PROSPECT vs SANTA at ΔE = 17.2 (tritanopia) — still clearly distinct. The
worst case anywhere is ΔE ≈ 16 (Fig 2, tritanopia), well above the ~10
confusability threshold.

## Poster changes

Only the `\includegraphics` **filenames** were changed — every width/height
option, caption, label, minipage, and layout is untouched.

- `content/block2.tex`: Fig 2 → `_colorblind`
- `content/block5.tex`: Fig 6, Fig 7.b, and the three Fig 8 panels → `_colorblind`

The poster compiles cleanly (`pdflatex poster.tex`, exit 0) with the new figures.

### Caveat — Fig 8 θ labels
The tikz key beside each Fig 8 panel hard-codes `\textcolor{blue}{ϑ_min}` and
`\textcolor{red}{ϑ_fit}`. The recoloured panels use Okabe blue for the data/min
line and **vermillion** for the fit/fit line. Vermillion reads as red, so the
labels remain sensible and were **not** modified (no formatting changes). If a
perfect colour match to the key is wanted, the `\textcolor{red}` could later be
set to vermillion `#D55E00` — a one-line change, flagged here rather than made.

## Reproducibility

- `parallel/uncertainty_plot.py`, `parallel/sweet_spot_plot.py` — canonical 1M
  scripts (already Okabe-Ito); run with the save flag to emit the `_colorblind`
  PDFs (Figs 6, 7.b).
- `parallel/regen_fnd_1M_cb.py` — Fig 8; faithfully replicates
  `directionAlgorithm`'s FND + |sin| fit on fid_1M with Okabe colours. Per-panel
  random seeds (`{10:6, 100:0, 1000:4}`) are fixed so the representative
  noisy→sharp progression is reproducible.
- `…/money_plot_paperA_code/regen_fig2_colorblind.py` — Fig 2; reads the
  original `DeltaPhiTable_extra_col.txt` for detector params, overrides only the
  colours (no Paper A data file modified).
- `parallel/cvd_validate.py` — the CVD/ΔE validation above.

## Follow-up: in-diagram LaTeX/TikZ annotation colours (2026-06-12)

The blue/red used *inside* the LaTeX-drawn diagrams and figure keys was swapped to
the Okabe-Ito colours so the annotations match the recoloured plots and pick up
the same colourblind-safe pair. Two new colours are defined in
`config/_preamble.tex`: `OkabeBlue` `#0072B2`, `Vermillion` `#D55E00`.

- **Fig 8 keys** (`block5.tex`): the per-panel key `\textcolor{blue}{ϑ_min}` /
  `\textcolor{red}{ϑ_fit}` → `OkabeBlue` / `Vermillion`, now matching the plot's
  blue data line and vermillion fit line exactly (resolves the earlier caveat).
- **Fig 5 a & b** (`block4.tex`): all `\color{blue}` (rotated axes, MC reference
  vectors/arcs) → `OkabeBlue`; `\color{red}` (experimental vector + θ_ν^exp
  label) → `Vermillion`.

Verified CVD-safe: among `{OkabeBlue, Vermillion, black, gray}` the minimum
pairwise ΔE is 27.1 in all CVD types (closest pair black/gray, luminance-only);
the **OkabeBlue vs Vermillion** pair is ΔE = 91.9 (vs pure blue/red, which is the
weak point for protanopes). Poster recompiles clean. Changes are colour-only.

### Not changed — Fig 4 / block3 (flagged)
`block3.tex` colours the IBD reaction text `{\color{red}e^+}` and
`{\color{green}γγ}` to match the RAT-PAC 2 event-display **image** (Fig 4:
positron red, γ green). That is a genuine red–green pair, but recolouring the
text without re-rendering the event-display image would desync them. It is a
red–green case (not the blue/red requested) and needs the Fig 4 image itself
regenerated with colourblind track colours — left for a separate pass.
