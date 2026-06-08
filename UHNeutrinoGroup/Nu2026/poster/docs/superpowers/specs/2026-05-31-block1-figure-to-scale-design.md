# Block-1 Figure: Correct the Scale — Design

**Date:** 2026-05-31
**Status:** IMPLEMENTED — via a simpler route than the reconstruction described below (see "Final approach").

## Final approach (implemented)

`content/block1.tex` includes the original figure at absolute dimensions — `\includegraphics[width=17.405cm,height=7.653cm]{...}` — so its **data area is exactly 16 cm × 6 cm on the printed 4 ft × 3 ft poster**: true **1:1 physical (life-size) scale**, where the axes cover their labeled distances. Verified on the rendered poster: data area 16.00 × 6.01 cm (scale 1.000 : 1); the 14.5 cm Prospect bar measures 14.5 cm, SANDD 0.5 cm. The non-uniform width:height ratio also corrects the source PDF's 1.241× horizontal stretch. Poster builds with 0 overfull.

This evolved in two steps: (1) an isotropy-only fix (`\scalebox{0.806}[1]` — equal-aspect but still ~1.35× magnified), then (2) — at the group's request that the axes be ruler-accurate on the physical poster — the absolute-size version above. **Accepted tradeoffs:** the figure is physically small (16 × 6 cm), so the axis/segment labels are condensed (~24%) and render below 28 pt, and block 1 now has spare vertical whitespace below the figure. Absolute `cm` dimensions are intentional (they make the 1:1 independent of `\linewidth`); do not convert back to `\linewidth`-relative sizing or the life-size property breaks.

The pgfplots reconstruction (below) was fully built and verified to scale, but faithfully de-stretching compressed the vertical axis enough to **cramp the four stacked scale-bar labels**. Rather than restyle/reposition, the user chose the direct PDF rescale. Reconstruction artifacts (`fig/src/`, `fig/segment_scale_diagram.pdf`) were removed.

## Problem (original analysis — still valid)

`fig/asy_fig_1_paperB.pdf` (block 1, "Localization of IBD Source") is captioned as showing **relative scale** of a neutron trajectory vs. four detectors' segment sizes — but it is rendered **1.24× stretched horizontally** (measured: x = 118.5 px/cm, y = 95.5 px/cm). Root cause: the source plot did not lock equal axis aspect, so x and y scaled independently. There is **no source file** in the repo, only the exported PDF.

## Decision

- **Faithful de-stretch:** reproduce the figure's content exactly, corrected to true 1:1 scale. Keep monochrome black, Computer Modern (serif), and the same axes/ranges. No restyle.
- **Tool:** standalone **TikZ/pgfplots** with `axis equal` (guarantees 1 cm-x == 1 cm-y). Native to the LaTeX stack, vector, font-consistent.

## Data (extracted from the PDF vector content stream — verified exact)

Method: inflate the PDF's FlateDecode streams, parse `m`/`l` path operators, calibrate stream-space → cm via the axis-frame spines. Verification that calibration is exact: the recovered scale-bar lengths come out to **14.50 / 8.50 / 6.00 cm** (Prospect/Bugey/MAD) — their exact nominal values.

- **Trajectory:** 29-vertex polyline, IBD vertex (0,0) → capture (1.15, 0.83), wandering to x≈4.78, y∈[−1.08, 2.58]. (saved: `/tmp/traj_cm.json`; will be embedded in the figure source.)
- **Scale bars** (horizontal, left-aligned): SANDD 0.5 cm, MAD 6 cm (y=−0.5), Bugey 8.5 cm (y=−1.5), Prospect 14.5 cm (y=−2.5); SANDD bar y and all bar start-x to be read off during implementation.
- **Markers:** ○ (open) at IBD vertex (0,0); ● (filled) at capture (1.15, 0.83).
- **Axes:** x∈[−8,8], y∈[−3,3], integer ticks, labels "x (cm)" / "y (cm)".

## Files

- **New:** `fig/src/segment_scale_diagram.tex` (standalone pgfplots source — embeds the trajectory + bars) → compiled to `fig/segment_scale_diagram.pdf`.
- **Edit:** `content/block1.tex` — swap `\includegraphics{...asy_fig_1_paperB.pdf}` → `{fig/segment_scale_diagram.pdf}` (keep caption/label).
- **Untouched:** `fig/asy_fig_1_paperB.pdf` retained as backup.

## Verification

1. Render `fig/segment_scale_diagram.pdf`; measure **anisotropy = 1.000** (x px/cm == y px/cm).
2. Confirm the trajectory data plotted == extracted data (same cm coords) and the figure reads as the original un-stretched (visual side-by-side).
3. Rebuild the poster (two-pass), confirm 0 overfull, block 1 figure looks correct and fits.

## Notes

- Not a git repo — spec saved, not committed.
- This also remediates the "no regenerable source" problem: the new figure ships with its `.tex` source.
