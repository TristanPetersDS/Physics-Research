# Poster Layout Overhaul — Design

**Date:** 2026-05-29
**Status:** Draft for review
**Target:** Neutrino 2026 poster (UC Irvine, 22–26 June 2026)

## 1 · Background and problem

The current `poster.tex` / `config/_preamble.tex` build produces a working A0 landscape poster but the layout system has accumulated brittleness:

- Page size is hardcoded to A0 in the `beamerposter` package call.
- TikZ banner/footer overlays use absolute `yshift` coordinates (`16.8 cm`, `17.4 cm`, `5 cm`, `5.6 cm`) — these break if any geometry changes.
- Inner-minipage heights inside `rblock` and `heroblock` subtract a magic `3.4 cm` to clear the ribbon title; if `\ribbonheight` or `\blockpadding` change, content silently overflows the border with no warning.
- `content/block5.tex` hardcodes `height=1.675in` on the three FND figure panels — this absolutely breaks on any page-size change.
- Figure widths across blocks are inconsistent (`0.79`, `0.4`, `0.39`, `0.48`, `0.3`, `0.5`, plus the `1.675in` outlier), with no shared vocabulary.
- `content/footer.tex` uses `\hspace*{-5.5cm}` and `\vspace{2.85cm}` to slot the QR code into a 4-minipage chain whose widths sum to >1.0.
- `content/block2.tex` calls `\cite{Duvall:2024cae}` but no `\bibliography{}` is wired, so the citation renders as `[?]`.

The conference logistics now require resizing the poster from A0 (≈46.81″ × 33.11″) to **48″ × 36″** (4 ft × 3 ft). This is a small dimensional change, but doing it on top of the brittle layout would compound the problem. The overhaul accomplishes both: change the page size and replace the layout primitives with a parameterized system that scales cleanly.

## 2 · Decisions summary

The brainstorm settled the following:

| # | Decision | Choice |
|---|---|---|
| 1 | Page size | **48″ × 36″** (= 121.92 × 91.44 cm), set via `beamerposter` `size=custom,width=,height=`. A0 fallback retained as a commented one-line swap. |
| 2 | Scaling model | **Hybrid.** Major regions (banner height, footer height, body height, panel widths) are paper-relative fractions and reflow on page resize. Fine details (block padding, mdframe border, ribbon height) are absolute and stay put. |
| 3 | Content-area subdivision | **Grid panel + hero panel.** Body is a horizontal split: a 2×2 grid of the four supporting blocks on the left, plus a single full-height hero block on the right. Replaces today's three-column 2+2+1 layout. |
| 4 | Gap-knob granularity | **Six named gaps.** One knob per distinct visual boundary: outer margin, banner-body gap, body-footer gap, grid gutter, grid-hero gap, block padding. |
| 5 | Type-size control | **Named role macros.** ~7 roles: `\bannerTitleSize`, `\bannerSubtitleSize`, `\bannerAuthorSize`, `\blockTitleSize`, `\bodySize`, `\captionSize`, `\smallPrintSize`. Block files use these instead of inline `\Large` / `\small`. |
| 6 | Figure-width control | **Named slots + raw-fraction escape.** Four slot macros: `\figFull` (0.95), `\figLarge` (0.75), `\figHalf` (0.48), `\figThird` (0.31). Block files use slots by default; raw `\linewidth` fractions allowed for one-offs; hardcoded inches (e.g. `1.675in`) banned. |
| 7 | Scope | **Full refactor including footer and figure cleanup.** Rewrite `poster.tex` and `config/_preamble.tex`, swap font/figure macros across all `content/block*.tex`, rebuild `content/footer.tex` from scratch. |
| 8 | Config file organization | **Single file.** All knobs and engine definitions stay in `config/_preamble.tex`; knobs in a clearly-marked block at the top, engine below. |

## 3 · Architecture

Three primary stacked regions on the page, with the content region itself subdivided into a 2×2 grid panel and a hero panel:

```
┌─────────────────────────────────────────────┐  ← page edge
│           title banner  (\bannerHeight)      │
│════════════════════════════════════════════│  ← gold underline  (\goldStripWidth)
│  ↕ \bannerBodyGap                            │
│ ┌──[\outerMargin]──┐                        │
│ │  ┌────────┐ ┌────────┐  ┌──────────────┐ │
│ │  │ blk 1  │ │ blk 3  │  │              │ │
│ │  ├────────┤ ├────────┤  │   hero blk 5 │ │
│ │  │ blk 2  │ │ blk 4  │  │              │ │
│ │  └────────┘ └────────┘  └──────────────┘ │
│ └──────────────────┘                        │
│  ↕ \bodyFooterGap                            │
│════════════════════════════════════════════│  ← gold underline
│           footer banner  (\footerHeight)     │
└─────────────────────────────────────────────┘
```

Within the content region:

- **Grid panel** occupies `\gridHeroSplit` (= 0.62) of the body-available width; contains blocks 1–4 in a 2×2 matrix with uniform `\gridGutter` between cells.
- **Hero panel** occupies the remaining body-available width; contains block 5 as a single full-height frame with the distinguishing gold border + gold-bar ribbon.

Block numbering preserved from the current poster (1 = top-left, 2 = bottom-left, 3 = top-right, 4 = bottom-right, 5 = hero).

**Knob/engine separation within the single config file.** `config/_preamble.tex` is organized in two clearly-marked sections:

1. **KNOBS block** at the top: all user-tunable parameters (page-relative ratios, gap lengths, type-role size macros, figure-width slots, frame styling, color palette). This is the section a user opens when they want to tune the poster.
2. **ENGINE block** below: derived-length computations, block environment definitions, beamer font and template configuration, package loads and patches. Rarely touched.

## 4 · Token system

The full knob block, with starting values chosen to approximately match the current visual proportions at the new 48″ × 36″ page:

```latex
% =====================================================================
%  KNOBS — edit these to tune the poster
% =====================================================================

% --- region heights as paper-relative ratios ---
\newcommand{\bannerHeightFrac}{0.19}    % banner = 19% of \paperheight
\newcommand{\footerHeightFrac}{0.075}   % footer = 7.5% of \paperheight

% --- six gap knobs (absolute) ---
\newlength{\outerMargin}      \setlength{\outerMargin}{1.0cm}
\newlength{\bannerBodyGap}    \setlength{\bannerBodyGap}{1.5cm}
\newlength{\bodyFooterGap}    \setlength{\bodyFooterGap}{1.0cm}
\newlength{\gridGutter}       \setlength{\gridGutter}{1.0cm}
\newlength{\gridHeroGap}      \setlength{\gridHeroGap}{1.0cm}
\newlength{\blockPadding}     \setlength{\blockPadding}{0.6cm}

% --- body split ---
\newcommand{\gridHeroSplit}{0.62}      % grid panel fraction of body-available width

% --- frame styling (absolute) ---
\newlength{\rblockBorder}    \setlength{\rblockBorder}{4pt}
\newlength{\heroBorder}      \setlength{\heroBorder}{4pt}
\newlength{\goldStripWidth}  \setlength{\goldStripWidth}{0.6cm}
\newlength{\ribbonHeight}    \setlength{\ribbonHeight}{2.5cm}
\newlength{\bannerInnerPad}  \setlength{\bannerInnerPad}{0.5cm}

% --- type roles (size only; weight/shape applied at use site) ---
\newcommand{\bannerTitleSize}{\veryHuge}
\newcommand{\bannerSubtitleSize}{\LARGE}
\newcommand{\bannerAuthorSize}{\normalsize}
\newcommand{\blockTitleSize}{\Large}
\newcommand{\bodySize}{\normalsize}
\newcommand{\captionSize}{\small}
\newcommand{\smallPrintSize}{\footnotesize}

% --- figure width slots (fractions of containing-block \linewidth) ---
\newcommand{\figFull}{0.95\linewidth}
\newcommand{\figLarge}{0.75\linewidth}
\newcommand{\figHalf}{0.48\linewidth}
\newcommand{\figThird}{0.31\linewidth}

% --- palette (unchanged from current) ---
\definecolor{UHGreen}{HTML}{024731}
\definecolor{UHGold}{HTML}{C8A464}
\definecolor{LLNLNavy}{HTML}{003594}
\definecolor{BlockBG}{HTML}{FFFFFF}
\definecolor{SoftGrey}{HTML}{ECECEC}
```

Starting-value rationale for the four paper-relative ratios and the outer margin:

- `\bannerHeightFrac = 0.19` produces ~17.4 cm at 48″×36″ (vs. current 16.8 cm) — a small bump to keep visual balance against the wider 4 ft page.
- `\footerHeightFrac = 0.075` produces ~6.9 cm at 48″×36″ (vs. current 5 cm) — bumped specifically to fit refs + acks + QR cleanly without the negative-hspace hack.
- `\outerMargin = 1 cm` makes the side margins explicit (today's are ~1 cm by accident from `0.99\paperwidth` columns).
- `\gridHeroSplit = 0.62` matches today's effective grid-to-hero ratio (~64:34 after gap accounting).

## 5 · Derived lengths

Computed below the knob block in `_preamble.tex`. All consumers of geometry pull from these, not from the raw knobs:

```latex
% =====================================================================
%  DERIVED LENGTHS — computed from knobs; don't edit directly
% =====================================================================
\newlength{\bannerHeight}
\setlength{\bannerHeight}{\bannerHeightFrac\paperheight}

\newlength{\footerHeight}
\setlength{\footerHeight}{\footerHeightFrac\paperheight}

\newlength{\bodyHeight}
\setlength{\bodyHeight}{\dimexpr
  \paperheight - \bannerHeight - \footerHeight - 2\goldStripWidth
  - \bannerBodyGap - \bodyFooterGap\relax}

\newlength{\bodyWidth}
\setlength{\bodyWidth}{\dimexpr\paperwidth - 2\outerMargin\relax}

\newlength{\gridHeroAvail}
\setlength{\gridHeroAvail}{\dimexpr\bodyWidth - \gridHeroGap\relax}

\newlength{\gridPanelWidth}
\setlength{\gridPanelWidth}{\gridHeroSplit\gridHeroAvail}

\newlength{\heroPanelWidth}
\setlength{\heroPanelWidth}{\dimexpr\gridHeroAvail - \gridPanelWidth\relax}

\newlength{\gridAvailW}
\setlength{\gridAvailW}{\dimexpr\gridPanelWidth - \gridGutter\relax}
\newlength{\gridCellWidth}
\setlength{\gridCellWidth}{0.5\gridAvailW}

\newlength{\gridAvailH}
\setlength{\gridAvailH}{\dimexpr\bodyHeight - \gridGutter\relax}
\newlength{\gridCellHeight}
\setlength{\gridCellHeight}{0.5\gridAvailH}
```

Resulting concrete values at the two supported page sizes:

| Length | At 48″ × 36″ (121.92 × 91.44 cm) | At A0 landscape (118.9 × 84.1 cm) |
|---|---|---|
| `\bannerHeight`     | 17.37 cm | 15.98 cm |
| `\footerHeight`     |  6.86 cm |  6.31 cm |
| `\bodyHeight`       | ~63.5 cm | ~58.1 cm |
| `\bodyWidth`        | 119.92 cm | 116.9 cm |
| `\gridPanelWidth`   | ~73.7 cm | ~71.9 cm |
| `\heroPanelWidth`   | ~45.2 cm | ~44.0 cm |
| `\gridCellWidth`    | ~36.4 cm | ~35.5 cm |
| `\gridCellHeight`   | ~31.3 cm | ~28.5 cm |

## 6 · Layout primitives

### 6.1 Banner template

TikZ overlay anchored to `current page.north`, with all coordinates derived from `\bannerHeight` and `\goldStripWidth`:

```latex
\begin{tikzpicture}[remember picture,overlay]
  \fill[UHGreen] (current page.north west)
                 rectangle ([yshift=-\bannerHeight]current page.north east);
  \fill[UHGold]  ([yshift=-\bannerHeight]current page.north west)
                 rectangle ([yshift=-\dimexpr\bannerHeight+\goldStripWidth\relax]
                            current page.north east);
\end{tikzpicture}
```

Banner content is a `columns` env with three columns (left logo wing, center title block, right logo wing) sized to fit within `\bannerHeight - \goldStripWidth - 2\bannerInnerPad`. Logos remain content-driven via `\titlelogo{w}{h}{path}`; the banner is sized to accommodate them, not vice versa.

### 6.2 Footer template

Mirror of the banner, anchored to `current page.south`:

```latex
\begin{tikzpicture}[remember picture,overlay]
  \fill[UHGold]  ([yshift=\dimexpr\footerHeight\relax]current page.south west)
                 rectangle ([yshift=\dimexpr\footerHeight+\goldStripWidth\relax]
                            current page.south east);
  \fill[UHGreen] (current page.south west)
                 rectangle ([yshift=\footerHeight]current page.south east);
  \node[anchor=center, text=white] at
       ([yshift=\dimexpr 0.5\footerHeight\relax]current page.south) {
    \begin{minipage}{\dimexpr\paperwidth-2\outerMargin\relax}
      \input{content/footer}
    \end{minipage}
  };
\end{tikzpicture}
```

### 6.3 Body grid

Two-level nested-minipage structure in `poster.tex` (after the banner overlay and a `\vspace*` clearing the banner):

```latex
\noindent\hspace*{\outerMargin}%
\begin{minipage}[t][\bodyHeight][t]{\gridPanelWidth}
  % --- row 1: blocks 1 and 3 ---
  \begin{minipage}[t][\gridCellHeight][t]{\gridCellWidth}
    \begin{rblock}{Localization of IBD Source}\input{content/block1}\end{rblock}
  \end{minipage}\hspace{\gridGutter}%
  \begin{minipage}[t][\gridCellHeight][t]{\gridCellWidth}
    \begin{rblock}{Our Approach to Simulation Design}\input{content/block3}\end{rblock}
  \end{minipage}

  \vspace{\gridGutter}

  % --- row 2: blocks 2 and 4 ---
  \begin{minipage}[t][\gridCellHeight][t]{\gridCellWidth}
    \begin{rblock}{Traditional Approach}\input{content/block2}\end{rblock}
  \end{minipage}\hspace{\gridGutter}%
  \begin{minipage}[t][\gridCellHeight][t]{\gridCellWidth}
    \begin{rblock}{Novel Algorithm for Segmented Detectors}\input{content/block4}\end{rblock}
  \end{minipage}
\end{minipage}%
\hspace{\gridHeroGap}%
\begin{minipage}[t][\bodyHeight][t]{\heroPanelWidth}
  \begin{heroblock}{$\bigstar$\,Conclusions, Findings, and Future Work}
    \input{content/block5}\vfill
  \end{heroblock}
\end{minipage}
```

### 6.4 Block environments

`rblock` and `heroblock` no longer subtract a magic constant for inner-minipage height. They derive it from named lengths via `\dimexpr`:

```latex
\newenvironment{rblock}[1]{%
  \begin{mdframed}[linecolor=UHGreen, linewidth=\rblockBorder,
                   backgroundcolor=BlockBG,
                   innerleftmargin=0pt, innerrightmargin=0pt,
                   innertopmargin=0pt, innerbottommargin=0pt,
                   skipabove=0pt, skipbelow=0pt,
                   userdefinedwidth=\linewidth]%
    \begin{block}{#1}%
      \begin{minipage}[t]%
        [\dimexpr\gridCellHeight - \ribbonHeight - 2\blockPadding
                 - 2\rblockBorder\relax][t]%
        {\dimexpr\linewidth - 2\blockPadding\relax}%
}{%
      \end{minipage}%
    \end{block}%
  \end{mdframed}%
}

\newenvironment{heroblock}[1]{%
  \setbeamercolor{block title}{fg=UHGreen, bg=UHGold}%
  \setbeamercolor{block body}{fg=black, bg=BlockBG}%
  \begin{mdframed}[linecolor=UHGold, linewidth=\heroBorder,
                   backgroundcolor=BlockBG,
                   innerleftmargin=0pt, innerrightmargin=0pt,
                   innertopmargin=0pt, innerbottommargin=0pt,
                   skipabove=0pt, skipbelow=0pt,
                   userdefinedwidth=\linewidth]%
    \begin{block}{#1}%
      \begin{minipage}[t]%
        [\dimexpr\bodyHeight - \ribbonHeight - 2\blockPadding
                 - 2\heroBorder\relax][t]%
        {\dimexpr\linewidth - 2\blockPadding\relax}%
}{%
      \end{minipage}%
    \end{block}%
  \end{mdframed}%
}
```

If `\ribbonHeight`, `\blockPadding`, or `\rblockBorder` are tuned, the inner area adjusts automatically — no stale constant to chase.

### 6.5 Captions, block titles, body type

Beamer font configuration is bound to the named roles:

```latex
\setbeamerfont{block title}{size=\blockTitleSize, series=\bfseries}
\setbeamerfont{block body}{size=\bodySize}
\setbeamerfont{caption}{size=\captionSize}
```

Where each role is a `\newcommand` expanding to a single LaTeX size command (e.g., `\newcommand{\captionSize}{\small}`). Editing `\captionSize` in the knobs block globally retags every beamer-managed figure caption.

**Scope of "universal" scaling.** Beamer's `\setbeamerfont{caption}` covers only the *caption text* under each `\begin{figure}`. Text rendered *inside* a figure — overpic `\put` annotations, TikZ node labels (`font=\small`), picture-primitive text — is unaffected by the beamer hook. To get true universal control, those inline font-size commands must also use the role macros. The migration in §7 includes this conversion.

## 7 · Block-file migration

| File | Changes |
|---|---|
| `content/title.tex` | Three size-command swaps: `\veryHuge\bfseries` → `\bannerTitleSize\bfseries`; `\Large\itshape` → `\bannerSubtitleSize\itshape`; `\normalsize` (author block) → `\bannerAuthorSize`. |
| `content/block1.tex` | `0.79\linewidth` → `\figLarge`. |
| `content/block2.tex` | `0.4\linewidth` → `\figHalf`. `\cite{Duvall:2024cae}` (renders as `[?]`) → hand-typed `[2]` matching the footer reference numbering. |
| `content/block3.tex` | Overpic `width=0.39\linewidth` → `width=\figHalf`. The percent-based `\put(x,y)` annotation coords inside overpic are width-invariant — no recalibration needed. The leading `\footnotesize` inside the overpic body → `\smallPrintSize` so it tracks the universal small-print knob. |
| `content/block4.tex` | Both side-by-side minipages `0.48\linewidth` → `\figHalf`. Picture-primitive `\setlength{\unitlength}{.04\linewidth}` is `\linewidth`-relative; no recalibration needed. The two `\footnotesize` declarations inside the `picture` envs → `\smallPrintSize`. |
| `content/block5.tex` | Three `0.3\linewidth` → `\figThird`; `0.5\linewidth` money plot → `\figLarge`. **Remove all three `height=1.675in` hardcodes**, switch FND panels to width-based sizing (`width=\figThird`). Recalibrate the three θ-label TikZ coordinates `(1.85, 2.225)`, `(-0.25, 2.23)`, `(0.25, 2.23)` etc. via build-eyeball-nudge iteration (expect 2–3 cycles). The TikZ node options `font=\small` for the θ labels → `font=\captionSize`. |
| `content/footer.tex` | Complete rebuild as three clean minipages (refs ≈ 50% / acks ≈ 36% / QR ≈ 10%) summing to ≈ 0.96\linewidth with `\hfill` distributing the remainder. No negative `\hspace`, no `\vspace` to slide the QR. QR path stays `content/ArXiV_QR_code.png` (in-place build). LLNL release number remains `LLNL-POST-XXXXXX` placeholder. |

The rebuilt footer (preserving the current visual hierarchy: refs at the larger `\captionSize`, acks at the smaller `\smallPrintSize`):

```latex
\noindent
\begin{minipage}[t]{0.50\linewidth}
  \captionSize
  \textbf{References}\par
  [1] Crow \emph{et al.}, in prep.\,(2026)\par
  [2] Duvall \emph{et al.}, Phys.\ Rev.\ Applied \textbf{22}, 054030 (2024)\par
\end{minipage}%
\hfill
\begin{minipage}[t]{0.36\linewidth}
  \smallPrintSize
  \textbf{Acknowledgments}\par
  This work was funded in-part by the Consortium for Monitoring,
  Technology, and Verification under DOE NNSA award DE-NA0003920.
  Prepared by LLNL under Contract DE-AC52-07NA27344. LLNL-POST-XXXXXX.
\end{minipage}%
\hfill
\begin{minipage}[t]{0.10\linewidth}
  \centering
  \smallPrintSize
  \textbf{Ref. [1]:}\\[0.3em]
  \includegraphics[width=0.9\linewidth]{content/ArXiV_QR_code.png}
\end{minipage}
```

**Macros being retired:** `\bodyheight`, `\rblockgap`, `\rblockheight` (replaced by `\bodyHeight`, `\gridGutter`, `\gridCellHeight`), `\placeholder` (unused), `\highlight` (unused).

**Macros being added:** all the knob macros from §4, plus the four `\fig*` slot macros, plus the new derived-length registers from §5.

## 8 · Build, verification, rollout

### 8.1 Build pipeline

Unchanged: `pdflatex` twice (TikZ `[remember picture, overlay]` two-pass requirement preserved), or `latexmk -pdf poster.tex`. Identical package set — no new dependencies. The QR path fix (`nu2026_poster/content/...` → `content/...`) is already applied as part of this session's preparatory work.

### 8.2 Implementation sequence

Each step builds; visible regressions are bounded to that step. **No `git`-based safety net is available — this repository is not under version control** (CLAUDE.md confirms). Backup files substitute.

1. **Snapshot.** Copy `config/_preamble.tex` → `config/_preamble.tex.old` and `poster.tex` → `poster.tex.old`. Keep the May-built `poster.pdf` as the visual regression baseline.
2. **Additive knobs.** Add the new KNOBS block + DERIVED LENGTHS block to the top of `_preamble.tex`. Nothing references them yet. Build passes unchanged.
3. **Block environments.** Replace `rblock` / `heroblock` definitions in `_preamble.tex` to derive inner-minipage heights from `\gridCellHeight` / `\bodyHeight` and the new gap knobs. The body grid in `poster.tex` must be updated in the same commit since rblocks now expect different surrounding context (step 4).
4. **`poster.tex` body grid and banner/footer overlays.** Rewrite the body to the grid-panel/hero-panel nested-minipage structure; rewrite the banner and footer TikZ overlays to derive `yshift` from `\bannerHeight` / `\footerHeight` / `\goldStripWidth`. Also change the `beamerposter` package call to `size=custom,width=121.92,height=91.44,scale=1.25`, with the A0 form as a commented fallback. Build, eyeball — expect rough first cut.
5. **`content/title.tex`.** Three size-command swaps. Visual check: title and authors render at expected sizes.
6. **`content/block1.tex` through `block4.tex`.** Mechanical figure-width and font-macro swaps. block2 gets the `\cite` → `[2]` swap.
7. **`content/block5.tex`.** Figure-width swaps; remove all three `1.675in` height hardcodes; recalibrate the three θ-label TikZ coordinates via build-eyeball-nudge iteration. Expect 2–3 cycles.
8. **`content/footer.tex` full rebuild** to the three-minipage layout from §7.
9. **Verify at 48″ × 36″** using the checklist in §8.3.
10. **Verify A0 fallback.** Swap the `beamerposter` package call to the A0 form. Build. Run the same checklist. Anything that breaks → the corresponding length wasn't paper-derived; fix it. Revert the swap.
11. **CLAUDE.md update** (see §8.4).
12. **Delete `.old` backups** once both verification passes succeed.

### 8.3 Verification checklist

Run after step 9 and again after step 10:

```bash
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Inspect `poster.pdf` visually for:

- No `[?]` or `??` markers (undefined refs / failed citations).
- No missing-glyph squares (■) — uppercase-Greek regression check. Any new uppercase Greek must have the `\renewcommand{\Greek}{\mathnormal{\OldGreek}}` wrapper.
- No "draft" placeholder boxes (missing figure files).
- Block borders intact; gold underlines visible; banner and footer span full page width; QR code renders.
- No content overflow past `mdframed` borders.
- Itemize bullets render (the `\labelitemi` mitigation in `\setlist[itemize]{label=...}` is preserved).

Then:

```bash
grep -iE "warning|overfull" poster.log | grep -viE "underfull|font shape"
```

Review remaining warnings — no new categories vs. the pre-overhaul baseline.

### 8.4 CLAUDE.md updates after implementation

- **"Body layout" section:** rewrite to describe the grid-panel + hero-panel split with `\gridHeroSplit`, plus the six gap knobs.
- **"Visual identity" section:** layout-constants list now points at the named knobs.
- **"Silent-failure footguns" item 5** (hardcoded `3.4 cm` inner-minipage heights): rewrite as "previously a footgun, now eliminated by `\dimexpr` derivation from `\gridCellHeight` and the ribbon/padding/border knobs."
- **"References, acknowledgements, QR code" section:** QR path is now `content/ArXiV_QR_code.png` for in-place builds; the `nu2026_poster/` parent-directory quirk is gone.
- **Add a short new subsection:** "Tuning the layout — where the knobs live" pointing at the `config/_preamble.tex` KNOBS block, listing the six gap knobs, two paper-relative ratios, seven type-role macros, and four figure slots.

## 9 · Footguns: preserved vs. eliminated

| Footgun (per current CLAUDE.md) | Status after overhaul |
|---|---|
| 1. Uppercase Greek font slot (`\Delta` etc. render as ■ under helvet+beamerposter) | **Preserved.** `\renewcommand{\Delta}{\mathnormal{\OldDelta}}` stays; pattern is documented for new uppercase Greek. |
| 2. `\labelitemi` undefined under enumitem | **Preserved.** `\setlist[itemize]{label=...}` mitigation stays. |
| 3. `columns` env `\hspace` gobbling | **Mostly eliminated.** Body grid no longer uses `columns`; banner still does, but its gap structure is column-width-driven (not `\hspace`-driven), so it stays safe. |
| 4. TikZ `[remember picture, overlay]` two-pass requirement | **Preserved.** Still required for banner and footer. |
| 5. Hardcoded `3.4 cm` inner-minipage subtraction in `rblock` / `heroblock` | **Eliminated.** Inner-minipage height now derived via `\dimexpr` from `\gridCellHeight` / `\bodyHeight` and the named ribbon/padding/border knobs. |

A sixth footgun-class that this overhaul addresses (not originally in CLAUDE.md):

- **Hardcoded absolute figure heights** (the `height=1.675in` in `content/block5.tex`). Eliminated: replaced with width-based sizing via `\figThird`, with θ-label TikZ coords recalibrated.

## 10 · Out of scope

To keep the overhaul focused, the following are explicitly **not** part of this work:

- Wiring BibTeX into the build (`refs.bib` remains unused; references stay hand-typed in `content/footer.tex`).
- Changing the colorblind-unfriendly figure palette (separate concern noted in the existing `poster.tex` to-do list).
- Replacing `mdframed` with `tcolorbox` (considered as Approach B during brainstorm; rejected to avoid new dependencies and visual re-tuning).
- A full TikZ-positioned page layout (Approach C; rejected because text inside TikZ nodes lacks LaTeX's natural overflow handling).
- Initializing the project as a git repository.
