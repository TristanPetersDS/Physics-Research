# Figure Style Guide — Neutrino 2026 Poster

**Living document.** Defines the *target* visual style for all data figures so that, once the
plot-generation code + data are available again, every figure can be regenerated to one
consistent look. Also logs the figure-related changes already applied directly in LaTeX.

Maintainer workflow: settle a choice here → when you regenerate a plot, apply the spec →
tick it off in the per-figure table. LaTeX-only adjustments (geometry, captions, embed size)
are made directly in `content/` and recorded in the changelog at the bottom.

Last updated: 2026-05-31.

---

## 0. Why this doc exists (generator status)

As of 2026-05-31 the **final** poster figures do **not** have their exact generators in this repo:

| Figure (as used)                         | In-repo generator?                          |
|------------------------------------------|---------------------------------------------|
| `06_money_plot_fit_arctan_log_4p.pdf`    | **No.** `fig/parallel/money_plot.py` is an *older* variant (default matplotlib colors, quadratic/cubic helpers, no arctan fit) — not this figure. |
| `bin_dist_rot*_001wt.pdf` (heatmaps)     | **No.** Pre-rendered from external RATPAC analysis. |
| `FND_n_*_dx_50.pdf` (spread panels)      | **No.** Pre-rendered from external RATPAC analysis. |

Consequence: **palette/typography changes are deferred to regeneration** and captured here.
Anything achievable purely in LaTeX (embed size, placement, captions) is done now and logged.

---

## 1. Color palette

### 1a. Categorical (lines / markers / series) — colorblind-safe

> **CONFIRMED 2026-05-31: Option B (Blue / Orange / Black).** This is the single categorical
> palette for *every* multi-series plot. Option A is retained below for the record only.

Three-series palette (proposed **Option B — Blue / Orange / Black**, max CVD-robustness):

| Token | Hex       | RGB           | Role examples |
|-------|-----------|---------------|---------------|
| `C1`  | `#0072B2` | 0,114,178     | money plot Δx = 5 mm;  FND θ_min |
| `C2`  | `#E69F00` | 230,159,0     | money plot Δx = 50 mm; FND θ_fit |
| `C3`  | `#000000` | 0,0,0         | money plot Δx = 150 mm; FND θ_true (reference) |

Alternative kept on record (**Option A — Okabe, order-preserving**): `#D55E00` (5 mm) /
`#009E73` (50 mm) / `#0072B2` (150 mm). Preserves the current warm→green→cool reading order
but the 50/150 pair is weaker under deuteranopia.

**Enhancement regardless of palette:** give each series a distinct *marker shape*
(circle / square / triangle) and/or line style so the plot also survives grayscale printing.
The money plot already uses solid = fit curve, error-bar markers = data; keep that and add
per-series marker shapes.

### 1b. Sequential (heatmaps / matrices) — keep **viridis**

The binning matrices already use **viridis** (perceptually uniform, CVD-safe). **Keep it.**
- Colorbar label: `Counts`.
- Cell annotations: white text on dark cells, black on light cells (already auto-handled).
- Do **not** switch heatmaps to a rainbow/jet map.

---

## 2. Typography & sizing

Goal: figure text is legible at poster viewing distance (~1–1.5 m) and roughly consistent
across panels. Body text floor on this poster is 28 pt; axis/tick labels may be smaller by
convention but should not look tiny.

Uniform matplotlib `rcParams` recipe (starting point — measure on the printed/embedded size
and scale `BASE` up if labels read small):

```python
BASE = 14
import matplotlib as mpl
mpl.rcParams.update({
    "font.family":      "sans-serif",     # match poster body (Helvetica/Arial/DejaVu Sans)
    "font.size":        BASE,
    "axes.labelsize":   BASE + 2,
    "axes.titlesize":   BASE + 2,
    "xtick.labelsize":  BASE - 1,
    "ytick.labelsize":  BASE - 1,
    "legend.fontsize":  BASE,
    "lines.linewidth":  2.0,
    "lines.markersize": 6,
    "axes.linewidth":   1.0,
    "pdf.fonttype":     42,               # embed TrueType (avoid Type-3)
    "savefig.bbox":     "tight",
    "savefig.facecolor":"white",
})
```

Key rule: figures are **enlarged** when embedded on the poster, so do not export them tiny.
Export at roughly the physical width they occupy (money plot ≈ 17 cm ≈ 6.7 in wide) so the
in-figure font size maps predictably to printed size.

---

## 3. Line / marker / error-bar conventions

- Data points: markers with `capsize=3` error bars; fit/theory: solid line, no markers.
- `grid(True, which="both", linestyle="--", linewidth=0.5)` on log axes (matches current money plot).
- Legends: frame on, upper-right unless it occludes data; use the math labels already in use
  (`$\Delta x = 5$ mm`, etc.).

---

## 4. Export settings

- Format: **PDF** (vector). One PNG exception remains: the RAT-PAC raster visualization.
- `bbox_inches="tight"`, white background, fonts embedded (`pdf.fonttype=42`).
- Keep a stable aspect ratio per figure class so multi-panel rows align:
  - Money plot: ~1.3:1 landscape (current 419×320 pt).
  - Binning heatmap: square data area + right colorbar.
  - FND spread panels: identical size across n (embedded at `height=3.05in` in LaTeX).

---

## 5. Per-figure target spec

| Figure | Palette | Notes | Regenerated? |
|--------|---------|-------|--------------|
| Money plot (`06_money_plot_fit_arctan_log_4p.pdf`) | Categorical C1/C2/C3 + per-series markers | Δx 5/50/150 mm → C1/C2/C3; keep arctan fit as solid line | ☐ |
| Binning heatmaps (`bin_dist_rot*_001wt.pdf`) | viridis | Already compliant; only regenerate if fonts need enlarging | ☐ |
| FND spread (`FND_n_*_dx_50.pdf`) | Categorical: θ_true→C3, θ_min→C1, θ_fit→C2 | Match money-plot palette; legend currently external in LaTeX | ☐ |
| Sweet-spot (`sweet_spot_final.pdf`) | Categorical: data→C3, fit→C2 | Optimal Δx ≈ 73 mm; currently red fit + black data; recolor to match money plot | ☐ |

---

## 6. LaTeX-side changelog (applied directly, no regeneration needed)

- **2026-06-10 — block 2 detector gallery + Fig 2 enlarge:**
  - Replaced the ψ-geometry `picture` diagram with a four-detector geometry gallery
    (Double Chooz / Checker-3D / NuLat5 / SANTA — the 3D group of Fig 2's legend), assets
    staged as `fig/detector_*` ([b]-aligned minipages, shared caption, `height=6.5cm`).
  - Enlarged the Chooz angular-resolution plot `0.40 → 0.47\linewidth`.
- **2026-06-10 — block 4 poster-format rework:**
  - Bullets → numbered 5-step algorithm (`enumerate`; green bold numbers via new
    `\setlist[enumerate,1]` in the preamble — same no-marker footgun defense as itemize).
  - Added Paper B's boxed $L^2$-norm equation as step 4.
  - The two `picture` diagrams re-cropped/re-scaled to matched heights
    (panel (b)'s picture box tightened to its drawn content `(6.7,4.3)(2.3,-0.1)`).
- **2026-06-10 — caption/whitespace pass (all blocks):**
  - Captions now live in minipages aligned with their figures (blocks 1, 2, 3, 5 money plot).
  - block 3: RAT-PAC render enlarged + centered; caption tightened (was overflowing the
    block border at the narrower caption width — re-balanced to image `0.50\linewidth`,
    caption minipage `0.62\linewidth`).
  - block 1: `\vfill` above/below the (fixed-size 1:1) figure band restored.
- **2026-06-10 — banner logos:** circular white discs via new `\titlelogocirc`,
  positioned absolutely in the banner TikZ overlay; UH seal + black LLNL "LL" icon are
  now true vectors (see CLAUDE.md "Logos workflow"). MTV remains the one raster logo.

- **2026-05-31 — block 5 top region (money plot):**
  - Fixed silent-shrink (CLAUDE.md footgun #6): `\includegraphics[width=0.45\linewidth]`
    → `width=\linewidth` inside its minipage, so the plot fills its ~17 cm half instead of ~7 cm.
  - Re-laid the Key findings box + money plot as a top-aligned **balanced split**
    (`[t]` minipages + `\vspace{0pt}` anchor trick).
  - Moved `\label` to immediately after `\captionof{figure}{…}` so the cross-reference resolves
    (was a stray `\label` inside an empty `figure`, a likely source of the `[?]` ref bug).
  - Italicized `$n$` in the findings bullets for consistency with the plot axis.

- **2026-05-31 — caption rework (concise + descriptive):**
  - `block3` RAT-PAC caption: rewrote the 4-line run-on, **fixed the missing close-paren**, and
    restated track colors compactly.
  - `block1` segmentation caption: trimmed; kept the "drawn to scale" emphasis.
  - `block5` ×3: money plot → "δϑ versus n …"; binning → tightened; FND → replaced the vague
    "Explanation of angles and spread" with what the panels actually show (min/fit → true as n grows).
  - `block4` caption left as-is (already concise; verbose alternatives stay commented out).

- **2026-05-31 — whitespace pass (blocks 1, 2, 4):**
  - `block2`: enlarged the angular-resolution plot `0.40\linewidth → 0.62\linewidth`, centered it,
    `\vfill`-distributed it; trimmed the caption; **fixed the `[?]` ref** (`\cite{Duvall:2024cae}`
    → hard-coded `[2]`, matching the footer); fixed "intial" typo.
  - `block4`: replaced hard-coded `\vspace{2cm}` with `\vfill` (top+bottom) and enlarged the
    geometry diagrams (`\unitlength` `.04 → .045\linewidth`).
  - `block1`: `\vfill` above+below the true-1:1 figure to center it (figure size is fixed by the
    1:1 constraint, so the band can only be balanced, not removed).
- **2026-05-31 — block 5 sweet-spot result added:**
  - Reduced the 3-panel binning angle-sweep to one representative panel ($\vartheta_\nu=0^\circ$)
    and paired it with the **sweet-spot figure** (`sweet_spot_final.pdf`, optimal
    $\Delta x\approx73$ mm) in one row, so the new result cost ~no extra height.
  - Added a gold `\highlight` **callout: "Optimal segment size: $\Delta x\approx73$ mm."**
  - Panels sized `height=9cm`; verified no overfull `\vbox`. FND spread + Future work unchanged.
  - The $-30^\circ/-45^\circ$ binning PDFs still exist in `fig/`; they're just no longer shown.

---

## 7. Open decisions

- [x] **Categorical palette confirmed: Option B (Blue / Orange / Black)** (2026-05-31).
- [ ] Whether to add per-series marker shapes (grayscale safety).
- [ ] Final `BASE` font size after measuring embedded legibility.
