# IBD Event-Display Rendering — Workflow, Insights & Roadmap

Vectorized (PDF/SVG) renders of the MTV inverse-beta-decay (IBD) simulation for the
Neutrino 2026 poster / Paper B, produced from RATPAC2 (Geant4 11.1.2).

**Status (2026-06-05):** the interactive vector-export pipeline is **confirmed working** end-to-end
(a real 30 MB vector PDF of an IBD event was produced). The next goal is a composited
"magnifying-lens" figure (see §7). Several alternative rendering routes are scoped but **not yet built** (§6).

---

## 0. TL;DR — the one path that works today

```bash
source ~/ratpac/env.sh
QT_QPA_PLATFORM=xcb rat -g ~/ratpac/ratpac/macros/mtv/vis_qt_mtv_colorblind.mac
```
Then, **in the Qt GUI command box** (bottom of the window), after the window is up:
```
/run/beamOn 1
/vis/viewer/zoomTo 20            # 40 m detector box → event is tiny; zoom in
/vis/ogl/set/exportFormat pdf
/vis/ogl/export ibd_event        # writes ibd_event_0000.pdf in the launch cwd
/vis/ogl/set/exportFormat svg
/vis/ogl/export ibd_event        # ibd_event_0000.svg
```
Output files land in the directory you launched `rat` from (we used `~/mtv_renders/`).
**The export MUST be done interactively, after `beamOn`, in the live window** — see §5 for why.

---

## 1. Environment

| Item | Value |
|---|---|
| RATPAC2 build | `/home/beefboi/ratpac/` (ratpac-setup superbuild: ROOT 6.36 + Geant4 11.1.2 + ratpac-two, all under `local/`) |
| ratpac-two source/build | `/home/beefboi/ratpac/ratpac/` (own git repo) |
| Environment setup | `source /home/beefboi/ratpac/env.sh` (sets `RATROOT`, `RATSHARE`, sources ROOT + Geant4) |
| `RATSHARE` | `/home/beefboi/ratpac/ratpac/install/share/RAT` |
| Geant4 | 11.1.2, built with `qt[yes]`, `opengl-x11[no]`; gl2ps compiled into `libG4OpenGL` |
| Registered vis drivers | `OGLSQt`, `OGLIQt`, `DAWNFILE`, `HepRepFile`, `VRML2FILE`, `RayTracer`, `ASCIITree` |
| Session | Wayland + XWayland (`DISPLAY=:0`). **Always launch Qt vis with `QT_QPA_PLATFORM=xcb`** (XWayland) — native Wayland gives a transparent window. |

> The analysis repo's `neutrino-directionality/CLAUDE.md` references stale `/Users/...` macOS paths — ignore those; the real build is above.

---

## 2. What is installed / created

### MTV geometry (from `UHNeutrinoGroup/mtv.tar.gz`, author "jack")
Installed into **both** runtime and source ratdb (so it survives rebuilds):
- `/home/beefboi/ratpac/ratpac/install/share/RAT/ratdb/mtv/` (runtime)
- `/home/beefboi/ratpac/ratpac/ratdb/mtv/` (source)

Contents:
- `mtv.geo` — a `world` (air, invisible) containing a `detector` box of **`Li6Doped_001wt`**
  (lithium-6 doped liquid scintillator), semi-transparent grey. **Both volumes are 20 m half-length
  (40 m box)** — a homogeneous simulation blob, not the segmented detector (segmentation is applied in
  software downstream). Selected via `experiment "mtv"` / `geo_file "mtv/mtv.geo"`.
- `MATERIALS_mtv.ratdb` — defines element `Lithium6`, materials `Li6Doped_001wt` / `Li6Doped_005wt`,
  and the `Li6Doped_001wt` OPTICS block (RINDEX/ABSLENGTH/RSLENGTH → Cerenkov optical photons are
  produced; **no SCINTILLATION property, so no scintillation photons**).

"MTV" is the project/collaboration name (the repo only had `MTV-logo-color.png`).

### Confirmed-working macros (DO NOT EDIT — reference/fallback)
- `/home/beefboi/ratpac/ratpac/macros/mtv/vis_qt_mtv_colorblind.mac` — colorblind `drawByParticleID`
  palette (e⁺ orange, neutron blue, γ yellow, optical photons faint), corrected vis setup.
- `/home/beefboi/ratpac/ratpac/macros/mtv/vis_qt_mtv.mac` — same, default colors.
- Both fixed vs the original tarball macros: use `/vis/drawVolume` (killed the `null scene pointer`
  errors), `endOfEventAction accumulate`, and leave `/run/beamOn` commented for interactive use.

### Confirmed render artifact
- `/home/beefboi/mtv_renders/test3._0000.pdf` — 30 MB, **genuine vector** (PDF 1.4, Producer Geant4,
  0 embedded raster, ~1.14 M line/move ops). Proof the pipeline works. The 30 MB is almost entirely
  optical-photon tracks (see §5).

### Experiments dir (for new work — keeps confirmed macros pristine)
- `/home/beefboi/ratpac/ratpac/macros/mtv/experiments/` — all experimental macros go here.
  - `headless_export_test.mac` — staged test: does a file-driver (HepRepFile) write an IBD event in
    batch without `-g`? (Not yet run — see §6/§9.)

---

## 3. How to make a vector render (interactive — the confirmed workflow)

1. `source ~/ratpac/env.sh`
2. `QT_QPA_PLATFORM=xcb rat -g ~/ratpac/ratpac/macros/mtv/vis_qt_mtv_colorblind.mac`
   (launch from the directory where you want output files, e.g. `cd ~/mtv_renders` first)
3. Wait ~10–15 s for ROOT/Geant4/physics to load; the Qt window opens showing the (empty) detector box.
4. In the GUI command box:
   - `/run/beamOn 1` → generates + draws one IBD event.
   - zoom/pan to frame it (40 m box ⇒ event is small): scroll wheel, or `/vis/viewer/zoomTo 20`.
   - export (see Appendix for the full styling cookbook):
     ```
     /vis/ogl/set/printSize 2000 2000
     /vis/ogl/set/exportFormat pdf
     /vis/ogl/export ibd_event           # → ibd_event_0000.pdf
     ```
5. gl2ps auto-numbers as `<name>_NNNN.<ext>`; each export increments. Vector formats: **pdf, svg, eps, ps**.

---

## 4. Quick styling cookbook (paste live; re-export without restarting)

```
# background
/vis/viewer/set/background white                 # or: black  (slide look)
# thicker, clearer tracks
/vis/modeling/trajectories/ColorBlind/default/setLineWidth 4
/vis/viewer/set/globalLineWidthScale 2
# HIDE optical photons but KEEP the physics (kills the 30 MB clutter):
/vis/filtering/trajectories/create/particleFilter pf
/vis/filtering/trajectories/pf/add opticalphoton
/vis/filtering/trajectories/pf/invert true
# mark vertices / capture points
/vis/modeling/trajectories/ColorBlind/default/setDrawStepPts true
/vis/modeling/trajectories/ColorBlind/default/setStepPtsSize 6
# detector appearance
/vis/viewer/set/style surface                    # or wireframe (see-through)
/vis/viewer/set/hiddenEdge true
# measured scale bar (baked into the render)
/vis/scene/add/scale 1 cm x 1 0 0 manual 0 0 0 cm
# alternative: drop optical photons at the source (faster events, must precede beamOn):
/process/inactivate G4CerenkovProcess
```

---

## 5. How it works + KEY INSIGHTS (read before re-attempting headless export)

These are hard-won; they save hours next session.

1. **Vector export = gl2ps inside `libG4OpenGL`.** Commands: `/vis/ogl/set/exportFormat {pdf|svg|eps|ps}`
   then `/vis/ogl/export <name>`. (`/vis/viewer/export` does **not** exist in this 11.1.2 build.)

2. **Trajectory export is interactive-only (architectural).** `OGLSQt` renders trajectories only into a
   *realized* Qt window. But `Rat.cc` (`Rat::Begin`, ~lines 159–172) runs the macro via
   `/control/execute` **before** `theSession->SessionStart()` realizes the window. So in any
   scripted/headless run the event is deferred ("1 event has been kept for refreshing…") and the export
   captures a **geometry-only, ~1 KB** file. Verified empty across: `xcb`+Xvfb, `softpipe`, and
   real-GPU `QT_QPA_PLATFORM=offscreen`. **Do not waste time retrying headless OGL export** — use the
   live GUI, or a file-driver route (§6).

3. **Headless software GL crashes** with `realloc(): invalid pointer` — Mesa's llvmpipe (system LLVM)
   clashes with the **bundled LLVM in `libtensorflow_framework.so.2`** (RATPAC built with TensorFlow).
   Workarounds: `GALLIUM_DRIVER=softpipe` (non-LLVM rasterizer) for headless GL, or use the **real GPU**
   (no llvmpipe → no clash). The confirmed render used the real GPU.

4. **Wayland transparency:** Qt-on-Wayland renders a see-through ("hole") window. Fix:
   `QT_QPA_PLATFORM=xcb` (force XWayland). Confirmed solid afterward.

5. **30 MB problem:** optical (Cerenkov) photons dominate the vector content (~1.14 M strokes). For
   posters, hide them (the `particleFilter` invert trick) or `/process/inactivate G4CerenkovProcess`.

6. **`omit_hadronic_processes 1.0`** (in the confirmed macros) suppresses neutron capture ⇒ **no
   triton/alpha**. The magnifier figure (§7) needs hadronic/neutron-capture **enabled**.

7. **File drivers write at end-of-event in batch** (HepRepFile/DAWNFILE/VRML2FILE) — so they should
   capture trajectories **without** a realized window. This is the basis of the headless routes in §6
   (test staged, not yet confirmed).

---

## 6. The four rendering routes (options to build)

| Route | Output | Headless? | Status | Setup |
|---|---|---|---|---|
| **A. OGL + gl2ps (live)** | vector pdf/svg/eps | No (interactive) | **Working** | none — §3 |
| **B. GeViewer** | vector svg/eps/ps/pdf + png | Generation yes; viewing GUI | Not built | `pip install geviewer`; read HepRep |
| **C. DAWN** | vector eps/pdf (line-art) | Yes | Not built | install `dawn`; `DAWNFILE` driver |
| **D. Blender** | photoreal raster | Yes (render) | Not built | export GDML/VRML; `blender` |

**A. OpenGL + gl2ps (live).** Confirmed. Best for quick iteration; interactive only.

**B. GeViewer — recommended next.** Lightweight Python/VTK viewer purpose-built for publication-quality
Geant4 visuals. Reads **HepRep** (preferred; per-component on/off toggles) or **VRML**. Exports **vector**
(SVG/EPS/PS/PDF/TEX) and raster (PNG) via its "Export Figure" button (custom dimensions), saves `.gev`
sessions, has a `gev-converter` CLI. Pipeline:
```
rat <macro with /vis/open HepRepFile ... /run/beamOn 1>   # writes G4Data0.heprep headlessly
geviewer G4Data0.heprep                                    # toggle components, Export Figure → PDF/SVG
```
Because the HepRep is written in batch (file driver), **trajectories are included even headless** —
this sidesteps the §5.2 constraint. Not yet installed (`pip install geviewer`; pulls PyVista/VTK; needs network).

**C. DAWN — "journal line-art."** `/vis/open DAWNFILE` writes a `.prim` (vector scene) headlessly; the
`dawn` binary renders it to vector EPS with hidden-line removal — the classic crisp technical-drawing look.
`dawn` is **not installed** (no apt package found; would need to build the Fukui Renderer). The `.prim`
can be generated now regardless.

**D. Blender — photoreal hero image.** Export geometry as **GDML** (`libGdml.so` is present) or **VRML**
(`VRML2FILE` driver) + an event's tracks, import into Blender for glass-scintillator / emissive-track
renders. Highest effort. Blender **not installed**.

---

## 7. Current figure goal — the "magnifying-lens" composite

**Concept:** a main image of the primary IBD vertex (e⁺ annihilation, γ emission, neutron scattering),
with an **inlaid circular "magnifier" pop-out** zoomed far in on the **⁶Li(n,t)α capture** (triton + alpha),
captioned with the **scale difference** (cm → µm, ×1000+). This visualizes the prompt→delayed→capture
chain across scales — directly on-message for the directionality method.

Breaks into three independent blocks:

**Block 1 — get the physics event (the real gotcha).**
- Use a **separate experimental macro** with **hadronic ON** (remove `omit_hadronic_processes`) so
  ⁶Li(n,t)α actually fires; triton ~2.7 MeV, alpha ~2.05 MeV, ranges ~tens of µm.
- **Fix the RNG seed** (`rat -s <N>`) so the same event renders at both zooms and regenerates on demand;
  scan a few seeds for a clean capture well-separated from the prompt vertex.

**Block 2 — render two panels of the same event.**
- Render **two camera framings** (don't just zoom one PDF — gl2ps tessellation is per-render): wide
  (vertex + annihilation + γ + neutron walk) and tight (the t+α star).
- Inset: strip to the story — hide optical photons + detector box (filters / GeViewer toggles).
- Add a **measured scale bar per panel** (`/vis/scene/add/scale 1 cm …` wide; `… 20 um …` inset).
- Palette incl. triton/alpha (the commented `PosterColors` block in the colorblind macro has triton green,
  alpha violet).

**Block 3 — composite the magnifier. VERDICT: TikZ, not GIMP.**
- Keep everything **vector**; assemble in **TikZ/LaTeX** (matches the poster, reproducible, crisp labels,
  exact lens geometry). Skip GIMP (it rasterizes the vector renders and isn't reproducible).
- Mechanics: `\clip … circle` the zoom image into a disk, ring it, draw two **tangent "cone" lines** back
  to a small source-circle on the wide image, add scale bars + "×N" caption. The TikZ **`spy` library**
  automates connector lines (rectangular; circular needs the manual tangents).
- Alternatives: **matplotlib** `zoomed_inset_axes`+`mark_inset` (matches the analysis figure pipeline, but
  rasterizes embedded images, circular inset needs a custom clip-path); **Inkscape** (vector GUI, one-off).

Skeleton (illustrative, not the final figure):
```latex
\begin{tikzpicture}
  \node[anchor=south west,inner sep=0](main){\includegraphics[width=12cm]{ibd_wide.pdf}};
  \coordinate (cap) at (7.3,4.1);                 % capture point on wide image
  \draw[white,thick] (cap) circle (0.3);
  \begin{scope}\clip (16,6) circle (2.6);
    \node at (16,6){\includegraphics[width=7cm]{ibd_capture_zoom.pdf}};\end{scope}
  \draw[line width=1.2pt] (16,6) circle (2.6);
  \draw[white] (cap) -- (tangentA);  \draw[white] (cap) -- (tangentB);
  \node at (16,3.2){$^{6}\mathrm{Li}(n,t)\alpha\;(\times\,2000)$};
\end{tikzpicture}
```

---

## 8. Roadmap / next steps (prioritized)

1. **Run the staged headless file-driver test** (`macros/mtv/experiments/headless_export_test.mac`):
   does `/vis/open HepRepFile` + `beamOn` write the event **without `-g`**? If yes, routes B/C/D are
   fully headless and reliable.
2. **Block 1:** seeded, hadronic-on capture macro in `experiments/`; confirm a clean ⁶Li(n,t)α event exists.
3. **Build GeViewer route** (`pip install geviewer`): HepRep export → view → vector Export Figure.
4. **Block 2:** wide + inset renders of the chosen seeded event (scale bars, clutter stripped).
5. **Block 3:** TikZ composite template wiring the two PDFs into the magnifier.
6. **Optional:** install `dawn` for the line-art variant; Blender for a hero image.

---

## 9. File map

| Path | What |
|---|---|
| `~/ratpac/env.sh` | environment setup |
| `~/ratpac/ratpac/macros/mtv/vis_qt_mtv*.mac` | confirmed vis macros (do not edit) |
| `~/ratpac/ratpac/macros/mtv/experiments/` | experimental macros |
| `~/ratpac/ratpac/{install/share/RAT,}/ratdb/mtv/` | MTV geometry + materials |
| `~/mtv_renders/test3._0000.pdf` | confirmed 30 MB vector render |
| `UHNeutrinoGroup/Nu2026/poster/docs/ibd-event-display-rendering.md` | this doc |
| `UHNeutrinoGroup/mtv.tar.gz` | original MTV geometry tarball |
| `UHNeutrinoGroup/{,Nu2026/}vis_macros.tar.gz` | original (pre-fix) vis macros |

---

## 10. Research & references

- GeViewer — publication-quality Python/VTK viewer for Geant4 (HepRep/VRML in; vector + PNG out):
  https://geviewer.readthedocs.io/ , https://pypi.org/project/geviewer/
- Geant4 Enhanced Trajectory Drawing (drawByParticleID/Charge, step points, line width):
  https://geant4.web.cern.ch/documentation/dev/bfad_html/ForApplicationDevelopers/Visualization/enhanceddrawing.html
- Geant4 DAWN tutorial (technical EPS line-art):
  https://conferences.fnal.gov/g4tutorial/g4cd/Documentation/Visualization/G4DAWNTutorial/G4DAWNTutorial.html
- Geant4 OpenGL tutorial:
  https://conferences.fnal.gov/g4tutorial/g4cd/Documentation/Visualization/G4OpenGLTutorial/G4OpenGLTutorial.html
- Visualization Drivers for Geant4 (driver overview, DAWN EPS): https://arxiv.org/pdf/0806.4887
- CERN — event displays in particle physics (visual language / inspiration):
  https://home.web.cern.ch/news/news/experiments/seeing-invisible-event-displays-particle-physics
- 3D Scientific Visualization with Blender (Brian R. Kent): https://www.cv.nrao.edu/~bkent/blender/tutorials.html
- Trajectory line width (forum): https://geant4-forum.web.cern.ch/t/modify-line-width/3551

---

## 11. Macro hygiene (user request)

The confirmed-working macros (`macros/mtv/vis_qt_mtv*.mac`) are the reference/fallback and must stay
**untouched**. All experimentation happens in `macros/mtv/experiments/`.
