# Documentation refresh + project cleanup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate the documentation/state drift accumulated across the modular split + logo workflow phases by rewriting drifted CLAUDE.md sections, dual-labeling POSTER_CONTENT.md tables, deleting obsolete files, and rescuing useful figure-inclusion patterns from a soon-to-be-deleted reference.

**Architecture:** Sequential execution. Rescue first (extract figure patterns from `poster_tmp.tex`), then state cleanup (file deletion + build verification), then doc updates (POSTER_CONTENT.md, CLAUDE.md), then final verification. Each task is a self-contained change with a discrete deliverable.

**Tech Stack:** bash (`rm`, `pdflatex`, `grep`), markdown editing, no test framework (this is doc/cleanup work). Verification = build success + content grep checks.

**Spec:** `docs/superpowers/specs/2026-05-14-poster-docs-cleanup-design.md`

**Note:** project is not a git repo, so no `git commit` steps. If/when this becomes a git repo, batch the commits per-task.

---

## File Structure

**Created:**
- `docs/figure-patterns.md` — three reusable figure-inclusion patterns extracted from `poster_tmp.tex`

**Modified:**
- `CLAUDE.md` — rewrite drifted sections (Build, Source-of-truth layout, Figure pipeline), light-edit Visual identity / Body layout, append two new sections (Logos workflow, Silent-failure footguns)
- `POSTER_CONTENT.md` — append Rosetta sentence to block fold note (~line 47); add `Block file` column to §6; rename `File`→`Asset` and add `Block` column to §7; update `fig/` paths to `figures/`

**Deleted (22 files + 1 dir):**
- `poster.tex` + 7 build artifacts: `poster.{aux,log,nav,out,pdf,snm,toc}`
- `poster.portrait.tex.bak`, `poster.portrait.pdf.bak`
- 6 current build artifacts: `main.{aux,log,nav,out,snm,toc}` (NOT `main.pdf` — that is the build output)
- `TMP_RESOURCES/poster_tmp.tex`
- `TMP_RESOURCES/Neutrino Poster 2026.pdf`
- `docs/superpowers/specs/2026-05-14-landscape-poster-redesign-design.md`
- `docs/superpowers/plans/2026-05-14-landscape-poster-redesign.md`
- `figures/logos/lawrence-livermore-national-laboratory-logo-vector.svg`
- `figures/logos/llnl_cropped.svg`
- `docs/superpowers/plans/` (empty after deletion of the landscape-redesign plan)

---

## Task 1: Extract figure-inclusion patterns to `docs/figure-patterns.md`

**Files:**
- Create: `docs/figure-patterns.md`
- Reference (read-only): `TMP_RESOURCES/poster_tmp.tex`

- [ ] **Step 1: Create `docs/figure-patterns.md` with the three extracted patterns**

Use Write to create the file with this exact content:

````markdown
# Figure inclusion patterns

Reference snippets extracted from the legacy `TMP_RESOURCES/poster_tmp.tex` (REVTeX two-column draft, since deleted). Use these when swapping body figure placeholders for real assets.

## 1. Overpic-style annotation overlay on a raster

For a raster figure (PNG/PDF) annotated with white-bordered call-out boxes and arrows pointing to features. Used in `poster_tmp.tex` for the RAT-PAC IBD visualization.

```latex
\usepackage[percent]{overpic}

\begin{overpic}[width=1.0\linewidth]{figures/RAT_PAC_IBD_run_6_5_crop.png}
  \put(16.5,90){\color{white}\vector(0,-1){5}}
  \put(0,93){\fcolorbox{white}{white!30}{%
    \parbox{70pt}{neutron capture
      ${\color{orange}n}\;{}^6\mathrm{Li} \to {}^3\mathrm{H}\;{}^4\mathrm{He}$}}}

  \put(67,45){\color{white}\vector(0,1){15}}
  \put(57,41){\fcolorbox{white}{white!30}{%
    \parbox{50pt}{positron\\ annihilation
      ${\color{red}e^+}\,e^- \to {\color{green}\gamma}\,{\color{green}\gamma}$}}}

  \put(81,86){\color{white}\vector(0,-1){15}}
  \put(65,85){\fcolorbox{white}{white!30}{%
    \parbox{70pt}{inverse $\beta$ decay
      $\bar\nu_e\,{}^1\mathrm{H} \to {\color{red}e^+}\,{\color{orange}n}$}}}
\end{overpic}
```

Coordinates `(x,y)` are percentages of the image (0–100). `\fcolorbox{white}{white!30}` is the white-edge translucent label; `\parbox{Npt}` constrains text width. Use one `\put` per annotation.

## 2. Side-by-side binning matrices with directional arrows

A three-up tabular of related figures with arrow glyphs and angle labels below each, used for the binning-distribution panel.

```latex
\begin{tabular}{ccc}
  \includegraphics[width=0.32\linewidth]{figures/bin_dist_rot0_001wt.pdf} &
  \includegraphics[width=0.32\linewidth]{figures/bin_dist_rot30_001wt.pdf} &
  \includegraphics[width=0.32\linewidth]{figures/bin_dist_rot45_001wt.pdf} \\
\end{tabular}

\begin{tabular}{>{\centering\arraybackslash}p{0.32\linewidth}
                >{\centering\arraybackslash}p{0.32\linewidth}
                >{\centering\arraybackslash}p{0.32\linewidth}}
  \makebox[0.32\linewidth][c]{%
    \begin{picture}(20,20)
      \put(-5,13){\color{black}\vector(1,0){20}}
    \end{picture}} &
  \makebox[0.32\linewidth][c]{%
    \begin{picture}(20,20)
      \put(-3,17){\color{black}\vector(2,-1){18}}
    \end{picture}} &
  \makebox[0.32\linewidth][c]{%
    \begin{picture}(20,20)
      \put(-1,19){\color{black}\vector(1,-1){14}}
    \end{picture}} \\
  $\vartheta_\nu = 0^\circ$ & $\vartheta_\nu = -30^\circ$ & $\vartheta_\nu = -45^\circ$
\end{tabular}
```

The `\vector(dx,dy){length}` arrow direction (e.g. `(1,0)`, `(2,-1)`, `(1,-1)`) encodes the antineutrino wind angle visually below each matrix.

## 3. Geometry diagram via `picture` primitives

The detector + axes + neutrino-wind diagram (segmented cube, prompt/delayed segments, 3D axes, capture-angle arc), built with raw `\picture` primitives. Requires `\usepackage{pict2e}` for the `\arc` macro.

```latex
\setlength{\unitlength}{.1\linewidth}
\begin{picture}(10,5)
  % grid of segments
  \multiput(5,0)(.5,0){9}{\color{black}\line(0,1){4}}
  \multiput(5,0)(0,0.5){9}{\color{black}\line(1,0){4}}

  % perspective extension lines
  \multiput(5,4)(.5,0){9}{\color{black}\line(1,1){1}}
  \multiput(9,0)(0,.5){9}{\color{black}\line(1,1){1}}
  \put(10,1){\line(0,1){4}}
  \put(6,5){\line(1,0){4}}

  % prompt + delayed segment markers (thick vertical bars)
  \thicklines
  \multiput(6.5,2.50)(.025,0){20}{\color{black}\line(0,1){0.5}}
  \multiput(6,1.50)(.025,0){20}{\color{gray}\line(0,1){0.5}}
  \thinlines

  \put(0.8,4.7){prompt segment}
  \put(0.8,3.9){delayed segment}

  % 3D axes
  \put(1,1){\vector(-1,-1){1}}    % z
  \put(1,1){\vector(0,1){2}}      % y
  \put(1,1){\vector(1,0){2}}      % x
  \put(0,0.3){$z$} \put(0.7,2.8){$y$} \put(2.8,.7){$x$}

  % neutrino direction + angle arc
  \put(1,1){\vector(2,1){2}}
  \put(1,1){\arc[0,26]{1}}
  \put(2.7,2){$\nu$}

  % capture angle within prompt-segment-local frame
  \put(6.75,-0.1){\color{black!90}\vector(0,1){4.7}}
  \put(4.8,2.75){\color{black!90}\vector(1,0){4.8}}
  \put(6.8,4.55){$y'$} \put(9.2,2.4){$x'$}
  \put(5.85,2.1){$\theta_n^i$}
  \put(6.75,2.75){\color{blue}\arc[0,245]{0.65}}
  \put(6.75,2.75){\color{blue}\vector(-1,-2){0.5}}

  % neutrino wind arrows
  \multiput(3.5,0.5)(0,1){4}{\color{black}\vector(2,1){1}}
  \put(2,0){neutrino wind}
  \put(2.2,1.2){$\vartheta_\nu$}
\end{picture}
```

Key macros: `\multiput(start)(step){count}{thing}` for repeated grid lines; `\vector(dx,dy){length}` for arrows; `\arc[startDeg,endDeg]{radius}` for circular arcs.

When porting to TikZ for the Neutrino 2026 poster (round 2), the same shape primitives map to `\node[...]`, `\draw[->]`, and TikZ's `arc` operation.
````

- [ ] **Step 2: Verify the file exists and is well-formed**

Run: `ls -la docs/figure-patterns.md && head -3 docs/figure-patterns.md`
Expected: file exists, ~5–6 KB, first three lines start with `# Figure inclusion patterns`.

---

## Task 2: Delete obsolete files

**Files:** 22 files + 1 directory deleted (no edits).

- [ ] **Step 1: Delete the old single-file build target and its 7 artifacts**

Run:
```bash
rm poster.tex poster.aux poster.log poster.nav poster.out poster.pdf poster.snm poster.toc
```
Expected: 8 files removed, no errors.

- [ ] **Step 2: Delete the pre-landscape backups**

Run:
```bash
rm poster.portrait.tex.bak poster.portrait.pdf.bak
```
Expected: 2 files removed.

- [ ] **Step 3: Delete current build artifacts (will regenerate next build)**

Run:
```bash
rm main.aux main.log main.nav main.out main.snm main.toc
```
Expected: 6 files removed. **Do NOT delete `main.pdf`** — it is the build output we want to keep until next build regenerates it.

- [ ] **Step 4: Delete TMP_RESOURCES candidates**

Run:
```bash
rm TMP_RESOURCES/poster_tmp.tex "TMP_RESOURCES/Neutrino Poster 2026.pdf"
```
Expected: 2 files removed. (Quote the filename with the space.)

- [ ] **Step 5: Delete the prior landscape-redesign spec + plan**

Run:
```bash
rm docs/superpowers/specs/2026-05-14-landscape-poster-redesign-design.md
rm docs/superpowers/plans/2026-05-14-landscape-poster-redesign.md
```
Expected: 2 files removed. (Note: `docs/superpowers/specs/` retains this plan's parent spec; the new plan you are reading right now stays in `docs/superpowers/plans/`.)

- [ ] **Step 6: Remove the now-empty `plans/` directory if applicable**

Run:
```bash
ls docs/superpowers/plans/ 2>/dev/null
```
If output shows ONLY this plan file (`2026-05-14-poster-docs-cleanup.md`), the dir is NOT empty — skip rmdir.
If output is empty, run: `rmdir docs/superpowers/plans` and expect success.

(Realistically the dir will still contain this plan file, so this step typically becomes a no-op. Document the check anyway.)

- [ ] **Step 7: Delete LLNL SVG sources (canonical asset is `figures/logos/llnl.pdf`)**

Run:
```bash
rm figures/logos/lawrence-livermore-national-laboratory-logo-vector.svg
rm figures/logos/llnl_cropped.svg
```
Expected: 2 files removed.

- [ ] **Step 8: Confirm deletion list**

Run:
```bash
ls poster.tex poster.aux poster.pdf poster.portrait.tex.bak \
   TMP_RESOURCES/poster_tmp.tex \
   "TMP_RESOURCES/Neutrino Poster 2026.pdf" \
   docs/superpowers/specs/2026-05-14-landscape-poster-redesign-design.md \
   docs/superpowers/plans/2026-05-14-landscape-poster-redesign.md \
   figures/logos/lawrence-livermore-national-laboratory-logo-vector.svg \
   figures/logos/llnl_cropped.svg 2>&1 | grep -c "No such"
```
Expected: `10` (every listed file should be missing).

---

## Task 3: Verify build still passes after deletion

**Files:** none modified; runs the build to confirm nothing load-bearing was deleted.

- [ ] **Step 1: First pdflatex pass**

Run:
```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```
Expected: EXIT 0; "Output written on main.pdf" near end of output; only the existing 5.5pt overfull warning + the long-line overfull hboxes in the footer minipage (these are unchanged from prior state).

- [ ] **Step 2: Second pdflatex pass (TikZ overlays need two passes)**

Run:
```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```
Expected: EXIT 0; same output. The footer + title-banner TikZ overlays now have `current page` resolved.

- [ ] **Step 3: Verify the PDF actually has the title banner and footer (proves both TikZ overlays rendered)**

Run:
```bash
pdftotext main.pdf - | grep -c "Selected refs"
pdftotext main.pdf - | grep -c "Enhancing Angular Sensitivity"
```
Expected: `1` and `1` respectively.

---

## Task 4: Update POSTER_CONTENT.md

**Files:**
- Modify: `POSTER_CONTENT.md` (block fold note ~line 47; §6 table ~lines 281–292; §7 table ~lines 303–314)

- [ ] **Step 1: Append Rosetta sentence to the block fold note**

Use Edit to append a sentence after the bulleted list at lines 41–46. Locate this block:

```markdown
- **⑤ HERO — δϑ vs n** ← §4 (Algorithm successes) + the soft-mention-only ML line from §5
- **Footer** ← refs + acks + LLNL-JRNL-2016175 + QR

---
```

Replace with:

```markdown
- **⑤ HERO — δϑ vs n** ← §4 (Algorithm successes) + the soft-mention-only ML line from §5
- **Footer** ← refs + acks + LLNL-JRNL-2016175 + QR

Block IDs ①–⑤ map 1:1 to `content/block1.tex`–`content/block5.tex`; the file convention is the operative one for source references, the ID convention is preserved here for editorial readability.

---
```

- [ ] **Step 2: Replace §6 (equations) table with dual-labeled version**

Locate the §6 table at lines ~283–292. Use Edit to replace this block:

```markdown
| ID | Where | LaTeX |
| -- | ----- | ----- |
| IBD | Block ① | `\bar\nu_e + {}^{1}\!H \to e^{+} + n` |
| $^{6}$Li capture | Block ③ | `{}^{6}\!\mathrm{Li}\,(n,\alpha)\,{}^{3}\!\mathrm{H},\ Q=4.78\text{ MeV}` |
| Chooz formula | Block ② | `\Delta\varphi = \arctan(P / l / \sqrt{N})` |
| Frobenius norm of difference | Block ④ | `\mathrm{FND}(\theta) = \lVert S_\theta - T\rVert_F = \sqrt{\sum_{ij}(S_\theta-T)_{ij}^2}` |
| Theoretical FND form | Block ④ | `\mathrm{FND}(\theta) \propto |\sin\tfrac{\theta-\vartheta_\nu}{2}|` |
| Reconstructed angle | Block ④ | `\hat\vartheta_\nu = \arg\min_\theta \mathrm{FND}(\theta)` |
| Circular mean resultant | Block ④ | `\bar R = |\lambda^{-1}\sum_i e^{i\vartheta_i}|` |
| Circular standard deviation | Block ④ | `\delta\vartheta = \sqrt{-2\ln\bar R}` |
```

with:

```markdown
| ID | Where | Block file | LaTeX |
| -- | ----- | ---------- | ----- |
| IBD | Block ① | `block1.tex` | `\bar\nu_e + {}^{1}\!H \to e^{+} + n` |
| $^{6}$Li capture | Block ③ | `block3.tex` | `{}^{6}\!\mathrm{Li}\,(n,\alpha)\,{}^{3}\!\mathrm{H},\ Q=4.78\text{ MeV}` |
| Chooz formula | Block ② | `block2.tex` | `\Delta\varphi = \arctan(P / l / \sqrt{N})` |
| Frobenius norm of difference | Block ④ | `block4.tex` | `\mathrm{FND}(\theta) = \lVert S_\theta - T\rVert_F = \sqrt{\sum_{ij}(S_\theta-T)_{ij}^2}` |
| Theoretical FND form | Block ④ | `block4.tex` | `\mathrm{FND}(\theta) \propto |\sin\tfrac{\theta-\vartheta_\nu}{2}|` |
| Reconstructed angle | Block ④ | `block4.tex` | `\hat\vartheta_\nu = \arg\min_\theta \mathrm{FND}(\theta)` |
| Circular mean resultant | Block ④ | `block4.tex` | `\bar R = |\lambda^{-1}\sum_i e^{i\vartheta_i}|` |
| Circular standard deviation | Block ④ | `block4.tex` | `\delta\vartheta = \sqrt{-2\ln\bar R}` |
```

- [ ] **Step 3: Replace §7 (figures) table with dual-labeled version**

Locate the §7 table at lines ~305–314. Use Edit to replace this block:

```markdown
| Panel | File | Source | Treatment |
| ----- | ---- | ------ | --------- |
| Block ① | `fig/RAT_PAC_IBD_run_6_5_crop.png` | Paper B Fig. 8 | Keep overlay annotations (positron annihilation, neutron capture, IBD vertex). |
| Block ② | `fig/angular_resolution_analytic_ylog_PackFactor_v2Useful.pdf` | Paper A Fig. 3 | Use as-is. Highlight one or two design curves only if room allows. |
| Block ③ | (TikZ, to be drawn round 2) | Paper B Fig. 4 analog | Custom rendering; do not import raster. |
| Block ④ | (TikZ, to be drawn round 2) | Paper B Fig. 11 | Show MC sets at three trial angles vs. one experimental set. |
| Block ③ | `fig/bin_dist_rot{0,30,45}_001wt.pdf` | Paper B Fig. 10 | Three matrices side by side with directional arrows below, mimicking `poster_tmp.tex`. |
| Block ④ | `fig/FND_plot.pdf` | Paper B Fig. 12 | Use as-is. |
| Block ⑤ (Hero) | `fig/parallel/06_money_plot_fit_arctan_log_4p.pdf` | Paper B Fig. 13 | Use as-is. Annotate the low-$n$ inflection and the crossover. |
| Footer | (to be generated) | preprint URL | Use `qrcode` package once URL is known. |
```

with:

```markdown
| Panel | Block | Asset | Source | Treatment |
| ----- | ----- | ----- | ------ | --------- |
| Block ① | `block1.tex` | `figures/RAT_PAC_IBD_run_6_5_crop.png` | Paper B Fig. 8 | Keep overlay annotations (positron annihilation, neutron capture, IBD vertex); see `docs/figure-patterns.md` §1. |
| Block ② | `block2.tex` | `figures/angular_resolution_analytic_ylog_PackFactor_v2Useful.pdf` | Paper A Fig. 3 | Use as-is. Highlight one or two design curves only if room allows. |
| Block ③ | `block3.tex` | (TikZ, to be drawn round 2) | Paper B Fig. 4 analog | Custom rendering; see `docs/figure-patterns.md` §3 for the picture-primitive geometry diagram pattern. |
| Block ④ | `block4.tex` | (TikZ, to be drawn round 2) | Paper B Fig. 11 | Show MC sets at three trial angles vs. one experimental set. |
| Block ③ | `block3.tex` | `figures/bin_dist_rot{0,30,45}_001wt.pdf` | Paper B Fig. 10 | Three matrices side by side with directional arrows below; see `docs/figure-patterns.md` §2. |
| Block ④ | `block4.tex` | `figures/FND_plot.pdf` | Paper B Fig. 12 | Use as-is. |
| Block ⑤ (Hero) | `block5.tex` | `figures/parallel/06_money_plot_fit_arctan_log_4p.pdf` | Paper B Fig. 13 | Use as-is. Annotate the low-$n$ inflection and the crossover. |
| Footer | `footer.tex` | (to be generated) | preprint URL | Use `qrcode` package once URL is known. |
```

- [ ] **Step 4: Update the logos paragraph immediately after the §7 table**

Locate this line (~line 317):

```markdown
Logos required: UH M$\bar{\text{a}}$noa (deep green, official), LLNL,
MTV Consortium. Drop into `fig/logos/`.
```

Replace with:

```markdown
Logos in place at `figures/logos/`:
- UH M$\bar{\text{a}}$noa: `university_of_hawaii_at_manoa_logo-freelogovectors.net_.png` (transparent PNG)
- LLNL: `llnl.pdf` (rendered from a cropped SVG; see CLAUDE.md "Logos workflow" for the regen pipeline)
- MTV: `MTV-logo-color.png` (re-encoded from upstream WebP)
```

- [ ] **Step 5: Verify POSTER_CONTENT.md edits**

Run:
```bash
grep -c "Block file" POSTER_CONTENT.md
grep -c "block1.tex\|block2.tex\|block3.tex\|block4.tex\|block5.tex" POSTER_CONTENT.md
```
Expected: first command returns `1` (only the §6 header). Second returns `>= 13` (each block file appears in §6 + §7 + Rosetta sentence).

---

## Task 5: Update CLAUDE.md drifted sections

**Files:**
- Modify: `CLAUDE.md` (sections: Build, Source-of-truth layout, Figure pipeline, Visual identity, Body layout)

- [ ] **Step 1: Light-edit "What this repository is" to acknowledge the modular structure**

Locate the second paragraph of this section:

```markdown
Not a git repository. Not code in the software sense — it is a typeset document plus an editorial spec.
```

Replace with:

```markdown
Not a git repository. Not code in the software sense — it is a typeset document plus an editorial spec. The source is split across `main.tex` (orchestrator), `config/_preamble.tex` (setup), and `content/` (per-block prose); see "Source-of-truth layout" below.
```

- [ ] **Step 2: Rewrite the "Build" section**

Locate the entire current "## Build" section through the line ending `kpsewhich beamerposter.sty` (lines 12–29 of current CLAUDE.md). Use Edit to replace with:

````markdown
## Build

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex   # run twice for TikZ overlays
# or
latexmk -pdf main.tex
```

`main.tex` is the only build target. The two-pass requirement is real: the title banner (green strip + gold underline) and footer strip are TikZ `[remember picture, overlay]` constructs that need a second pass to resolve `current page` references. A single-pass build silently produces a poster with no title banner and no footer.

Build artifacts (`main.{aux,log,nav,out,snm,toc}`) regenerate every build and can be deleted at any time without consequence; only `main.pdf` is the output.

Required TeX Live packages (Ubuntu, one-time install):

```bash
sudo apt install texlive-latex-base texlive-latex-extra \
                 texlive-fonts-recommended texlive-fonts-extra \
                 texlive-pictures texlive-science \
                 texlive-latex-recommended latexmk
```

Beamer + `beamerposter` + TikZ + `siunitx` + `mdframed` + `enumitem` are load-bearing — confirm with `kpsewhich beamerposter.sty` if a build fails on a fresh machine.

The LLNL logo is a PDF rendered from a cropped SVG. To re-render after editing the SVG (requires `librsvg2-bin` for `rsvg-convert`):

```bash
rsvg-convert -f pdf -o figures/logos/llnl.pdf figures/logos/llnl_cropped.svg
```

The cropping pipeline (auto-detect SVG content bbox, rewrite viewBox) is documented inline in the "Logos workflow" section below.
````

- [ ] **Step 3: Rewrite the "Source-of-truth layout" section**

Locate the entire current "## Source-of-truth layout" section through the bullet ending `Paper B's figures: Fig. 8, 10, 11, 12, 13).` (lines 31–41 of current CLAUDE.md). Use Edit to replace with:

````markdown
## Source-of-truth layout

The source is modular. Edits to one file frequently imply edits to its peers; the critical mappings are below.

```
main.tex                      build target; orchestration only —
                              frame, title banner overlay, body 3-col grid,
                              footer overlay. ~115 lines.
config/_preamble.tex          packages, palette, beamer theme + block templates,
                              \bodyheight, all macros (\placeholder, \titlelogo,
                              \highlight), block envs (heroblock, rblock),
                              \setlist[itemize] (with the required label= for
                              bullets to render), \sisetup. ~190 lines.
content/title.tex             title banner center column (paper title, subtitle,
                              author list, venue). Edit copy here.
content/footer.tex            footer strip refs + acks + QR placeholder.
content/block{1..5}.tex       per-block prose, top-to-bottom-per-column:
                              block1 = Col 1 top, block2 = Col 1 bot,
                              block3 = Col 2 top, block4 = Col 2 bot,
                              block5 = Col 3 hero. See "Body layout" below.
figures/logos/                title-banner logos (UH, LLNL, MTV).
figures/                      body figures (currently placeholders;
                              real assets enumerated in POSTER_CONTENT.md §7).
TMP_RESOURCES/                source papers only:
                              - Duvall et al. PRApplied 22 054030 (2024) [Paper A]
                              - Crow et al. in-prep [Paper B] — figure numbers
                                referenced from this file's tables.
                              - Conference Guidelines for poster preparation.
docs/                         design + plan archives, figure-patterns crib.
POSTER_CONTENT.md             editorial spec + presenter talking points.
                              §6 (equations) and §7 (figures) are
                              single-source-of-truth tables; update them in
                              the same edit when you change an equation or
                              figure. §9 lists collaboration-mandated language.
```

The `_preamble.tex` ↔ `main.tex` ↔ `content/blockN.tex` triangle is the operative one: structural changes go to `main.tex`, setup/style/macros go to `_preamble.tex`, prose goes to `content/`.

`POSTER_CONTENT.md` §6/§7 dual-label panels: the editorial `①…⑤` IDs and the source `block1.tex…block5.tex` filenames refer to the same panels. Use the file convention when navigating source; the ID convention when discussing the editorial spec.
````

- [ ] **Step 4: Rewrite the "Figure pipeline" section**

Locate the entire current "## Figure pipeline" section (line 43 onwards through the paragraph ending with the figure name list). Use Edit to replace with:

````markdown
## Figure pipeline

`figures/logos/` holds the three title-banner logos (UH PNG, LLNL PDF, MTV PNG) — wired via `\titlelogo` (defined in `config/_preamble.tex`).

`figures/` itself is the destination for body figure assets, which are currently TikZ `\placeholder{w}{h}{label}` stubs (macro defined in `config/_preamble.tex`). The intended real assets are enumerated in `POSTER_CONTENT.md` §7 (e.g. `figures/RAT_PAC_IBD_run_6_5_crop.png`, `figures/bin_dist_rot{0,30,45}_001wt.pdf`, `figures/FND_plot.pdf`, `figures/parallel/06_money_plot_fit_arctan_log_4p.pdf`).

When swapping a placeholder for a real asset, also drop the "Paper X Fig.~Y" attribution into the caption, and check `docs/figure-patterns.md` for reusable inclusion patterns (overpic annotation overlays, side-by-side tabular with arrow icons, picture-primitive geometry diagrams).
````

- [ ] **Step 5: Light-edit "Visual identity" — fix line-number reference**

Locate this line in the "Visual identity" section:

```markdown
Defined at `poster.tex:43–50`. Do not introduce new accent colors without changing all three together:
```

Replace with:

```markdown
Defined in `config/_preamble.tex` (palette block, search for `\definecolor{UHGreen}`). Do not introduce new accent colors without changing all three together:
```

Also update this paragraph at the end of the section:

```markdown
Font: `helvet` set as default sans (`\sfdefault`). Title banner is a TikZ overlay with a green strip (top 20% of page height) and a 6 mm gold underline — modify the rectangle coordinates as a pair (`16.8cm` / `17.4cm` in the title-banner TikZ block near the top of the document body). The hero block in the right column uses a separate `heroblock` environment with a 2 pt gold border (via `mdframed`) and a gold bar header (UH green text on UH gold).
```

Replace with:

```markdown
Font: `helvet` set as default sans (`\sfdefault`). Title banner is a TikZ overlay with a green strip (top 20% of page height) and a 6 mm gold underline — modify the rectangle coordinates as a pair (`16.8cm` / `17.4cm`) in the title-banner TikZ block near the top of `main.tex`. The hero block in the right column uses a separate `heroblock` environment (defined in `config/_preamble.tex`) with a 2 pt gold border (via `mdframed`) and a gold bar header (UH green text on UH gold). The hero's inner minipage is fixed-height at `\bodyheight - 2.5cm` so the gold border always spans the full column regardless of content.
```

- [ ] **Step 6: Light-edit "Body layout" — append block-file annotations**

Locate the bullet list in this section (lines 63–68 of current CLAUDE.md):

```markdown
- **Col 1 (top):** ① Motivation + IBD
- **Col 1 (bottom):** ② Conventional Chooz approach
- **Col 2 (top):** ③ Pattern-matching algorithm I — geometry + binning
- **Col 2 (bottom):** ④ Pattern-matching algorithm II — FND + circular statistics
- **Col 3 (full height):** ⑤ HERO — δϑ vs n (Paper B Fig. 13 + numerical takeaways + ML-baseline single-line mention)
- **Footer strip (full width, green):** refs, acks, LLNL-JRNL-2016175, QR
```

Replace with:

```markdown
- **Col 1 (top):** ① Motivation + IBD — `content/block1.tex`
- **Col 1 (bottom):** ② Conventional Chooz approach — `content/block2.tex`
- **Col 2 (top):** ③ Pattern-matching algorithm I — geometry + binning — `content/block3.tex`
- **Col 2 (bottom):** ④ Pattern-matching algorithm II — FND + circular statistics — `content/block4.tex`
- **Col 3 (full height):** ⑤ HERO — δϑ vs n (Paper B Fig. 13 + numerical takeaways + ML-baseline single-line mention) — `content/block5.tex`
- **Footer strip (full width, green):** refs, acks, LLNL-JRNL-2016175, QR — `content/footer.tex`
```

Also locate the trailing paragraph after the bullets:

```markdown
Block numbering is the editorial source-of-truth used in `POSTER_CONTENT.md §6` (equations) and `§7` (figures).
```

Replace with:

```markdown
Block file numbering (`block1`…`block5`) follows top-to-bottom-per-column. The editorial `①…⑤` IDs in `POSTER_CONTENT.md` §6/§7 map 1:1 to the block files; both conventions are valid, but use the file convention when editing source.
```

- [ ] **Step 7: Verify CLAUDE.md no longer references the old single-file world**

Run:
```bash
grep -nE "poster\.tex|fig/[^l]" CLAUDE.md
```
Expected: zero matches. (`fig/[^l]` excludes a possible `fig/logos/` we may have missed; if anything matches, audit and re-edit.)

---

## Task 6: Append two new sections to CLAUDE.md

**Files:**
- Modify: `CLAUDE.md` (append-only; new sections go at the end)

- [ ] **Step 1: Append "Logos workflow" section**

Append this block at the end of CLAUDE.md (after the "Language constraints" section):

````markdown

## Logos workflow

Three logos live in `figures/logos/`:

| Logo | File | Notes |
|------|------|-------|
| UH Mānoa seal | `university_of_hawaii_at_manoa_logo-freelogovectors.net_.png` | Transparent PNG, 640×480 |
| LLNL wordmark | `llnl.pdf` | Rendered from a cropped SVG via `rsvg-convert` |
| MTV consortium | `MTV-logo-color.png` | Re-encoded from upstream WebP via Pillow |

All three are wired into the title banner in `main.tex` via `\titlelogo{w}{h}{path}` (macro in `config/_preamble.tex`). The macro wraps each image in a fixed-size cream-backed (`BlockBG!50!white`) rounded box at `(w cm) × (h cm)`, with 0.4 cm inner padding and `keepaspectratio`. Cream backgrounds are required because most institutional logos ship with transparent backgrounds and would otherwise blend into the dark green title strip.

**LLNL re-render pipeline.** The upstream LLNL SVG had a 652×652 viewBox with content occupying only a narrow horizontal band (~6:1 aspect). Without cropping, the wordmark rendered as a tiny dot inside a large cream box. The crop pipeline:

```python
import subprocess
from PIL import Image

src = 'figures/logos/lawrence-livermore-national-laboratory-logo-vector.svg'
# 1) render SVG to high-res transparent PNG to find content bbox
subprocess.run(['rsvg-convert', '-f', 'png', '-w', '2400', '-o', '/tmp/llnl.png', src])
img = Image.open('/tmp/llnl.png').convert('RGBA')
bbox = img.getbbox()  # tight (left, upper, right, lower) of non-zero alpha
scale = 2400 / 652    # original viewBox is 652×652
# 2) compute new viewBox in original SVG units
vb = (bbox[0]/scale, bbox[1]/scale,
      (bbox[2]-bbox[0])/scale, (bbox[3]-bbox[1])/scale)
# 3) rewrite SVG with cropped viewBox
with open(src) as f: txt = f.read()
new = txt.replace('viewBox="0 0 652 652"',
                  f'viewBox="{vb[0]:.2f} {vb[1]:.2f} {vb[2]:.2f} {vb[3]:.2f}"')
with open('figures/logos/llnl_cropped.svg', 'w') as f: f.write(new)
# 4) render the cropped SVG to PDF for pdflatex
subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', 'figures/logos/llnl.pdf',
                'figures/logos/llnl_cropped.svg'])
```

If the upstream SVG ever changes, re-run this pipeline. The intermediate cropped SVG is not committed; only `llnl.pdf` is canonical.

To swap any logo for a different file, drop the new asset into `figures/logos/` and update the corresponding `\titlelogo{...}` call in `main.tex`. To reshape a slot (e.g. make MTV's box square instead of landscape), edit the `w` and `h` arguments to the `\titlelogo` call.
````

- [ ] **Step 2: Append "Silent-failure footguns" section**

Append this block at the end of CLAUDE.md (after the "Logos workflow" section just added):

````markdown

## Silent-failure footguns

Four traps in this beamer + beamerposter (scale=1.25) + helvet stack, all with silent failure modes (no warning, no error, just wrong output). All are mitigated in the current source; if you change related code, re-check.

1. **Uppercase Greek silently disappears.** `\Delta`, `\Phi`, `\Psi`, `\Gamma`, `\Lambda`, `\Sigma`, `\Omega`, `\Xi`, `\Pi` render as missing-glyph squares (■) under helvet+beamerposter. The OML font selected has empty uppercase-Greek slots. Mitigation: `config/_preamble.tex` contains `\let\OldDelta\Delta` + `\renewcommand{\Delta}{\mathnormal{\OldDelta}}`. **If any other uppercase Greek is added later, wrap it the same way** — `\mathnormal{}` reaches a working font; `\mathrm{}` and `\mathit{}` produce an acute accent; `\boldsymbol{}` also works. Lowercase Greek is unaffected.

2. **No bullets under enumitem.** Beamer-poster does not define `\labelitemi`, and enumitem reads it verbatim — without explicit `label=`, every `\begin{itemize}` renders with no bullet glyph. `\setbeamertemplate{itemize item}` is also ignored when enumitem owns the list. Mitigation: `config/_preamble.tex` sets `label=\color{UHGreen}\textbf{\textbullet}` directly on `\setlist[itemize]`. Same for sub-itemize via `\setlist[itemize,2]`.

3. **`columns` env absorbs hspace asymmetrically.** Wrapping body content in `\begin{columns}[T,totalwidth=\paperwidth]` with `\hspace{0.025\paperwidth}` between columns produces visibly larger left margin than right (trailing hspace gets gobbled). Mitigation: the body grid in `main.tex` uses raw `\noindent` + `\hspace*{}` (starred) + minipage chain, not the `columns` env. The starred form is required so leading spacers are not gobbled at the start of horizontal mode.

4. **TikZ `[remember picture, overlay]` requires two pdflatex passes.** The title banner and footer strip are TikZ overlays anchored to `current page.south/north`. With a single pass these don't render at all (the page-bound coords resolve to nothing) and the build looks "missing footer". Always run `pdflatex` twice (or use `latexmk -pdf main.tex`).

If you encounter a similar "wrong but no error" symptom in this template, suspect one of these first.
````

- [ ] **Step 3: Verify the new sections are present**

Run:
```bash
grep -c "## Logos workflow\|## Silent-failure footguns" CLAUDE.md
```
Expected: `2`.

Run:
```bash
grep -c "rsvg-convert\|labelitemi\|mathnormal" CLAUDE.md
```
Expected: `>= 3` (each appears at least once in the new sections).

---

## Task 7: Final verification

**Files:** none modified; aggregate sanity check.

- [ ] **Step 1: Final build sanity (CLAUDE.md/POSTER_CONTENT.md edits should not affect the PDF, but worth confirming)**

Run:
```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex && \
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```
Expected: both passes EXIT 0; `main.pdf` regenerated.

- [ ] **Step 2: Verify intended content present**

Run:
```bash
ls main.tex main.pdf config/_preamble.tex \
   content/title.tex content/footer.tex \
   content/block1.tex content/block2.tex content/block3.tex \
   content/block4.tex content/block5.tex \
   docs/figure-patterns.md \
   docs/superpowers/specs/2026-05-14-poster-docs-cleanup-design.md \
   docs/superpowers/plans/2026-05-14-poster-docs-cleanup.md \
   figures/logos/university_of_hawaii_at_manoa_logo-freelogovectors.net_.png \
   figures/logos/llnl.pdf \
   figures/logos/MTV-logo-color.png 2>&1 | grep -c "No such"
```
Expected: `0` (every listed file is present).

- [ ] **Step 3: Verify CLAUDE.md drift is resolved**

Run:
```bash
grep -nE "poster\.tex|^Defined at .poster\.tex" CLAUDE.md
```
Expected: zero matches.

- [ ] **Step 4: Verify POSTER_CONTENT.md tables have the new column**

Run:
```bash
grep -E "^\| ID \| Where \| Block file \| LaTeX \|" POSTER_CONTENT.md
grep -E "^\| Panel \| Block \| Asset \| Source \| Treatment \|" POSTER_CONTENT.md
```
Expected: each command returns exactly 1 matching line.

- [ ] **Step 5: Visual diff of the rendered PDF (no changes expected)**

Run:
```bash
pdftotext main.pdf - | wc -c
```
Expected: `5186` (matches the byte count from before this work — the textual content of the PDF should be byte-identical because no LaTeX source changed in a way that affects rendering).

- [ ] **Step 6: Final tree walk**

Run:
```bash
find . -maxdepth 3 -type f \( -name "*.tex" -o -name "*.md" -o -name "*.pdf" \) \
  -not -path "./TMP_RESOURCES/*" -not -path "./.claude/*" -not -path "./.superpowers/*" | sort
```
Expected output (exact):
```
./CLAUDE.md
./POSTER_CONTENT.md
./config/_preamble.tex
./content/block1.tex
./content/block2.tex
./content/block3.tex
./content/block4.tex
./content/block5.tex
./content/footer.tex
./content/title.tex
./docs/figure-patterns.md
./docs/superpowers/plans/2026-05-14-poster-docs-cleanup.md
./docs/superpowers/specs/2026-05-14-poster-docs-cleanup-design.md
./main.pdf
./main.tex
```

If the tree matches and Steps 1–5 passed, the cleanup is complete.

---

## Self-review notes

After writing this plan I checked:

- **Spec coverage:** Every section of the spec has at least one task. The "rescue figure patterns" requirement → Task 1. File deletion → Task 2. Verification of build → Task 3. POSTER_CONTENT.md updates → Task 4. CLAUDE.md drifted-section rewrites → Task 5. CLAUDE.md new sections → Task 6. End-to-end verification → Task 7.

- **Placeholder scan:** None. Every step shows the actual content to apply, not "edit appropriately" language. The exact `rm` commands, exact tables, exact CLAUDE.md prose are all inline.

- **Type/identifier consistency:** Block file names (`block1.tex`–`block5.tex`) used consistently across §6 table, §7 table, body layout bullets, and Rosetta sentence. The new POSTER_CONTENT.md §7 column name `Block` matches the §6 column name pattern. The logo file paths in CLAUDE.md "Logos workflow" match the actual filenames on disk.

- **Risk re-confirmation:** Task 3 (build verification after deletion) catches any over-aggressive deletion before doc updates begin. The new spec lives in `docs/superpowers/specs/` and this plan lives in `docs/superpowers/plans/` — neither is in the deletion list.
