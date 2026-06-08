# Layout Overhaul — Debugging Notes

**Date:** 2026-05-30 (session ran on top of 2026-05-29 spec and plan)
**Status:** Investigation incomplete; root cause not isolated. Page-resize portion of the overhaul landed; parameterization portion reverted.

**Related docs:**
- Design spec: `docs/superpowers/specs/2026-05-29-poster-layout-overhaul-design.md`
- Implementation plan: `docs/superpowers/plans/2026-05-29-poster-layout-overhaul.md`
- CLAUDE.md → "Deferred work: parameterized layout overhaul" section (high-level pointer)

## Symptom

After replacing `config/_preamble.tex` with the new parameterized version (KNOBS block + DERIVED LENGTHS block + new `rblock`/`heroblock` environments), block 5 (the hero block on the right side) silently truncates. Only the "★ Conclusions, Findings, and Future Work" title bar plus the first 2 bullets of "Key findings:" render. The remaining "Key findings" bullet, all of "Future work" with its 3 bullets, and all 3 figures (binning distributions, FND panels, money plot) are missing from the rendered PDF.

The build reports:

```
Overfull \vbox (1617.53516pt too high) detected at line <end-of-frame>
```

(Magnitude varies 1343–1617 pt depending on knob values used; always present with the new preamble at 48″ × 36″.)

`pdfinfo` confirms the page dimensions are the correct 3456 × 2592 pt (48″ × 36″). The build exits cleanly with code 0. No errors; only the overfull `\vbox` warning.

## Cross-checks that pass (the baseline works)

These configurations were verified to render block 5 fully with no overfull `\vbox`:

| Configuration | Result |
|---|---|
| OLD preamble + OLD `poster.tex` body (3-column 2+2+1) + A0 page size | ✅ baseline; all content visible |
| OLD preamble + OLD `poster.tex` body (3-column 2+2+1) + 48″ × 36″ page size | ✅ all content visible, no overfull |
| OLD preamble + OLD `poster.tex` body + NEW custom-size `beamerposter` call | ✅ identical to above |

**Conclusion from cross-checks:** the 48″ × 36″ page size itself is not the problem. The OLD layout primitives handle it cleanly (with unused vertical whitespace at the bottom because `\bodyheight` is hardcoded at 58.7 cm).

## Cross-checks that fail (variations of the new layout)

These all reproduce the truncation + overfull:

| Configuration | Result |
|---|---|
| NEW preamble (knobs + derived + new envs, `\AtBeginDocument` deferred) + NEW poster.tex 2×2 grid panel + hero panel side-by-side | ❌ truncation, overfull 1617 pt |
| NEW preamble + NEW poster.tex with 3-sibling layout (col1, col2, hero stacked-rblocks pattern matching OLD) | ❌ truncation, overfull 1617 pt |
| NEW preamble with derived lengths hardcoded inline (no `\AtBeginDocument`) + same body | ❌ truncation, overfull 1617 pt |
| NEW preamble + NEW poster.tex body with inner-minipage forced-height *removed* on the heroblock | ❌ truncation persists; overfull 1525 pt |
| NEW preamble + NEW poster.tex with outer hero panel minipage *also* unconstrained (content-sized) | ❌ truncation persists; overfull 1525 pt |
| NEW preamble + NEW poster.tex but bypassing `heroblock` entirely (raw `\fbox{minipage{block5}}` in outer panel) | ❌ truncation persists; shows 1 more bullet than with heroblock, then cuts |
| NEW preamble + NEW envs but heroblock inner-minipage uses the OLD `\dimexpr\bodyHeight-3.4cm\relax` formula | ❌ truncation persists |
| NEW preamble with `\bodyHeight=58.7 cm` (matching OLD value) instead of the derived 63.51 cm | ❌ different rendering (hero wraps below grid panel), more bullets visible, but still overfull 1343 pt and figures still missing |

## Concrete measurements

All values gathered via `\typeout` and `\sbox{...}` instrumentation inside `poster.tex`.

**Lengths at hero-panel-open time (NEW preamble, derived):**
- `\bodyHeight` = 1806.99 pt = **63.5 cm** ✓
- `\gridCellHeight` = 889.27 pt = **31.3 cm** ✓
- `\heroPanelWidth` = 1285.78 pt = **45.3 cm** ✓
- `\paperheight` = 2601.72 pt = **91.44 cm** ✓
- `\paperwidth` = 121.92 cm ✓
- `\textheight` = 2597.72 pt ≈ paperheight

**Inside the heroblock environment (in the new preamble):**
- `\linewidth` = 1243.64 pt = 43.8 cm
- `\textwidth` = 1243.64 pt = 43.8 cm (correctly scoped to the block)

**Block 5 rendered into a width-matched `\sbox` (in isolation, outside heroblock):**
- height + depth = 1646.11 pt = **57.2 cm total content**
- This fits the 59.6 cm inner-minipage area the heroblock allocates.

**Full hero rendering measured via `\sbox` (heroblock + block 5 + chrome):**
- height + depth = 1714.69 pt = **60.5 cm total**
- Fits the 63.5 cm outer panel.

**Figure sizes from `pdftex.def` log lines (NEW preamble):**
- 3 binning plots: 373.10 × 272.61 pt = 13.1 × 9.6 cm each
- 3 FND panels: ~155–162 × 121 pt = ~5.5 × 4.3 cm each
- 1 money plot: 621.82 × 473.98 pt = 21.9 × 16.7 cm

Sum-of-content estimate for block 5: ~50 cm vertical extent (matches the `\sbox` measurement reasonably).

**Inferred frame content total at end of frame:**
- Banner content minipage = 494 pt
- vspace banner→body = 60 pt
- Body line (forced grid panel @ 1807 pt) = 1807 pt
- Footer TikZ overlay = 0 pt (no vertical advance)
- **Total: 2361 pt < 2597 pt textheight** — should fit with ~8 cm to spare. No overfull expected from this arithmetic. The actual 1617 pt overfull is unexplained by the sums.

## Hypotheses ruled out

1. **Page size is too small / hero panel doesn't have enough vertical room.** ❌ Block 5 content is 57 cm; inner minipage is 59.6 cm. Fits with margin. Also: OLD layout at the same 48″ × 36″ page size renders block 5 fully.

2. **`\AtBeginDocument` timing — derived lengths computed before `beamerposter` finalizes `\paperheight`.** ❌ Initially seemed plausible; explicit instrumentation shows `\bodyHeight`, `\paperheight` are at expected values inside the frame. Hardcoding the lengths inline (no deferral) gives identical truncation.

3. **Hero panel is sized to `\gridCellHeight` instead of `\bodyHeight` because of a length-shadowing issue.** ❌ `\typeout` right at hero-panel-open time confirms `\bodyHeight` = 1807 pt and `\gridCellHeight` = 889 pt are both correct. The minipage is created with `[t][\bodyHeight][t]` and `\bodyHeight` is correct at that exact moment.

4. **Block 5 content overflows the inner minipage (figures bigger than expected).** ❌ `\sbox` measurement at the heroblock's actual inner width shows block 5 totals 57 cm — under the 59.6 cm available.

5. **The `\dimexpr\bodyHeight - \ribbonHeight - 2\blockPadding - 2\heroBorder\relax` decomposed formula is computing something different than the OLD `\dimexpr\bodyheight - 3.4cm\relax`.** ❌ Both formulas were tested with the new preamble; both produced the same truncation.

6. **Nested horizontal-mode minipages (2×2 grid cells inside a forced-height grid panel) confuse the side-by-side hero panel's line-height calculation.** ❌ Restructuring the body to 3 sibling-column minipages (matching the OLD pattern exactly, no nested cells) still truncates.

7. **The `heroblock` environment itself has a bug.** ❌ Bypassing heroblock entirely (raw `\fbox{minipage}` with block 5 inside) still truncates with the new preamble.

## What the evidence points at (without isolating it)

The bug is somewhere in the **new `config/_preamble.tex`'s interaction with `mdframed`, `beamerposter`, and/or the body-line vbox sizing**. Specifically:

- The OLD preamble at 48″ × 36″ works. The NEW preamble at 48″ × 36″ doesn't. Same `poster.tex` body structure in both cases (when tested with the 3-sibling layout).
- The difference between OLD and NEW preambles that *isn't* knob/length-value related:
  - NEW preamble adds the KNOBS block (only macro/length definitions — should have no side effects).
  - NEW preamble adds the DERIVED LENGTHS block — either inline or in `\AtBeginDocument`.
  - NEW preamble redefines block environments with camelCase names referencing the new constants.
  - NEW preamble removes `\placeholder` and `\highlight` macros (unused; shouldn't matter).
  - NEW preamble's block envs use `\dimexpr` formulas with named lengths rather than the OLD `\dimexpr...-3.4cm` literal.
- Even setting `\bodyHeight = 58.7 cm` (matching OLD's value exactly) in NEW preamble produces truncation, ruling out the value of `\bodyHeight` as the trigger.

A residue worth investigating: when `\bodyHeight` was set to 58.7 cm in the NEW preamble, the rendered layout *changed structure* — the hero panel wrapped below the grid panel instead of sitting beside it. This suggests the new preamble's body line is being computed with widths summing to slightly over `\paperwidth - 2\outerMargin`, causing horizontal wrap behavior to vary with content. Sum check:

```
outerMargin (1.0) + gridCellWidth (36.37) + gridGutter (1.0)
  + gridCellWidth (36.37) + gridHeroGap (1.0) + heroPanelWidth (45.19)
  + outerMargin (1.0)
= 121.93 cm vs \paperwidth = 121.92 cm  (over by 0.01 cm, rounding)
```

The 0.01 cm rounding discrepancy comes from hardcoded display-rounded values; with the derived `\setlength` computation it should be exact. But this is a place where additional careful arithmetic auditing would be productive.

## Suggested next investigation paths (for whoever picks this up)

In rough order of cheapness:

1. **Width arithmetic audit.** Use `\typeout{\the\dimexpr ...}` immediately before the body line opens to verify the side-by-side minipage widths sum to *exactly* `\paperwidth - 2\outerMargin`, not 0.01 cm over. If they're over, even by a fraction, beamer might be forcing a paragraph wrap that explains the body line height anomaly.

2. **`\showthe \pagegoal` / `\showthe \pagetotal` instrumentation.** Use `\showthe` (not `\typeout`) at multiple points in the frame to dump beamer's view of the page's vbox target and current accumulated height. The implementer's earlier note about `\pagegoal = 16383.99998 pt` (the dimen max) at one debug point suggests beamer's page-sizing state may be unconventional inside the frame; this needs verification at each instrumentation point.

3. **mdframed verbose mode.** Pass `mdframed`'s `\mdfdefinestyle` or per-instance debug options that emit the computed frame box dimensions to the log. Compare what mdframed thinks the heroblock frame size is to what the surrounding minipage thinks.

4. **Bisection of the new preamble.** Start from the OLD preamble (proven to work) and progressively add NEW preamble blocks one at a time (KNOBS → DERIVED LENGTHS → new block envs → camelCase renames) until the truncation appears. The first addition that breaks it is the culprit.

5. **`tcolorbox` swap (was Approach B in the brainstorm).** Replace `mdframed` with `tcolorbox` for the hero block specifically. If the truncation goes away, the bug is mdframed-specific. The brainstorm rejected Approach B for risk reasons; if mdframed turns out to be the root cause, Approach B becomes the right answer.

## What changed in this session (concrete delta from baseline)

The session preserved the baseline source structure. Final delta versus the pre-session repository state:

- `poster.tex` line 54 (`beamerposter` call): A0 size → custom `width=121.92,height=91.44` for 48″ × 36″. A0 retained as commented-out alternative on the next line. Header comment updated to reflect the new target dimensions.
- `content/footer.tex` line 31: `\includegraphics{nu2026_poster/content/ArXiV_QR_code.png}` → `\includegraphics{content/ArXiV_QR_code.png}` (fixes the QR path for in-place builds; was applied in the earlier session and is preserved).
- `CLAUDE.md`: project description updated to 48″ × 36″ with A0 fallback note; new "Deferred work: parameterized layout overhaul" section added at the end pointing at the design spec, plan, and this debug-notes document.
- `docs/superpowers/specs/2026-05-29-poster-layout-overhaul-design.md`: written; preserved as-is for future reference.
- `docs/superpowers/plans/2026-05-29-poster-layout-overhaul.md`: written; preserved as-is for future reference.
- `docs/superpowers/specs/2026-05-30-layout-overhaul-debug-notes.md`: this file.

Nothing else in the repository changed.
