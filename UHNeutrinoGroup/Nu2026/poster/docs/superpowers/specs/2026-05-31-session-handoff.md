# Poster — Session Handoff & Current State (2026-05-31)

Read this + `CLAUDE.md` to continue work in a fresh chat. This file is the session log; CLAUDE.md is the canonical reference.

## Build command (use this; it is consistent and handles the 2-pass)

```bash
cd /home/beefboi/Desktop/Research/Nu2026/poster
latexmk -pdf -interaction=nonstopmode poster.tex
```

`latexmk` auto-detects the second pass needed by the TikZ `[remember picture,overlay]` title-banner/footer. Equivalent manual form: `pdflatex -interaction=nonstopmode -halt-on-error poster.tex` **run twice**. `poster.tex` is the only build target; output is `poster.pdf`. A single pass silently drops the banner + footer. Clean artifacts anytime: `latexmk -c` (keeps `poster.pdf`).

To inspect a region at true scale, render and crop: `pdftoppm -png -r <dpi> [-x -y -W -H] poster.pdf out` (page is exactly 121.92×91.44 cm, so px↔cm is `dpi/2.54`).

## What was done this session (all complete + verified)

1. **Layout overhaul** — body is now driven by two knobs in `config/_preamble.tex`: `\postermargin` (M = 1.5 cm, every gap) and `\blockinnerpad` (P = 0.8 cm, internal box padding). Equal margins everywhere, equal columns (`\colwidth`), derived `\bodyheight` (65.44 cm), 28 pt font floor. Spec: `2026-05-31-poster-equal-margins-fonts-design.md`.
2. **CLAUDE.md synced** to the new layout values.
3. **Block-1 figure → true 1:1 physical scale** — `content/block1.tex` includes `fig/asy_fig_1_paperB.pdf` at absolute `17.405cm × 7.653cm` so the axes are life-size on the printed poster (14.5 cm bar measures 14.5 cm). Spec: `2026-05-31-block1-figure-to-scale-design.md`.
4. **Block-5 Figure 6 (FND panels)** — enlarged the three FND plots to `\includegraphics[height=3.05in]` so each plot area (~6.2–6.4 cm tall) matches Figure 5's heatmap **grid** height; moved the ϑ_true/ϑ_min/ϑ_fit legend **outside to the right** (colorbar-style) at `\fontsize{18}{22}`; minipages stay `0.32\textwidth`.

## Files changed (vs `.bak` baselines kept alongside)

| File | Change | Backup |
|---|---|---|
| `poster.tex` | body: top spacer, equal `\colwidth` columns via `\centerline`, M gaps | `poster.tex.bak` |
| `config/_preamble.tex` | knobs, derived lengths, internal padding, 28 pt font floor | `config/_preamble.tex.bak` |
| `content/block1.tex` | figure → absolute 1:1 size (one `\includegraphics` line) | **none** (was `width=0.79\linewidth`) |
| `content/block5.tex` | Figure 6 panels: height-sized + right-side legend | `content/block5.tex.bak` |

## Overleaf merge (still pending on user's side)

Walkthrough given in chat. **Two caveats that are NOT in this session's diffs:**
- The **4 ft × 3 ft page-size line** (`poster.tex` ~line 56: `\usepackage[size=custom,width=121.92,height=91.44,scale=1.25]{beamerposter}`) predates this session — it was already in the `.bak` baseline. The layout constants are tuned to the **91.44 cm height** (the `68.44cm` in `\bodyheight` = 91.44 − 17.4 banner − 5.6 footer). If the Overleaf project is not already at this size, the page-size line must be set too, or the body mis-fits. Safest merge = replace the 4 files wholesale.
- The **footer QR path** (`content/footer.tex` → `content/ArXiV_QR_code.png`) also predates this session; verify it matches the Overleaf folder layout.

## Insights / gotchas discovered (important)

- **`\textwidth` inside a beamer minipage = the minipage's width, not the block width.** This bit Figure 6: `width=0.28\textwidth` inside a `0.32\textwidth` minipage rendered at 0.28 × 11.8 cm ≈ 3.3 cm (tiny), not 0.28 × 36.76 cm. **Size figures inside minipages by absolute `height=`/`width=` (cm/in) or by `\linewidth`, never `\textwidth`.** (Hero block `\textwidth`/`\linewidth` = 36.76 cm at top level, measured via `\typeout{\the\textwidth}`.)
- **Safe layout edits = change VALUES of the existing length constants only.** A prior (2026-05-29/30) wholesale preamble rewrite silently truncated the hero block (overfull `\vbox`); never re-do that. See CLAUDE.md "Layout overhaul".
- **Equal page margins via centering:** the beamerposter text block is page-centered, so wrapping the body (width `\paperwidth−2M`) in `\centerline` yields exactly M margins with no hardcoded offset.
- **PDF vector extraction** (for the block-1 1:1 work): zlib-inflate the PDF content streams, parse `m`/`l` path ops, calibrate via the axis-frame spines. Reusable for recovering plotted data from a figure PDF.

## Known issues / remaining TODO

- **Pre-existing overfull `\hbox`** in `content/footer.tex` (lines ~31–33) — from the `\hspace*{-5.5cm}` reference-column hack. Harmless (always been there) but worth cleaning.
- **Sub-28 pt text in two figures** (deliberate, but violates the conference 28 pt floor): block-1 figure labels (cost of true 1:1) and the block-5 Figure 6 legend (18 pt). Revisit if strict compliance is required.
- **Deferred guideline items** (see `conference_guidelines` memory): sans-serif body (poster uses `\usefonttheme{serif}`), off-white background (currently pure white), colorblind-safe palette (green-heavy theme; check figures for red/green — Fig 6 uses red/blue/gray which is acceptable).
- **`LLNL-POST-XXXXXX`** placeholder in `content/footer.tex` acknowledgements — replace before submission.
- **Content finalization** (from the to-do list at the top of `poster.tex`): figure caption `[?]` cross-ref rendering bug, consistent figure formatting/coloring, finalize text + object placement per block.

## Verification done

All builds: 0 overfull `\vbox`, 0 errors, page 3456×2592 pt (48×36 in). Geometry measured from rendered PDF (margins all = 1.5 cm; columns equal; block-1 data area = 16.00×6.01 cm = 1:1; Fig 6 plot ≈ Fig 5 grid height). Hero block (block 5) renders fully — no truncation.
