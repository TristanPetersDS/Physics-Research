# Documentation refresh + project cleanup — design

**Date:** 2026-05-14
**Status:** Approved (pending user review of this written spec)
**Predecessor:** `2026-05-14-landscape-poster-redesign-design.md` (slated for deletion as part of this work)

## Context

The Neutrino 2026 poster project went through three rounds of structural change in a short window:

1. Single-file `poster.tex` → debugged six rendering bugs (bullets, `\Delta`, footer clipping, hero fill, margin asymmetry, column gaps).
2. Single-file → modular split: `main.tex` orchestrator + `config/_preamble.tex` + `content/{title,footer,block1..5}.tex` + `figures/logos/`.
3. Logo workflow: `\titlelogo` macro + WebP→PNG re-encoding + LLNL SVG → cropped SVG → PDF pipeline.

The repo carries debt from each transition:

- **CLAUDE.md** still describes the single-file world (`poster.tex` paths, `fig/` directory, inline `\placeholder` macro at "poster.tex:93"). None of this is true now.
- **POSTER_CONTENT.md** §6/§7 use the `①…⑤` panel-ID convention; the operative source convention is `block1.tex…block5.tex` (top-to-bottom-per-column).
- **Filesystem** holds `poster.tex` and its build artifacts, two `.bak` files from the pre-landscape-redesign era, an old REVTeX two-column draft, the original LLNL SVG and its cropped intermediate, and the previous brainstorming session's design+plan docs.

This spec captures the design for refreshing the docs and cleaning the filesystem in one pass.

## Scope

**In scope:**
- Rewrite the drifted sections of CLAUDE.md (Build, Source-of-truth layout, Figure pipeline, Visual identity, Body layout).
- Add two new CLAUDE.md sections: Logos workflow and Silent-failure footguns.
- Dual-label POSTER_CONTENT.md §6/§7 with a new `File` column.
- Extract figure-inclusion patterns from `TMP_RESOURCES/poster_tmp.tex` into `docs/figure-patterns.md` before deleting the source.
- Delete obsolete files (full list under "File deletion" below).
- Verify build still passes after deletions.

**Out of scope:**
- Editing block prose in `content/blockN.tex` (separate concern).
- Adding new functionality (no Makefile, no build script — keep manual `pdflatex main.tex × 2`).
- Restructuring directory layout.
- Reformatting the visual design.

## Design

### Approach: hybrid rewrite

CLAUDE.md's section outline is well-organized; what drifted is the *content* of those sections, not their structure. Approach: keep the outline, rewrite the drifted section bodies, append two new sections at the end. This preserves the document's voice and the user's existing mental model while bringing it back to truth.

### CLAUDE.md changes (section-by-section)

| Section | Action | Rationale |
|---|---|---|
| What this repository is | Light edit — note modular structure | Stable framing, minor drift |
| Build | **Rewrite** — `main.tex`, two-pass requirement, LLNL SVG re-render command, "build artifacts are regenerable" footnote | `poster.tex` doesn't exist; SVG workflow is new |
| Source-of-truth layout | **Full rewrite** — describe `main.tex` orchestrator, `config/_preamble.tex` setup, `content/` prose split, `figures/logos/` assets, `TMP_RESOURCES/` for source papers only | Most outdated section |
| Figure pipeline | **Rewrite** — `figures/` (not `fig/`), logos in place, body figures still placeholders | Wrong dir, wrong status |
| Visual identity | Light edit — line numbers point to `config/_preamble.tex` | Drift |
| Body layout | Light edit — append `(block1.tex)`…`(block5.tex)` next to each ①…⑤ entry | Dual-label per agreed convention |
| Language constraints | **Untouched** — stable collaboration policy | No drift |

**New sections (appended):**

- **Logos workflow.** Explains `\titlelogo{w}{h}{path}` macro (cream-backed rounded box wrapping `\includegraphics`). Lists the three logos with paths. Documents the LLNL SVG → cropped SVG → PDF pipeline (Python crop snippet inline, reproducible). Notes the rsvg-convert install requirement.

- **Silent-failure footguns.** Promotes the four traps from `memory/beamer_poster_gotchas.md` so they're visible without memory loaded. The four:
  1. Uppercase Greek silently disappears under helvet+beamerposter (need `\mathnormal{}`).
  2. `\labelitemi` undefined under beamerposter — enumitem needs `label=` set on the list.
  3. `columns` env absorbs trailing/leading hspace asymmetrically — use raw minipages + `\hspace*{}`.
  4. TikZ `[remember picture, overlay]` requires a second pdflatex pass.

### POSTER_CONTENT.md changes

- **§6 (equations table)** — add `File` column listing the corresponding `blockN.tex`.
- **§7 (figures table)** — same treatment; add `File` column.
- **Block fold note (~lines 38–46)** — append a one-line Rosetta sentence: "Block IDs ①–⑤ map 1:1 to `content/block1.tex`–`content/block5.tex`."
- **Everything else** — untouched (talking points, quantitative claims, Q&A, language conventions are stable).

### figure-patterns.md (new)

A small markdown crib at `docs/figure-patterns.md` extracting the three reusable figure-inclusion patterns from `poster_tmp.tex`:
1. Overpic-style annotation overlay on a raster figure.
2. Tabular layout of binning matrices side-by-side.
3. Geometry TikZ diagram (segmented cube + axes + neutrino wind arrow).

Each pattern: ~10-line LaTeX snippet + 1-sentence "use when…" description. This preserves the only practically-useful content from `poster_tmp.tex` before the file is deleted.

### File deletion

**Definite (unambiguous, no policy):**
- `poster.tex` — old single-file build target
- `poster.{aux,log,nav,out,pdf,snm,toc}` — its 7 build artifacts
- `poster.portrait.tex.bak`, `poster.portrait.pdf.bak` — pre-landscape backups
- `main.{aux,log,nav,out,snm,toc}` — current build artifacts (will regenerate next build)

**Borderline (user-confirmed for deletion):**
- `TMP_RESOURCES/poster_tmp.tex` — *after* extracting patterns to `docs/figure-patterns.md`
- `TMP_RESOURCES/Neutrino Poster 2026.pdf`
- `docs/superpowers/specs/2026-05-14-landscape-poster-redesign-design.md`
- `docs/superpowers/plans/2026-05-14-landscape-poster-redesign.md`
- `figures/logos/lawrence-livermore-national-laboratory-logo-vector.svg`
- `figures/logos/llnl_cropped.svg`

**Empty-dir cleanup after deletion:**
- `docs/superpowers/plans/` becomes empty after the landscape-redesign plan is deleted → remove the dir.
- `docs/superpowers/specs/` retains this new spec → keep the dir.
- `docs/superpowers/` retains the `specs/` subdir → keep.
- `docs/` retains `superpowers/` and the new `figure-patterns.md` → keep.

End state under `docs/`: `docs/figure-patterns.md` + `docs/superpowers/specs/2026-05-14-poster-docs-cleanup-design.md`.

## Order of execution

1. **Extract figure patterns** from `poster_tmp.tex` into `docs/figure-patterns.md`.
2. **Delete files** per the list above.
3. **Build verification:** `pdflatex main.tex` × 2 — confirm no deleted file was load-bearing for the build.
4. **POSTER_CONTENT.md update** — dual-label tables, append Rosetta sentence.
5. **CLAUDE.md update** — apply the section-by-section table, append new sections.
6. **Final build verification** (sanity check: no markdown edits should affect the PDF, but worth confirming).

## Verification / acceptance criteria

- `main.tex` builds clean (no new warnings beyond the existing 5.5pt overfull from col 2 natural-content).
- `pdftotext main.pdf` byte-identical to current state — no visual changes from this work.
- CLAUDE.md contains zero references to `poster.tex` or `fig/` (paths from the old single-file world).
- CLAUDE.md mentions all four silent-failure footguns by name.
- POSTER_CONTENT.md §6/§7 tables have a `File` column populated correctly for all 5 blocks.
- `docs/figure-patterns.md` exists with the 3 patterns extracted.
- No file in the deletion list remains on disk.
- `figures/logos/` contains exactly: UH PNG, MTV PNG, llnl.pdf.
- `TMP_RESOURCES/` retains only: the two source papers and the conference Guidelines PDF.

## Risk

- **Build break from over-aggressive deletion.** Mitigation: the build verification step (#3) catches this immediately, and all deleted items are independently confirmed not load-bearing (none are `\input{}`'d, none are `\includegraphics`'d).
- **Loss of `poster_tmp.tex` reference content.** Mitigation: figure-patterns.md extraction step (#1) preserves the practically-useful content before deletion.
- **Spec lives inside the directory we're cleaning.** Mitigation: deletion step explicitly enumerates the older landscape-redesign-* files, never globs the directory.
- **No git safety net.** Project isn't a git repo. Mitigation: deletions are confined to files explicitly user-confirmed; if anything goes wrong, only this spec session's work is at risk.

## Out-of-scope follow-ups (noted, not done here)

- `.gitignore` for build artifacts — relevant only if/when the project becomes a git repo.
- Makefile or build script encoding the two-pass + SVG conversion steps — could simplify CLAUDE.md's Build section.
- Migration of POSTER_CONTENT.md §6/§7 to single-convention (block-file-only) — current dual-label is a transitional state.
