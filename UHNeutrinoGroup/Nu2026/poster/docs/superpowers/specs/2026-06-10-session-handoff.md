# Poster — Session Handoff & Current State (2026-06-10)

Read this + `CLAUDE.md` to continue work in a fresh chat. This file is the session log;
CLAUDE.md is the canonical reference (its "Current state" header has a 2026-06-10 update
block, and the "Logos workflow" section was rewritten this session). Previous handoff:
`2026-05-31-session-handoff.md` (its path is stale — see below).

## Build command

```bash
cd /home/beefboi/Desktop/Research/Physics-Research/UHNeutrinoGroup/Nu2026/poster
latexmk -pdf -interaction=nonstopmode poster.tex
```

- **The path above is the current one.** The 05-31 handoff's `~/Desktop/Research/Nu2026/poster`
  is stale; the poster now lives inside the git repo (`Physics-Research`), and the `.tex`
  source IS git-tracked (since commit `3ef364f`).
- **In-place builds require the `nu2026_poster -> .` self-symlink** in the poster dir
  (gitignored; recreate with `ln -sfn . nu2026_poster`). Without it the footer QR
  `\includegraphics{nu2026_poster/content/ArXiV_QR_code.png}` fails the build.
- ⚠️ **cwd footgun (bit me this session):** if you run `latexmk -pdf poster.tex` from the
  repo root, kpathsea resolves a SYSTEM `poster.tex` (`texmf-dist/.../poster-mac/poster.tex`)
  — it "succeeds" doing nothing useful and dumps `poster.{aux,log,fls,fdb_latexmk}` junk
  into the repo root. Always `cd` into the poster dir first (bash cwd persists across tool
  calls, and earlier `cd`-to-repo-root commands linger).

Inspect regions at scale: `pdftoppm -png -r 120 poster.pdf /tmp/p` → page is 5760×4320 px
at 120 dpi (px/cm = 47.24). Useful crop offsets at 120 dpi: body top y≈860; col 1 x≈60,
col 2 x≈1970, col 3 (hero) x≈3850; banner = `-crop 2880x420+0+0` at 60 dpi.

## What was done this session (all complete, built, visually verified)

1. **Banner logos → circular + vector** (`poster.tex`, `config/_preamble.tex`):
   - New macro `\titlelogocirc{d}{w}{path}` (preamble): tight white disc, diameter `d` cm,
     image at `w` cm. `w` is separate so square marks inscribe without poking past the rim
     (square mark: keep `w ≲ 0.65·d`; circular artwork can run `w ≈ d − 0.6`).
   - Logos are **absolutely positioned as nodes inside the banner TikZ overlay**
     (anchored to `current page.north west/east`, centered in the 16.8 cm strip). The
     `columns` wings in the title row are now empty placeholders that only preserve title
     width. Flow-based placement made the discs overhang the gold underline — don't go back.
   - Calls: UH `{14}{13.3}{figures/logos/uh_seal_vector}`,
     LLNL `{7}{4.6}{figures/logos/llnl_icon_black}`,
     MTV `{7}{6.4}{figures/logos/MTV-logo-color}`.
   - **UH seal**: true vector, Ghostscript-cropped out of the official lockup PDF
     (`~/Downloads/university-of-hawaii-at-manoa-logo.pdf`, seal bbox `1.4 242.8 265.5 507.4` pt).
   - **LLNL black circular no-text mark**: user said don't hunt external assets — it was
     **constructed** from the two "LL" icon paths (the only elements with x<120) in
     `figures/logos/lawrence-livermore-national-laboratory-logo-vector.svg`, recolored
     `#000`, viewBox tight-cropped, `rsvg-convert`ed to `llnl_icon_black.pdf`.
   - **MTV**: still raster (2250 px ≈ 800+ dpi at Ø6.4 cm — print-safe). Vector swap is
     an open nice-to-have.

2. **Block 2 rework** (`content/block2.tex`):
   - ψ-geometry `picture` diagram REMOVED (old source survives in git history and
     `block2.tex.bak-overflow`).
   - Added a four-detector geometry gallery matching Fig 2's "3D" legend group:
     Double Chooz / Checker-3D / NuLat5 / SANTA, `height=6.5cm`, `[b]`-aligned minipages
     (widths 0.17/0.26/0.25/0.27) so the name labels share a baseline; one shared caption
     (Fig 3). Assets staged per repo convention as `fig/detector_dc.pdf` (tight-cropped
     from `figures/dc_geo_plain_white_gray.eps` — the GRAY variant matches the others; the
     plain one is blue) and `fig/detector_{checker3d,nulat5,santa}.png` (trimmed copies of
     `figures/checkerboard-3d_full_geo_scale.png`, `figures/nulat_geo_scale.png`,
     `figures/santa_plain_axes.png`).
   - Fig 2 (Chooz angular-resolution plot) enlarged `0.40 → 0.47\linewidth`; caption sits
     in the plot's minipage. Fixed lingering "intial" typo.

3. **Block 4 rework** (`content/block4.tex`):
   - Bullets → numbered **5-step algorithm** (Paper B's steps). `enumerate` needs the new
     `\setlist[enumerate,1]{label=\color{UHGreen}\textbf{\arabic*.},...}` in the preamble —
     same "no marker without explicit label=" footgun as itemize.
   - Step 4 carries the paper's boxed L² norm (renders as eq. (2)):
     `L^2_i(\vartheta) = \sqrt{\sum_{k,j} (x_{kj})_i^2}`, `(x_{kj})_i ∈ [DifferenceSet_i](ϑ)`.
   - The two `picture` diagrams now render at matched heights: panel (a) unitlength
     `0.087\linewidth` in a 0.55 minipage; panel (b) had ~40% dead margin baked into its
     `(10,4)` box — its picture box was tightened to `(6.7,4.3)(2.3,-0.1)` (crop via the
     optional `\begin{picture}(w,h)(x0,y0)` offset args), unitlength `0.133\linewidth` in a
     0.42 minipage. (a)/(b) sublabels + shared caption (Fig 5).

4. **Design-audit fixes** (blocks 1/3/5):
   - block 1: restored `\vfill` above/below the fixed-size 1:1 figure (had been lost in an
     Overleaf round-trip); figure+caption now share a centered 0.62 minipage. The 1:1
     figure itself is untouched (absolute `17.405cm × 7.653cm` — never resize).
   - block 3: RAT-PAC render enlarged + centered (overpic at 0.81 of a 0.62 minipage
     ≈ 0.50 block width); the top overpic call-out boxes extend ABOVE the image, so keep
     the `\vspace{0.5cm}` clearance below the bullets. Caption trimmed — my first version
     overflowed the bottom border (see insight below).
   - block 5: Fig 6 caption moved into the money-plot minipage (Layout A otherwise
     untouched — it's the user's deliberate reconstruction, see memory).

5. **Docs synced**: CLAUDE.md (current-state block, logos workflow rewrite, QR-symlink
   note, `\postermargin` now 0.75 cm with derived values shifted), figure-style-guide.md
   changelog (four dated 2026-06-10 entries). Memory files updated
   (`poster-overleaf-roundtrip`, `poster-worktree-state`).

## Git state at session end (NOTHING COMMITTED — user hasn't asked)

Modified: `.gitignore` (symlink ignore rule), poster `CLAUDE.md`, `config/_preamble.tex`,
`content/block{1..5}.tex`, `poster.tex`, `docs/figure-style-guide.md`.
Untracked new assets that BELONG IN the next commit: `fig/detector_dc.pdf`,
`fig/detector_{checker3d,nulat5,santa}.png`, `figures/logos/llnl_icon_black.{svg,pdf}`,
`figures/logos/uh_seal_vector.pdf`. (`poster.pdf` is a build product;
`docs/vector-export-crash-brief.md` and `parallel/data_10M_detected/` predate this
session — they belong to the MTV-render and 10M-dataset threads, branch
`feat/10M-dataset-wiring`.) Note the preamble/block2/block5 diffs also contain the
user's pre-session edits (`\strut` ribbon fix, M 1.5→0.75, block-5 Layout A) — the
working tree is a mix; don't assume every hunk is from 2026-06-10.

## Overleaf sync (pending, user-driven)

Push all seven changed `.tex`/`CLAUDE.md`-adjacent files AND upload the new assets:
`figures/logos/uh_seal_vector.pdf`, `figures/logos/llnl_icon_black.pdf` (+`.svg` if
wanted), the four `fig/detector_*` files, plus `fig/parallel/sweet_spot_final.pdf` from
the 06-05 session. Without the assets the Overleaf build errors on missing graphics.
Commit locally BEFORE unpacking any Overleaf zip (see `poster-overleaf-roundtrip` memory).

## Insights / gotchas from this session

- **Caption-width budget math:** a caption moved from full block width (~76 chars/line)
  into a 0.5-width minipage doubles its line count — block 3's caption silently overflowed
  the bottom border this way (footgun-#5 style: no warning). When minipage-aligning a
  caption, re-budget the block: rblock inner height ≈ 28.96 cm at current knobs.
- **`picture` envs crop like viewBoxes:** `\begin{picture}(w,h)(x0,y0)` offset args crop
  dead margin without touching any drawing coordinates — the right fix for mismatched
  diagram scales (block 4 panel b).
- **gs crop recipe** (used for UH seal + DC detector; pdfcrop is NOT installed):
  `gs -o out.pdf -sDEVICE=pdfwrite -dDEVICEWIDTHPOINTS=W -dDEVICEHEIGHTPOINTS=H
  -dFIXEDMEDIA -c "<</PageOffset [-x0 -y0]>> setpagedevice" -f in.pdf`.
  The `-sDEVICE=bbox` device is useless when the file paints a white background rect
  (reports the full page) — find the content bbox by rendering to PNG and scanning
  non-white pixels with PIL instead.
- **Logo SVG surgery:** institutional wordmark SVGs often contain the icon as separable
  paths; filter elements by coordinate range, recolor via the CSS classes, re-fetch bbox,
  rewrite viewBox (CLAUDE.md documents the original LLNL variant of this pipeline).
- The two remaining **overfull `\hbox`es are pre-existing** (footer QR `2.75\linewidth`
  hack ≈ 72 pt; 4 pt in the title row). Don't chase them as regressions.

## Remaining TODO (carried + new)

- `LLNL-POST-XXXXXX` placeholder in `content/footer.tex` — replace before submission.
- **Palette regeneration** (figure-style-guide §1a, Okabe-Ito Option B): money plot +
  sweet-spot are DONE (see `okabe-ito-plot-recolor` memory); the block-2 Chooz plot and
  block-5 FND panels still carry old colors and need their generators re-run.
- MTV logo vector replacement (optional; raster is print-safe).
- Footer cleanup (negative-`\hspace` reference columns, QR width hack) — cosmetic.
- block-5 `\fbox` boxes (Key findings / Future work) are plain black-rule boxes; restyling
  to the UHGold/`mdframed` family was considered and deliberately deferred (user owns
  block 5's Layout A).
- Content finalization per the to-do header in `poster.tex` (text + placement sign-off
  per block).
- Conference-guideline gaps (deliberate so far): serif/sans mix, pure-white background,
  sub-28 pt text inside figures (block-1 1:1 figure, Fig 6 18 pt side legend).

## Verification done

`latexmk` exits clean (0 errors; only the 2 pre-existing overfull hboxes). Full page +
every block visually inspected at 120 dpi after each change; block 3's first-pass caption
overflow caught and fixed this way. Banner discs verified inside the green strip with the
gold underline clear. QR code confirmed rendering (symlink works). Stray root-level
`poster.*` artifacts from the cwd footgun were deleted.
