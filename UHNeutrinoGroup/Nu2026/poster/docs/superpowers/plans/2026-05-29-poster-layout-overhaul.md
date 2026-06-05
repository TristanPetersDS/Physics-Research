# Poster Layout Overhaul — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resize the Neutrino 2026 poster from A0 to 48″ × 36″ (4 ft × 3 ft) and replace the brittle hardcoded layout system with a parameterized knob-driven system per the design spec at `docs/superpowers/specs/2026-05-29-poster-layout-overhaul-design.md`.

**Architecture:** Three-region page model (title banner / content / footer banner). All major lengths are derived from `\paperwidth` / `\paperheight` and a small set of named "knobs" defined at the top of `config/_preamble.tex`. The content region is split horizontally into a 2×2 grid panel (blocks 1–4) and a full-height hero panel (block 5). Hybrid scaling: major regions reflow on page resize (paper-relative fractions); fine details like padding and border widths stay absolute.

**Tech Stack:** `beamer` + `beamerposter` (custom size) + TikZ + `mdframed` + `helvet` — identical to current. No new dependencies.

**Repository state:** Not under git. Snapshots use `.old` filename suffixes; rollback = `cp` from `.old`. Verification = `pdflatex` exit code 0 + visual inspection of `poster.pdf`.

---

## File structure

Files modified across the plan:

| Path | Role |
|---|---|
| `config/_preamble.tex` | KNOBS block (parameters) and ENGINE block (derived lengths, beamer config, block environments). One file; two clearly-marked sections. |
| `poster.tex` | Page-size declaration, banner TikZ overlay, body grid (grid panel + hero panel), footer TikZ overlay. |
| `content/title.tex` | Three font-size macro swaps. |
| `content/block1.tex` | One figure-width swap. |
| `content/block2.tex` | One figure-width swap, one `\cite` → hand-typed `[2]` swap. |
| `content/block3.tex` | One figure-width swap, one inline-font swap. |
| `content/block4.tex` | Two figure-width swaps, two inline-font swaps. |
| `content/block5.tex` | Multiple figure-width swaps, three `1.675in` height removals, three θ-label TikZ coord recalibrations, one inline-font swap. |
| `content/footer.tex` | Full rebuild as clean three-minipage layout. |
| `CLAUDE.md` | Updates to Body layout, Visual identity, Footguns, References sections; new "Tuning the layout" subsection. |

Files created (transient, removed at end):

| Path | Role |
|---|---|
| `config/_preamble.tex.old` | Backup of pre-overhaul preamble. |
| `poster.tex.old` | Backup of pre-overhaul orchestrator. |
| `poster.baseline.pdf` | Snapshot of pre-overhaul PDF for visual regression diffing. |

---

## Task 1: Snapshot the current state

**Files:**
- Create: `config/_preamble.tex.old`
- Create: `poster.tex.old`
- Create: `poster.baseline.pdf`

- [ ] **Step 1: Backup the preamble.**

```bash
cp config/_preamble.tex config/_preamble.tex.old
```

Expected: silent success, exit 0.

- [ ] **Step 2: Backup the orchestrator.**

```bash
cp poster.tex poster.tex.old
```

Expected: silent success, exit 0.

- [ ] **Step 3: Snapshot the current PDF as baseline.**

```bash
cp poster.pdf poster.baseline.pdf
```

Expected: silent success, exit 0.

- [ ] **Step 4: Confirm all three backups exist with non-zero sizes.**

```bash
ls -la config/_preamble.tex.old poster.tex.old poster.baseline.pdf
```

Expected: three lines, sizes match originals (preamble ~6.5 KB, poster.tex ~5 KB, baseline.pdf ~700+ KB).

---

## Task 2: Rewrite `config/_preamble.tex` and `poster.tex` to the new layout system

This is the load-bearing change. Both files are coupled (the new block environments depend on lengths computed from the new knobs and consumed by the new body grid in `poster.tex`), so they are replaced together. Build verification happens at the end of this task only.

**Files:**
- Modify: `config/_preamble.tex` (full replacement)
- Modify: `poster.tex` (full replacement)

- [ ] **Step 1: Write the new `config/_preamble.tex`.**

Use the Write tool to overwrite `config/_preamble.tex` with the following exact content:

```latex
% =====================================================================
%  config/_preamble.tex — packages, knobs, engine
%  See docs/superpowers/specs/2026-05-29-poster-layout-overhaul-design.md
% =====================================================================

% ---- packages -------------------------------------------------------
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{graphicx}
\usepackage[percent]{overpic}
\usepackage{pict2e}
\usepackage{epsfig}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta,calc,backgrounds,
                shapes.geometric,decorations.pathreplacing,fit}
\usepackage{xcolor}
\usepackage{amsmath,amssymb,bm}

% Uppercase Greek footgun fix (helvet + beamerposter empty font slot).
% If any new uppercase Greek (\Phi, \Sigma, \Omega, etc.) is introduced,
% add a matching \renewcommand line here using \mathnormal.
\let\OldDelta\Delta
\renewcommand{\Delta}{\mathnormal{\OldDelta}}

\usepackage{siunitx}
\usepackage{enumitem}
\usepackage{caption}
\usepackage{microtype}
\usepackage{booktabs}
\usepackage[framemethod=tikz]{mdframed}

% =====================================================================
%  KNOBS — edit these to tune the poster
% =====================================================================

% --- palette ---
\definecolor{UHGreen}{HTML}{024731}
\definecolor{UHGold}{HTML}{C8A464}
\definecolor{LLNLNavy}{HTML}{003594}
\definecolor{BlockBG}{HTML}{FFFFFF}
\definecolor{SoftGrey}{HTML}{ECECEC}

% --- region heights as paper-relative ratios ---
\newcommand{\bannerHeightFrac}{0.19}
\newcommand{\footerHeightFrac}{0.075}

% --- six gap knobs (absolute) ---
\newlength{\outerMargin}      \setlength{\outerMargin}{1.0cm}
\newlength{\bannerBodyGap}    \setlength{\bannerBodyGap}{1.5cm}
\newlength{\bodyFooterGap}    \setlength{\bodyFooterGap}{1.0cm}
\newlength{\gridGutter}       \setlength{\gridGutter}{1.0cm}
\newlength{\gridHeroGap}      \setlength{\gridHeroGap}{1.0cm}
\newlength{\blockPadding}     \setlength{\blockPadding}{0.6cm}

% --- body split (grid panel fraction of body-available width) ---
\newcommand{\gridHeroSplit}{0.62}

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

% =====================================================================
%  DERIVED LENGTHS — computed from knobs; do not edit directly
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

% =====================================================================
%  ENGINE — beamer config, block templates, environments
% =====================================================================

\setbeamercolor{block title}{fg=white,bg=UHGreen}
\setbeamercolor{block body}{fg=black,bg=BlockBG}
\setbeamerfont{block title}{size=\blockTitleSize,series=\bfseries}
\setbeamerfont{block body}{size=\bodySize}
\setbeamertemplate{itemize item}%
  {\color{UHGreen}\raisebox{0.05ex}{\textbf{\textbullet}}}
\setbeamertemplate{itemize subitem}%
  {\color{UHGreen}\raisebox{0.1ex}{\textendash}}
\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{caption}[numbered]{}
\setbeamertemplate{caption label separator}{:~}
\setbeamerfont{caption}{size=\captionSize}

\setbeamertemplate{block begin}{%
  \vspace*{-0.3ex}%
  \begin{beamercolorbox}[wd=\linewidth,sep=0pt,leftskip=0pt,rightskip=0pt,colsep*=0pt]{block title}%
    \begin{minipage}[c][\ribbonHeight][s]{\linewidth}%
      \vspace*{\fill}%
      \hspace{\blockPadding}\usebeamerfont*{block title}\insertblocktitle\par%
      \vspace*{0.28cm}%
    \end{minipage}%
  \end{beamercolorbox}%
  \nointerlineskip%
  \begin{beamercolorbox}[leftskip=\blockPadding,rightskip=\blockPadding,vmode]{block body}%
    \vspace{0.10cm}%
}

\setbeamertemplate{block end}{%
    \vspace{0.30cm}%
  \end{beamercolorbox}%
  \vspace{0.40cm}%
}

% ---- title-banner logo wrapper (unchanged from prior version) ----
\newcommand{\titlelogo}[3]{%
  \begin{tikzpicture}
    \node[fill=BlockBG!50!white,
          minimum width=#1 cm,
          minimum height=#2 cm,
          inner sep=0.4cm,
          rounded corners=3pt] {%
      \includegraphics[width=\dimexpr#1 cm - 0.8cm\relax,
                       height=\dimexpr#2 cm - 0.8cm\relax,
                       keepaspectratio]{#3}%
    };
  \end{tikzpicture}%
}

% ---- block environments ----
\newenvironment{rblock}[1]{%
  \begin{mdframed}[linecolor=UHGreen,linewidth=\rblockBorder,
                   backgroundcolor=BlockBG,
                   innerleftmargin=0pt,innerrightmargin=0pt,
                   innertopmargin=0pt,innerbottommargin=0pt,
                   skipabove=0pt,skipbelow=0pt,
                   userdefinedwidth=\linewidth]%
  \begin{block}{#1}%
  \begin{minipage}[t]%
    [\dimexpr\gridCellHeight-\ribbonHeight-2\blockPadding-2\rblockBorder\relax][t]%
    {\dimexpr\linewidth-2\blockPadding\relax}%
}{%
  \end{minipage}%
  \end{block}%
  \end{mdframed}%
}

\newenvironment{heroblock}[1]{%
  \setbeamercolor{block title}{fg=UHGreen,bg=UHGold}%
  \setbeamercolor{block body}{fg=black,bg=BlockBG}%
  \begin{mdframed}[linecolor=UHGold,linewidth=\heroBorder,
                   backgroundcolor=BlockBG,
                   innerleftmargin=0pt,innerrightmargin=0pt,
                   innertopmargin=0pt,innerbottommargin=0pt,
                   skipabove=0pt,skipbelow=0pt,
                   userdefinedwidth=\linewidth]%
  \begin{block}{#1}%
  \begin{minipage}[t]%
    [\dimexpr\bodyHeight-\ribbonHeight-2\blockPadding-2\heroBorder\relax][t]%
    {\dimexpr\linewidth-2\blockPadding\relax}%
}{%
  \end{minipage}%
  \end{block}%
  \end{mdframed}%
}

% =====================================================================
%  List + siunitx config
% =====================================================================
\setlist[itemize]{label=\color{UHGreen}\textbf{\textbullet},
                  leftmargin=1.4em,labelsep=0.5em,
                  itemsep=5pt,topsep=2pt,parsep=0pt}
\setlist[itemize,2]{label=\color{UHGreen}\textendash,
                    leftmargin=1.2em,labelsep=0.4em,
                    itemsep=3pt,topsep=2pt,parsep=0pt}

\sisetup{detect-all=true}
```

- [ ] **Step 2: Write the new `poster.tex`.**

Use the Write tool to overwrite `poster.tex` with the following exact content:

```latex
% =====================================================================
%  Conference poster — Neutrino 2026
%  "Enhancing Angular Sensitivity of Segmented Antineutrino Detectors
%   for Reactor Monitoring"
%
%  Target: 4 ft × 3 ft landscape (48" × 36" = 121.92 × 91.44 cm)
%  A0 fallback: comment-swap the \usepackage[...]{beamerposter} line.
%
%  Layout system: parameterized knobs in config/_preamble.tex.
%  See docs/superpowers/specs/2026-05-29-poster-layout-overhaul-design.md
% =====================================================================

%%% To-Do %%%
% [X] Page resize to 48"x36" + parameterized layout overhaul
% [X] Fix references to non-placeholder set
% [X] Update figure caption reference rendering bug (was [?])
% [X] Add section content for Blocks 1..5
% [X] Update contributors list
% [X] Update Acknowledgements section
% [X] Add QR code to Paper B
% [X] Fix horizontal text clipping issue in body blocks
% [X] Adjust Acknowledgements section to fix text clipping
% [ ] Finalize affiliate seals
% [ ] Replace LLNL-POST-XXXXXX placeholder before final submission
% [ ] Update figures to consistent formatting and colorblind-friendly palette

\documentclass[final]{beamer}
\usepackage[size=custom,width=121.92,height=91.44,scale=1.25]{beamerposter}
% A0 fallback (swap the line above for this one):
% \usepackage[size=a0,orientation=landscape,scale=1.25]{beamerposter}

\input{config/_preamble}
\usefonttheme{serif}

% =====================================================================
\begin{document}
\begin{frame}[t]

% ----------------- TITLE BANNER OVERLAY ------------------------------
\begin{tikzpicture}[remember picture,overlay]
  \fill[UHGreen]
    (current page.north west)
    rectangle ([yshift=-\bannerHeight]current page.north east);
  \fill[UHGold]
    ([yshift=-\bannerHeight]current page.north west)
    rectangle ([yshift=-\dimexpr\bannerHeight+\goldStripWidth\relax]
               current page.north east);
\end{tikzpicture}

% ----------------- TITLE BANNER CONTENT ------------------------------
% Banner content lives in a vertically-centered minipage occupying
% exactly \bannerHeight. Three columns: left logo / title / right logos.
\noindent\begin{minipage}[c][\bannerHeight][c]{\paperwidth}
  \centering
  \begin{minipage}[c]{0.14\paperwidth}
    \centering
    \titlelogo{14}{14}{figures/logos/university_of_hawaii_at_manoa_logo-freelogovectors.net_}
  \end{minipage}\hfill
  \begin{minipage}[c]{0.70\paperwidth}
    \input{content/title}
  \end{minipage}\hfill
  \begin{minipage}[c]{0.14\paperwidth}
    \centering
    \titlelogo{14}{6.75}{figures/logos/llnl}\\[0.5cm]
    \titlelogo{14}{6.75}{figures/logos/MTV-logo-color}
  \end{minipage}
\end{minipage}%
\par\vspace{\dimexpr\goldStripWidth + \bannerBodyGap\relax}

% =====================================================================
%  BODY — grid panel (2x2) + hero panel (full height)
% =====================================================================
\noindent\hspace*{\outerMargin}%
\begin{minipage}[t][\bodyHeight][t]{\gridPanelWidth}
  % --- row 1 (blk1, blk3) ---
  \begin{minipage}[t][\gridCellHeight][t]{\gridCellWidth}
    \begin{rblock}{Localization of IBD Source}
      \input{content/block1}
    \end{rblock}
  \end{minipage}%
  \hspace{\gridGutter}%
  \begin{minipage}[t][\gridCellHeight][t]{\gridCellWidth}
    \begin{rblock}{Our Approach to Simulation Design}
      \input{content/block3}
    \end{rblock}
  \end{minipage}

  \vspace{\gridGutter}

  % --- row 2 (blk2, blk4) ---
  \begin{minipage}[t][\gridCellHeight][t]{\gridCellWidth}
    \begin{rblock}{Traditional Approach}
      \input{content/block2}
    \end{rblock}
  \end{minipage}%
  \hspace{\gridGutter}%
  \begin{minipage}[t][\gridCellHeight][t]{\gridCellWidth}
    \begin{rblock}{Novel Algorithm for Segmented Detectors}
      \input{content/block4}
    \end{rblock}
  \end{minipage}
\end{minipage}%
\hspace{\gridHeroGap}%
\begin{minipage}[t][\bodyHeight][t]{\heroPanelWidth}
  \begin{heroblock}{$\bigstar$\,Conclusions, Findings, and Future Work}
    \input{content/block5}
    \vfill
  \end{heroblock}
\end{minipage}\hspace*{\outerMargin}

% =====================================================================
%  FOOTER STRIP
% =====================================================================
\begin{tikzpicture}[remember picture,overlay]
  \fill[UHGold]
    ([yshift=\footerHeight]current page.south west)
    rectangle ([yshift=\dimexpr\footerHeight+\goldStripWidth\relax]
               current page.south east);
  \fill[UHGreen]
    (current page.south west)
    rectangle ([yshift=\footerHeight]current page.south east);
  \node[anchor=center, text=white] at
       ([yshift=\dimexpr 0.5\footerHeight\relax]current page.south) {
    \begin{minipage}{\dimexpr\paperwidth-2\outerMargin\relax}
      \input{content/footer}
    \end{minipage}
  };
\end{tikzpicture}
\end{frame}
\end{document}
```

- [ ] **Step 3: Build (two-pass for TikZ overlays).**

```bash
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Expected: both passes exit 0; final line `Output written on poster.pdf (1 page, ~700K bytes).`

If the first pass fails on the `\usepackage[...]{beamerposter}` line with an unrecognized `size=custom` error, the local TeX Live build is older than `beamerposter` v3. Fallback: replace the package call with:

```latex
\PassOptionsToPackage{paperwidth=121.92cm,paperheight=91.44cm}{geometry}
\usepackage[size=a0,orientation=landscape,scale=1.25]{beamerposter}
\setlength{\paperwidth}{121.92cm}\setlength{\paperheight}{91.44cm}
```

Then re-run both passes.

- [ ] **Step 4: Visual check.**

Open `poster.pdf`. Verify:
- Page dimensions are 48″ × 36″ (use `pdfinfo poster.pdf | grep "Page size"` — expect `3456.00 x 2592.00 pts` for 48×36 at 72 dpi).
- Green title banner spans the full top of the page; gold underline visible just below it.
- All three logos render in the title banner (UH left, LLNL+MTV stacked right). Title text in center.
- Five blocks visible in the body: four in a 2×2 grid on the left, one tall hero on the right.
- Block borders intact (green for the four rblocks; gold for the hero).
- Green footer strip spans the full bottom; gold underline above it.
- No `[?]` markers (other than block2's existing `\cite{Duvall:2024cae}`, addressed in Task 5).
- No missing-glyph squares (■).

If the build fails or the visual check shows broken layout, restore both files and stop:

```bash
cp config/_preamble.tex.old config/_preamble.tex
cp poster.tex.old poster.tex
```

Then diff the new versions against `.old` to identify the issue before retrying.

---

## Task 3: Migrate `content/title.tex`

Three font-size macro swaps. No prose changes.

**Files:**
- Modify: `content/title.tex`

- [ ] **Step 1: Swap the banner title size command.**

In `content/title.tex`, replace:

```latex
{\veryHuge\bfseries Enhancing Angular Sensitivity of\par}
\vspace{0.15cm}
{\veryHuge\bfseries Segmented Antineutrino Detectors\par}
```

With:

```latex
{\bannerTitleSize\bfseries Enhancing Angular Sensitivity of\par}
\vspace{0.15cm}
{\bannerTitleSize\bfseries Segmented Antineutrino Detectors\par}
```

- [ ] **Step 2: Swap the subtitle size command.**

In `content/title.tex`, replace:

```latex
{\Large\itshape for Reactor Monitoring\par}
```

With:

```latex
{\bannerSubtitleSize\itshape for Reactor Monitoring\par}
```

- [ ] **Step 3: Swap the author/affiliation size command.**

In `content/title.tex`, replace:

```latex
{\normalsize\color{UHGreen!10!white}%
```

With:

```latex
{\bannerAuthorSize\color{UHGreen!10!white}%
```

- [ ] **Step 4: Build (two-pass).**

```bash
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Expected: exit 0; no new warnings.

- [ ] **Step 5: Visual check.**

Open `poster.pdf`. Title banner text should render at the same sizes as before — `\veryHuge` and `\bannerTitleSize` both expand to `\veryHuge` per the knob definition, so this is a refactor-only change. If sizes look wrong, the swap missed something.

---

## Task 4: Migrate `content/block1.tex`

One figure-width swap.

**Files:**
- Modify: `content/block1.tex`

- [ ] **Step 1: Swap the figure width.**

In `content/block1.tex`, replace:

```latex
\includegraphics[width=0.79\linewidth]{fig/asy_fig_1_paperB.pdf}
```

With:

```latex
\includegraphics[width=\figLarge]{fig/asy_fig_1_paperB.pdf}
```

(`\figLarge` = `0.75\linewidth`; the segmentation-scaling figure shrinks very slightly.)

- [ ] **Step 2: Build (two-pass).**

```bash
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Expected: exit 0.

- [ ] **Step 3: Visual check.**

In `poster.pdf`, the block 1 figure (segmentation scaling) should render at ~75% of the block-1 inner width. Caption underneath unchanged.

---

## Task 5: Migrate `content/block2.tex`

One figure-width swap; one `\cite` removal.

**Files:**
- Modify: `content/block2.tex`

- [ ] **Step 1: Swap the figure width.**

In `content/block2.tex`, replace:

```latex
\includegraphics[width=0.4\linewidth]{fig/angular_resolution_analytic_ylog_PackFactor_v2Useful.pdf}
```

With:

```latex
\includegraphics[width=\figHalf]{fig/angular_resolution_analytic_ylog_PackFactor_v2Useful.pdf}
```

- [ ] **Step 2: Replace the broken `\cite` with hand-typed `[2]`.**

In `content/block2.tex`, replace:

```latex
This result is taken from our previous study~\cite{Duvall:2024cae}.
```

With:

```latex
This result is taken from our previous study~[2].
```

(Matches the hand-typed reference numbering in `content/footer.tex`.)

- [ ] **Step 3: Build (two-pass).**

```bash
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Expected: exit 0; **the `Citation 'Duvall:2024cae' undefined` warning is gone**.

- [ ] **Step 4: Visual check.**

In `poster.pdf`, block 2's figure caption now ends with `... our previous study [2].` — no more `[?]` marker. Figure widens slightly (0.4 → 0.48).

---

## Task 6: Migrate `content/block3.tex`

One figure-width swap; one inline font-size swap inside `overpic`.

**Files:**
- Modify: `content/block3.tex`

- [ ] **Step 1: Swap the figure width.**

In `content/block3.tex`, replace:

```latex
    \begin{overpic}[width=0.39\linewidth]{fig/RAT_PAC_IBD_run_6_5_crop.png}
```

With:

```latex
    \begin{overpic}[width=\figHalf]{fig/RAT_PAC_IBD_run_6_5_crop.png}
```

- [ ] **Step 2: Swap the inline `\footnotesize` for the role macro.**

In `content/block3.tex`, replace the line immediately after `\begin{overpic}...`:

```latex
      \footnotesize
```

With:

```latex
      \smallPrintSize
```

(`\smallPrintSize` expands to `\footnotesize` today — refactor-only, but routes the size through the role knob so future tuning propagates.)

- [ ] **Step 3: Build (two-pass).**

```bash
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Expected: exit 0.

- [ ] **Step 4: Visual check.**

In `poster.pdf`, block 3's RAT-PAC visualization is now ~48% of the block-3 inner width (slightly larger than before). The white annotation labels inside the figure (`neutron capture`, `positron annihilation`, `inverse β decay`) and their arrows are still aligned correctly — `overpic`'s `\put(x,y)` coords are percent-based, so width changes don't break alignment.

---

## Task 7: Migrate `content/block4.tex`

Two figure-width swaps (inside the two side-by-side minipages); two inline font swaps.

**Files:**
- Modify: `content/block4.tex`

- [ ] **Step 1: Swap minipage width #1.**

In `content/block4.tex`, the first minipage line (around line 14):

```latex
    \begin{minipage}[t]{0.48\linewidth}
```

stays as `0.48\linewidth` (this is the *minipage* width, not a figure width — it's already correct). **No change to this line.**

The same applies to the second minipage (around line 76):

```latex
    \begin{minipage}[t]{0.48\linewidth}
```

**No change.**

- [ ] **Step 2: Swap the first `\footnotesize` inside the picture env.**

In `content/block4.tex`, inside the first `\begin{picture}(10,5)` block (around line 17):

```latex
\begin{picture}(10,5)
  \footnotesize
```

Replace with:

```latex
\begin{picture}(10,5)
  \smallPrintSize
```

- [ ] **Step 3: Swap the second `\footnotesize` inside the picture env.**

In `content/block4.tex`, inside the second `\begin{picture}(10,4)` block (around line 81):

```latex
\begin{picture}(10,4)
  \footnotesize
```

Replace with:

```latex
\begin{picture}(10,4)
  \smallPrintSize
```

- [ ] **Step 4: Build (two-pass).**

```bash
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Expected: exit 0.

- [ ] **Step 5: Visual check.**

In `poster.pdf`, block 4's two side-by-side geometry diagrams render with picture-primitive labels in the same `\footnotesize`-equivalent size as before. Arrows and axis labels intact.

---

## Task 8: Migrate `content/block5.tex` (the heaviest)

Multiple figure-width swaps; three `height=1.675in` removals; θ-label TikZ coord recalibration via iterative build-eyeball-nudge.

**Files:**
- Modify: `content/block5.tex`

- [ ] **Step 1: Swap the three binning-distribution figure widths.**

In `content/block5.tex`, the binning distribution figure triplet (around lines 18–22):

```latex
\includegraphics[width=0.3\linewidth]{fig/bin_dist_rot0_001wt.pdf}
&
\includegraphics[width=0.3\linewidth]{fig/bin_dist_rot30_001wt.pdf}
&
\includegraphics[width=0.3\linewidth]{fig/bin_dist_rot45_001wt.pdf} \\
```

Replace all three `width=0.3\linewidth` with `width=\figThird`:

```latex
\includegraphics[width=\figThird]{fig/bin_dist_rot0_001wt.pdf}
&
\includegraphics[width=\figThird]{fig/bin_dist_rot30_001wt.pdf}
&
\includegraphics[width=\figThird]{fig/bin_dist_rot45_001wt.pdf} \\
```

- [ ] **Step 2: Switch FND panel #1 to width-based sizing.**

In `content/block5.tex`, the first FND panel (around lines 54–61):

```latex
    \begin{tikzpicture}
        \node[inner sep=0]
            {\includegraphics[height=1.675in]{fig/parallel/FND_n_10_dx_50.pdf}};
        
        \node[red, font=\small] at (1.85,2.225) {$\vartheta_\mathrm{fit}$};
        \node[blue, font=\small] at (1.15,2.225) {$\vartheta_\mathrm{min}$};
        \node[gray!50!black, font=\small] at (0.25,2.225) {$\vartheta_\mathrm{true}$};
    \end{tikzpicture}
```

Replace with:

```latex
    \begin{tikzpicture}
        \node[inner sep=0]
            {\includegraphics[width=\figThird]{fig/parallel/FND_n_10_dx_50.pdf}};
        
        \node[red, font=\captionSize] at (1.85,2.225) {$\vartheta_\mathrm{fit}$};
        \node[blue, font=\captionSize] at (1.15,2.225) {$\vartheta_\mathrm{min}$};
        \node[gray!50!black, font=\captionSize] at (0.25,2.225) {$\vartheta_\mathrm{true}$};
    \end{tikzpicture}
```

(`height=1.675in` removed, replaced with `width=\figThird`; `font=\small` → `font=\captionSize`. The `(x, y)` coords are unchanged for now — they will be recalibrated after the first build.)

- [ ] **Step 3: Switch FND panel #2 to width-based sizing.**

In `content/block5.tex`, the second FND panel (around lines 70–76):

```latex
    \begin{tikzpicture}
        \node[inner sep=0]
            {\includegraphics[height=1.675in]{fig/parallel/FND_n_100_dx_50.pdf}};
        
        \node[red, font=\small] at (-0.25,2.23) {$\vartheta_\mathrm{fit}$};
        \node[blue, font=\small] at (-0.9,2.23) {$\vartheta_\mathrm{min}$};
        \node[gray!50!black, font=\small] at (0.45,2.23) {$\vartheta_\mathrm{true}$};
    \end{tikzpicture}
```

Replace with:

```latex
    \begin{tikzpicture}
        \node[inner sep=0]
            {\includegraphics[width=\figThird]{fig/parallel/FND_n_100_dx_50.pdf}};
        
        \node[red, font=\captionSize] at (-0.25,2.23) {$\vartheta_\mathrm{fit}$};
        \node[blue, font=\captionSize] at (-0.9,2.23) {$\vartheta_\mathrm{min}$};
        \node[gray!50!black, font=\captionSize] at (0.45,2.23) {$\vartheta_\mathrm{true}$};
    \end{tikzpicture}
```

- [ ] **Step 4: Switch FND panel #3 to width-based sizing.**

In `content/block5.tex`, the third FND panel (around lines 85–91):

```latex
    \begin{tikzpicture}
        \node[inner sep=0]
            {\includegraphics[height=1.675in]{fig/parallel/FND_n_1000_dx_50.pdf}};
        
        \node[red, font=\small] at (0.25,2.23) {$\vartheta_\mathrm{fit}$};
        \node[blue, font=\small] at (-0.4,2.23) {$\vartheta_\mathrm{min}$};
        \node[gray!50!black, font=\small] at (0.9,2.23) {$\vartheta_\mathrm{true}$};
    \end{tikzpicture}
```

Replace with:

```latex
    \begin{tikzpicture}
        \node[inner sep=0]
            {\includegraphics[width=\figThird]{fig/parallel/FND_n_1000_dx_50.pdf}};
        
        \node[red, font=\captionSize] at (0.25,2.23) {$\vartheta_\mathrm{fit}$};
        \node[blue, font=\captionSize] at (-0.4,2.23) {$\vartheta_\mathrm{min}$};
        \node[gray!50!black, font=\captionSize] at (0.9,2.23) {$\vartheta_\mathrm{true}$};
    \end{tikzpicture}
```

- [ ] **Step 5: Swap the money plot width.**

In `content/block5.tex` (around line 102):

```latex
    \includegraphics[width=0.5\linewidth]{fig/parallel/06_money_plot_fit_arctan_log_4p.pdf}
```

Replace with:

```latex
    \includegraphics[width=\figLarge]{fig/parallel/06_money_plot_fit_arctan_log_4p.pdf}
```

- [ ] **Step 6: First build to see where the θ-labels land.**

```bash
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Expected: exit 0.

- [ ] **Step 7: Eyeball the FND panel θ-labels in `poster.pdf`.**

For each of the three FND panels (a) n=10, (b) n=100, (c) n=1000:

- The three labels `θ_fit` (red), `θ_min` (blue), `θ_true` (gray) should sit *just above* the plot, near the top edge.
- The horizontal position of each label should match the corresponding vertical line/peak in the plot below it.

Because the figures switched from height-based (1.675 in) to width-based (`\figThird` of the block 5 inner width ≈ 13.6 cm), the figure heights now follow the PDFs' intrinsic aspect ratios and may differ from the previous 1.675 in. The θ-label `(x, y)` coords were calibrated against the old height; if the new height differs, the labels will be vertically offset (sitting either inside the plot or floating too high above it).

- [ ] **Step 8: Recalibrate the θ-label coords.**

For each panel where labels are misplaced:

- **Vertical (y) offset:** if labels sit *inside* the plot, decrease `y` (e.g., 2.225 → 2.0 → 1.8). If labels float *too high* above the plot, increase `y` (e.g., 2.225 → 2.4 → 2.6). Adjust all three labels in the panel together — they share the same `y`.
- **Horizontal (x) offset:** if labels don't sit above their corresponding plot features, nudge each label's `x` individually. The relative spacing between `θ_fit`, `θ_min`, `θ_true` within a panel should match the spacing of the features they label.

Use the Edit tool to update the coords in `content/block5.tex` for each panel as needed.

- [ ] **Step 9: Rebuild and re-eyeball.**

```bash
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Inspect the FND panels again. If still off, repeat Steps 8–9. Expect 2–3 total iterations. The target is "each label sits visually just above its plot feature, all three at the same y across each panel."

- [ ] **Step 10: Final visual check for block 5.**

In `poster.pdf`, block 5 (hero) should show:
- "Key findings" and "Future work" bullet lists at the top.
- The three binning-distribution figures (n=10, n=100, n=1000) panels with directional arrows below.
- The three FND panels in a row with properly-aligned θ-labels above each.
- The money-plot at the bottom, sized at `\figLarge` (~75% of hero inner width).

---

## Task 9: Rebuild `content/footer.tex`

Complete replacement. No negative `\hspace`, no `\vspace` slide, no `nu2026_poster/` path prefix.

**Files:**
- Modify: `content/footer.tex` (full replacement)

- [ ] **Step 1: Overwrite `content/footer.tex`.**

Use the Write tool to overwrite `content/footer.tex` with the following exact content:

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
  Technology, and Verification under Department of Energy National
  Nuclear Security Administration award number DE-NA0003920.
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

- [ ] **Step 2: Build (two-pass).**

```bash
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Expected: exit 0; **no overfull-hbox warning at lines 31–33** (the previous 70 pt overfull box is gone).

- [ ] **Step 3: Visual check.**

In `poster.pdf`, the footer strip shows:
- Left half (~50%): "References" header with two numbered entries, rendered at `\captionSize` (= `\small`).
- Middle (~36%): "Acknowledgments" header with the LLNL/DOE/MTV paragraph, rendered at `\smallPrintSize` (= `\footnotesize`).
- Right (~10%): "Ref. [1]:" label with the QR code below it.
- No content overflows the green footer strip vertically; all three columns sit within the strip.

---

## Task 10: Verify at 48″ × 36″ (full checklist)

**Files:** none modified.

- [ ] **Step 1: Clean build.**

```bash
rm -f poster.aux poster.log poster.nav poster.out poster.snm poster.toc
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Expected: both passes exit 0; final `poster.pdf` size in the 700–800 KB range.

- [ ] **Step 2: Confirm page dimensions.**

```bash
pdfinfo poster.pdf | grep -E "Pages|Page size"
```

Expected:
```
Pages:           1
Page size:       3456 x 2592 pts (or similar; 121.92 cm × 91.44 cm)
```

(48 in × 72 pt/in = 3456 pt; 36 in × 72 pt/in = 2592 pt. May print as cm or with slight rounding.)

- [ ] **Step 3: Warning scan.**

```bash
grep -iE "warning|overfull" poster.log | grep -viE "underfull|font shape|sansmath"
```

Expected: no `Citation .* undefined`, no `Overfull \hbox` in the footer region (lines around the footer minipages), no `File .* not found`. Pre-existing "Underfull hbox" warnings from block content are acceptable.

- [ ] **Step 4: PDF visual checklist.**

Open `poster.pdf` and confirm each item:

- [ ] No `[?]` or `??` markers anywhere in the document.
- [ ] No missing-glyph squares (■) — Greek footgun regression check.
- [ ] No "draft" placeholder boxes (would mean a figure file is missing).
- [ ] Green title banner spans full page width at the top.
- [ ] Gold underline visible immediately below the title banner.
- [ ] UH logo in left wing, LLNL+MTV logos stacked in right wing.
- [ ] Title text, subtitle, author list visible in center of banner.
- [ ] Block 1 ("Localization of IBD Source") in top-left of grid panel; green border.
- [ ] Block 2 ("Traditional Approach") in bottom-left of grid panel.
- [ ] Block 3 ("Our Approach to Simulation Design") in top-right of grid panel.
- [ ] Block 4 ("Novel Algorithm for Segmented Detectors") in bottom-right of grid panel.
- [ ] Hero block 5 ("★ Conclusions, Findings, and Future Work") full-height on the right; gold border, gold ribbon title bar.
- [ ] Itemize bullets visible in all block bullet lists.
- [ ] All figures rendered (no missing images).
- [ ] FND panel θ-labels in block 5 sit visually just above each plot (recalibrated in Task 8).
- [ ] No content overflows past `mdframed` block borders.
- [ ] Gold underline visible immediately above the footer strip.
- [ ] Green footer strip spans full page width at the bottom.
- [ ] Footer references (left), acknowledgments (center), QR code (right) all visible; no overflow; no negative-spacing artifacts.

If any item fails, identify the file responsible, restore from backup if needed, and re-do the relevant task.

---

## Task 11: Verify the A0 fallback

**Files:**
- Modify (temporarily): `poster.tex`

- [ ] **Step 1: Swap the beamerposter line to A0.**

In `poster.tex`, find:

```latex
\usepackage[size=custom,width=121.92,height=91.44,scale=1.25]{beamerposter}
% A0 fallback (swap the line above for this one):
% \usepackage[size=a0,orientation=landscape,scale=1.25]{beamerposter}
```

Replace with:

```latex
% \usepackage[size=custom,width=121.92,height=91.44,scale=1.25]{beamerposter}
% A0 fallback (swap the line above for this one):
\usepackage[size=a0,orientation=landscape,scale=1.25]{beamerposter}
```

(Comments swapped: the A0 line is now active.)

- [ ] **Step 2: Clean build at A0.**

```bash
rm -f poster.aux poster.log poster.nav poster.out poster.snm poster.toc
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Expected: both passes exit 0.

- [ ] **Step 3: Confirm A0 page dimensions.**

```bash
pdfinfo poster.pdf | grep -E "Pages|Page size"
```

Expected:
```
Pages:           1
Page size:       3370.39 x 2383.94 pts (A0)
```

- [ ] **Step 4: PDF visual checklist (A0).**

Open `poster.pdf` and confirm the same checklist as Task 10 Step 4. The poster should be visually similar to the 48×36 version, scaled to A0 dimensions. Major regions (banner, body, footer) should reflow proportionally. Fine details (block padding, border widths) stay the same absolute size.

Any item that *fails at A0 but passed at 48×36* indicates a length that wasn't truly paper-derived — find it and fix it (likely a hardcoded cm value that should have used `\paperheight` or `\paperwidth`).

- [ ] **Step 5: Revert poster.tex to 48×36.**

In `poster.tex`, restore the original (48×36 active, A0 commented):

```latex
\usepackage[size=custom,width=121.92,height=91.44,scale=1.25]{beamerposter}
% A0 fallback (swap the line above for this one):
% \usepackage[size=a0,orientation=landscape,scale=1.25]{beamerposter}
```

- [ ] **Step 6: Rebuild at 48×36 to restore the final PDF.**

```bash
rm -f poster.aux poster.log poster.nav poster.out poster.snm poster.toc
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
pdflatex -interaction=nonstopmode -halt-on-error poster.tex
```

Confirm `pdfinfo poster.pdf | grep "Page size"` reports the 48×36 dimensions again.

---

## Task 12: Update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

This task updates the project documentation so it reflects the post-overhaul state. Five distinct edits, each tied to a section of CLAUDE.md.

- [ ] **Step 1: Replace the "Body layout" section.**

In `CLAUDE.md`, find the section starting `## Body layout` and ending just before `## References, acknowledgements, QR code`. Replace it entirely with:

```markdown
## Body layout

The body region is split horizontally into two panels:

- **Grid panel** (left, `\gridHeroSplit` ≈ 0.62 of body width) — a 2×2 matrix of `rblock` instances:
  - top-left: ① "Localization of IBD Source" — `content/block1.tex`
  - bottom-left: ② "Traditional Approach" — `content/block2.tex`
  - top-right: ③ "Our Approach to Simulation Design" — `content/block3.tex`
  - bottom-right: ④ "Novel Algorithm for Segmented Detectors" — `content/block4.tex`
- **Hero panel** (right, remaining body width) — a single full-height `heroblock`:
  - ⑤ "★ Conclusions, Findings, and Future Work" — `content/block5.tex`
- **Footer strip** (full width, green, TikZ overlay) — refs + acks + QR code — `content/footer.tex`

All layout dimensions derive from `\paperwidth` / `\paperheight` and the named knobs in `config/_preamble.tex` (see "Tuning the layout" below). The 2×2 cell size is computed as `\gridCellWidth × \gridCellHeight`, where each cell width = `(\gridPanelWidth - \gridGutter) / 2` and each cell height = `(\bodyHeight - \gridGutter) / 2`. Hero panel uses the full `\bodyHeight`.

Block titles are set in `poster.tex` at the `\begin{rblock}{...}` / `\begin{heroblock}{...}` call sites, not in the block files themselves.
```

- [ ] **Step 2: Replace the "Visual identity" layout-constants paragraph.**

In `CLAUDE.md`, find the paragraph starting `Defined in \`config/_preamble.tex\` (palette block...)` inside the `## Visual identity` section. The palette listing stays. After it, find the "Title banner is a TikZ overlay..." paragraph — replace with:

```markdown
Title banner is a TikZ overlay anchored to `current page.north`; the green strip extends down by `\bannerHeight` and the gold underline below it by `\goldStripWidth`. Coordinates derive from these knobs, not from hardcoded cm values. Footer strip is the mirror at the bottom (`\footerHeight` for the green region, `\goldStripWidth` for the gold underline above it). The hero block in the right column uses a separate `heroblock` environment (defined in `_preamble.tex`) with a `\heroBorder`-thick gold `mdframed` border and a gold-bar title (UH-green text on UH-gold). Regular blocks use `rblock` with a `\rblockBorder`-thick UH-green border and a green-bar title (white text on UH-green).
```

- [ ] **Step 3: Update footgun item 5.**

In `CLAUDE.md`, find footgun item 5 starting with `5. **Hard-coded inner-minipage heights break on title/padding tweaks.**`. Replace the entire numbered item with:

```markdown
5. **Inner-minipage heights derive from `\dimexpr` over named lengths.** Previously a footgun: `heroblock` and `rblock` subtracted a magic `3.4 cm` from `\bodyheight` / `\rblockheight` to clear the ribbon title, and that constant went stale every time `\ribbonheight` or `\blockpadding` was tweaked, with content silently overflowing the border. **Now eliminated:** both environments compute their inner-minipage height as `\dimexpr\<surroundCellHeight> - \ribbonHeight - 2\blockPadding - 2\<borderWidth>\relax`. If any of `\ribbonHeight`, `\blockPadding`, `\rblockBorder`, or `\heroBorder` is tuned, the inner area adjusts automatically — no stale constant to chase.
```

- [ ] **Step 4: Update the QR-path note.**

In `CLAUDE.md`, find the QR-code paragraph inside `## References, acknowledgements, QR code` that mentions the `nu2026_poster/` path prefix. Replace it with:

```markdown
The QR code is embedded with `\includegraphics[width=0.9\linewidth]{content/ArXiV_QR_code.png}`. The path is relative to the build directory (in-place builds work directly). The 2026-05-29 layout overhaul removed the previous `nu2026_poster/`-prefixed path that required building from a specifically-named parent directory.
```

- [ ] **Step 5: Add a new "Tuning the layout" subsection.**

In `CLAUDE.md`, immediately after the existing `## Body layout` section (now ending with the block-titles-in-poster.tex note), insert a new section:

```markdown
## Tuning the layout — where the knobs live

All user-tunable layout parameters live in the **KNOBS** block at the top of `config/_preamble.tex`, organized into four groups. Edit values there, rebuild (two-pass), and the layout reflows.

**Region heights** (paper-relative fractions of `\paperheight`):
- `\bannerHeightFrac` (default 0.19) — title banner height
- `\footerHeightFrac` (default 0.075) — footer banner height

**Six gap knobs** (absolute cm; do not scale with page size):
- `\outerMargin` (1 cm) — page edge to body grid horizontal margin
- `\bannerBodyGap` (1.5 cm) — vertical gap between banner gold strip and body top
- `\bodyFooterGap` (1.0 cm) — vertical gap between body bottom and footer gold strip
- `\gridGutter` (1.0 cm) — horizontal and vertical gap between 2×2 grid cells
- `\gridHeroGap` (1.0 cm) — horizontal gap between grid panel and hero panel
- `\blockPadding` (0.6 cm) — inside-frame padding for all block environments

**Body split:**
- `\gridHeroSplit` (0.62) — grid panel as a fraction of body-available width

**Type roles** (size commands; weight/shape applied at use site):
- `\bannerTitleSize` (`\veryHuge`), `\bannerSubtitleSize` (`\LARGE`), `\bannerAuthorSize` (`\normalsize`)
- `\blockTitleSize` (`\Large`), `\bodySize` (`\normalsize`)
- `\captionSize` (`\small`), `\smallPrintSize` (`\footnotesize`)

**Figure width slots** (fractions of containing-block `\linewidth`):
- `\figFull` (0.95), `\figLarge` (0.75), `\figHalf` (0.48), `\figThird` (0.31)

Below the KNOBS block, **DERIVED LENGTHS** computes `\bannerHeight`, `\footerHeight`, `\bodyHeight`, `\bodyWidth`, `\gridPanelWidth`, `\heroPanelWidth`, `\gridCellWidth`, `\gridCellHeight` via `\setlength{...}{\dimexpr ...\relax}`. Block files and `poster.tex` consume the derived lengths, not the raw knobs.

To page-resize, edit only the `beamerposter` package call in `poster.tex` — for example, swap to A0 by commenting the `size=custom` line and uncommenting the `size=a0,orientation=landscape` fallback. All region heights and widths reflow automatically.
```

- [ ] **Step 6: Spot-check the edited CLAUDE.md.**

```bash
grep -nE "^## " CLAUDE.md
```

Expected: the section headers include `## Body layout`, `## Tuning the layout — where the knobs live`, and the existing ones. Read the updated sections to confirm internal consistency (no lingering references to `\bodyheight` lowercase, `\rblockgap`, or 2+2+1 three-column layout).

---

## Task 13: Clean up backups

**Files:**
- Delete: `config/_preamble.tex.old`
- Delete: `poster.tex.old`
- Delete: `poster.baseline.pdf`

- [ ] **Step 1: Confirm Task 10 and Task 11 verification both passed.**

If either verification revealed issues that haven't been resolved, **stop and do not delete backups**. Backups must remain until the final PDF is confirmed good.

- [ ] **Step 2: Delete the backups.**

```bash
rm config/_preamble.tex.old poster.tex.old poster.baseline.pdf
```

Expected: silent success.

- [ ] **Step 3: Confirm deletion.**

```bash
ls config/_preamble.tex.old poster.tex.old poster.baseline.pdf 2>&1
```

Expected: `No such file or directory` for all three.

---

## Self-review

Spec coverage check (every spec section maps to one or more tasks):

| Spec section | Covered by |
|---|---|
| §1 Background | (motivation only; no implementation) |
| §2 Decisions summary | All tasks |
| §3 Architecture | Task 2 (both files) |
| §4 Token system (KNOBS block) | Task 2 Step 1 |
| §5 Derived lengths | Task 2 Step 1 (in the DERIVED LENGTHS section of `_preamble.tex`) |
| §6.1 Banner template | Task 2 Step 2 (TIKZ overlay + banner content minipage) |
| §6.2 Footer template | Task 2 Step 2 (TIKZ overlay) and Task 9 (content) |
| §6.3 Body grid | Task 2 Step 2 |
| §6.4 Block environments | Task 2 Step 1 (rblock / heroblock defs) |
| §6.5 Captions, block titles, body type | Task 2 Step 1 (`\setbeamerfont` bindings) |
| §7 Block-file migration table | Tasks 3 (title), 4 (block1), 5 (block2), 6 (block3), 7 (block4), 8 (block5), 9 (footer) |
| §8.1 Build pipeline | All build steps |
| §8.2 Implementation sequence | Tasks 1–13 (matches the 12-step sequence) |
| §8.3 Verification checklist | Task 10 Steps 3–4 |
| §8.4 CLAUDE.md updates | Task 12 |
| §9 Footguns | Task 12 Step 3 (footgun item 5 update); the other four footguns are preserved by Task 2's preamble |
| §10 Out of scope | (not implemented; explicit non-goals) |

No gaps found. Every spec requirement is covered.

Placeholder scan: no "TBD", "TODO", "implement later", "Add appropriate", "similar to Task N" markers in the plan. All code blocks contain literal content.

Type consistency check: macro names used across tasks match the definitions in Task 2 (`\bannerTitleSize`, `\bannerSubtitleSize`, `\bannerAuthorSize`, `\blockTitleSize`, `\bodySize`, `\captionSize`, `\smallPrintSize`, `\figFull`, `\figLarge`, `\figHalf`, `\figThird`, `\bannerHeight`, `\footerHeight`, `\bodyHeight`, `\gridCellWidth`, `\gridCellHeight`, `\outerMargin`, `\bannerBodyGap`, `\bodyFooterGap`, `\gridGutter`, `\gridHeroGap`, `\blockPadding`, `\gridHeroSplit`, `\rblockBorder`, `\heroBorder`, `\goldStripWidth`, `\ribbonHeight`, `\bannerInnerPad`, `\bannerHeightFrac`, `\footerHeightFrac`). All consumers in Tasks 3–11 use these exact names.

No issues to fix inline.
