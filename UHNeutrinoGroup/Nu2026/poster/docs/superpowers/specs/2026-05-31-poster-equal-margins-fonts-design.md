# Poster Layout: Equal Margins, Internal Padding, 28 pt Font Floor — Design

**Date:** 2026-05-31
**Status:** Validated in scratch build; awaiting sign-off before applying to canonical source.
**Supersedes approach in:** `2026-05-29-poster-layout-overhaul-design.md` / `2026-05-30-layout-overhaul-debug-notes.md` (the parameterized *wholesale-rewrite* approach that silently truncated the hero block — see "Safety rationale").

## Goal

At the new 48″ × 36″ size, make the body layout visually consistent and reclaim wasted space, plus meet the Neutrino 2026 28 pt font minimum:

1. **One unified margin `M`** for every gap: top, bottom, left, right, col1→col2, col2→col3, and the vertical gap between the two stacked boxes in cols 1–2.
2. **Equal column widths** (currently 37.8 / 37.8 / 41.45 cm → all equal).
3. **Equal column heights** (all = body height).
4. **More content space** (body currently 58.7 cm with an ~8 cm dead band above the footer).
5. **Internal padding `P`** inside every box (top/bottom/left/right), fixing content rendering too close to the title ribbon (currently 0.10 cm gap).
6. **28 pt font floor** — no text below 28 pt (guideline: *"Font size of at least 28 pt"*).

## Decisions

- **M = 1.5 cm** (unified margin)
- **P = 0.8 cm** (internal box padding)
- **Font floor = 28 pt** — `\tiny`/`\scriptsize`/`\footnotesize`/`\small` all redefined to `\fontsize{28}{34}\selectfont`. (At `scale=1.25`, those rendered 15/18/21.6/25.93 pt; `\normalsize` = 31.1 pt is already compliant. Flooring `\small` also fixes all figure captions, which use the caption font `size=\small`.)

### Measured page anchors (from the rendered PDF)

- Title banner gold underline bottom: **17.4 cm** from top.
- Footer gold strip top: **5.6 cm** from bottom.
- ⇒ Available body region = 91.44 − 17.4 − 5.6 = **68.44 cm**.

### Derived layout (all in `\dimexpr`, driven by `\postermargin` = M)

```
bodyheight    = 68.44cm - 2*M                       = 65.44 cm  (was 58.7)
rblockgap     = M                                   = 1.50 cm
rblockheight  = (bodyheight - rblockgap)/2          = 31.97 cm
colwidth      = (paperwidth - 4*M)/3                = 38.64 cm  (was 37.8/37.8/41.45)
body top gap  = 1.12cm + M                          = 2.62 cm   (was 2.75 hardcoded)
inner minipage height = blockheight - 3.3cm - P     (was blockheight - 3.4cm)
```

The `1.12 cm` base in the top-gap is empirical: the current `\vspace{2.75cm}` yields a measured 1.63 cm top margin, and the gap tracks the spacer 1:1, so `vspace = 2.75 − 1.63 + M`. Verified: M=1.5 → measured top margin 1.53 cm.

## Changes by file

### `config/_preamble.tex`
- Add layout knobs `\postermargin` (M) and `\blockinnerpad` (P); add `\colwidth` length.
- Replace the hardcoded `\bodyheight 58.7cm` / `\rblockgap 1cm` with the derived `\dimexpr` forms above.
- Set `\blockpadding` = `\blockinnerpad` (left/right inset = P).
- `block begin` template: change the post-ribbon `\vspace{0.10cm}` → `\vspace{\blockinnerpad}` (internal **top** padding).
- `rblock`/`heroblock` inner minipage height: `…-3.4cm` → `…-3.3cm-\blockinnerpad` (compensates for the larger top padding; reduces to the proven value when P=0.10).
- Append the 28 pt font floor (4 `\renewcommand`s).

### `poster.tex`
- Body top spacer `\vspace{2.75cm}` → `\vspace{\dimexpr 1.12cm + \postermargin\relax}` (top margin = M).
- Body grid: set `\colwidth = (\paperwidth-4\postermargin)/3`; wrap the three column minipages in `\centerline{…}`; widths `0.31/0.31/0.34\paperwidth` → `\colwidth`; inter-column `\hspace*{0.01\paperwidth}` → `\hspace{\postermargin}`.
  - **Why `\centerline`:** the beamerposter text block is centered in the page, so centering a body of width `paperwidth−2M` yields exactly M on each side — no hardcoded left-offset constant needed. (Verified: left = right = 1.52 cm at M=1.5.)

## Safety rationale (why this avoids the documented prior failure)

The 2026-05-30 debug notes proved: **OLD preamble + 48″×36″ renders the hero block fully**; every *failing* configuration involved a **wholesale new preamble** (renamed camelCase lengths, new `block`/`hero` env definitions, KNOBS+DERIVED blocks). The overfull-`\vbox` truncation was never tied to a length *value* — it was something structural in the rewrite's interaction with `mdframed`+`beamerposter` that was never isolated.

This design therefore **keeps the OLD preamble's environment/template structure byte-for-byte** and only (a) changes length **values**, and (b) makes two minimal padding edits. It stays entirely on the proven-working side of that ledger.

## Verification (already performed in `/tmp/postervar`, to be repeated on the real source)

Built at M ∈ {1.0, 1.5, 2.0}, P = 0.8, font floor on:
- **0 overfull-`\vbox` warnings** in all three (the failure signature was 1300–1600 pt overfull).
- Hero block renders **fully** (Key findings + Future work + all 3 figures, breathing room above the gold border).
- Measured geometry at M=1.5: left/right/gap12/gap23/top all = 1.52–1.53 cm; three columns all 38.61 cm; bottom margin = M by construction.
- Font probe confirms `\footnotesize`/`\small`/captions now ≥ 28 pt.

**Acceptance check on the real build:** `grep -c 'Overfull \vbox'` = 0; re-measure margins = 1.5 cm; hero close-up shows the money-plot figure intact.

## Out of scope (flagged, deferred unless requested)

Guideline "Use/Avoid" items the poster doesn't yet follow, intentionally **not** changed here:
1. Sans-serif body font (poster uses `\usefonttheme{serif}`).
2. Off-white/pastel background (currently pure white).
3. Avoid red+green / colorblind-safe palette (green-heavy theme; figures may use red/green).

## Notes

- Not a git repository — design doc saved but not committed.
- Internal **bottom** padding remains the block's existing ≈0.7 cm (block-end spacing); top/left/right = P = 0.8 cm. Effectively uniform; can be made exactly P as a trivial follow-up.
