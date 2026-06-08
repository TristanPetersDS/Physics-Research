# Physics-Research

Personal research repository for my PhD work with the **University of Hawai‘i at
Mānoa neutrino-directionality group** (Dr. John G. Learned). It collects the
analysis code, simulated data, generated figures, and conference deliverables for
measuring the **angular sensitivity / directionality of small segmented
antineutrino detectors** via inverse beta decay (IBD) in RATPAC2 simulations.

> ⚠️ Personal/working repository — not a published or shared package. Paths,
> entry points, and data layouts reflect an active research workflow.

## What's inside

```
UHNeutrinoGroup/
├── neutrino-directionality/      # The analysis + plotting engine (Python)
│   ├── parallel/                 # MPI direction-reconstruction algorithm + plot scripts
│   │   ├── events/               # .npy event data (vertices / captures)
│   │   └── data14 … data34/      # per-run uncertainty outputs
│   └── processor/                # RATPAC2 ASCII track parser + histogram / 3D plots
├── Nu2026/                       # Conference deliverables for Neutrino 2026
│   ├── B_A_new_method…/          # Paper B: data, figures, code, references
│   │   ├── REFERENCES/           # External talks (IAEA 2025, RATPAC2 School)
│   │   └── simulation_data/      # Doped-detector simulation bundles (.tar.gz)
│   └── poster/                   # Neutrino 2026 poster figures, logos, planning docs
└── CLAUDE.md                     # Detailed dev notes (figure→script map, run instructions)
```

### The two halves
- **`neutrino-directionality/`** — the engine. Processes simulated RATPAC2 IBD
  data and produces every physics figure: the "money plot" (detected events vs.
  angle), the sweet-spot / ideal-segment-size plot, FND-vs-angle panels, polar
  angle distributions, and capture / track histograms.
- **`Nu2026/`** — the deliverables. The Neutrino 2026 poster figures and Paper B.
  These hold the **figures + data + producing code, not the poster's LaTeX
  source** (which lives in a separate build directory outside this repo).

## Current state
- ✅ SSH auth + GitHub remote configured (`origin` → `Physics-Research`).
- 🟢 Active: Neutrino 2026 poster + Paper B figure production. Open task —
  migrate plots to a colorblind-friendly palette (the segment-size → color
  mapping, currently 5 mm = red, 50 mm = green, 150 mm = blue).
- 📦 Tracked data: `.npy` event arrays and `.tar.gz` simulation bundles are kept
  in-repo for reproducibility.
- 🚫 Not tracked: large `*.zip` raw-data bundles, the `REFERENCES/` library of
  external papers/theses (copyright + size — kept local only), LaTeX build
  artifacts, and machine-local `.claude/settings.local.json` (see `.gitignore`).

## Setup
```bash
./setup.sh          # creates .venv, installs requirements.txt, verifies imports
./setup.sh --system # install into the current Python env instead of a venv
```
The script also **checks the two dependencies pip cannot provide**: a system MPI
(`mpiexec`, required to build `mpi4py`) and a LaTeX toolchain (`pdflatex`, since
the plot scripts set `text.usetex=True`). It prints the Arch `pacman` commands if
either is missing — it does not install them for you.

Python stack (see `requirements.txt`): `numpy`, `scipy`, `matplotlib`, `pandas`,
`tqdm`, `mpi4py`. Verified-working on Python 3.14.3 with Open MPI 5.0.10 and
TeX Live 2026.

## Running the code

**Parallel direction algorithm**
```bash
cd UHNeutrinoGroup/neutrino-directionality/parallel
mpiexec -n 10 python3 main.py     # parallel over 10 ranks
python3 main.py                   # single core
```
> `main.py` defines the `ParallelProcessor` class but has **no `__main__`
> driver** — instantiate it and call methods at the bottom of the file (examples
> in `CLAUDE.md`). The number of MPI ranks only slices the angle search; results
> are identical regardless of `-n`.

**Standalone plot scripts** (each hardcodes its input `dataNN/` dir near the top)
```bash
python3 parallel/uncertainty_plot.py        # money plot
python3 parallel/sweet_spot_plot.py         # ideal segment size
python3 processor/hist_doped.py             # doped track-length histograms
```

See **`UHNeutrinoGroup/CLAUDE.md`** for the full figure→script map and per-script
data-directory details.

## Event-display rendering (Neutrino 2026)

Vectorized (PDF/SVG) renders of the RATPAC2 **MTV inverse-beta-decay** simulation
for the poster / Paper B. The workflow, the four rendering routes
(OpenGL + gl2ps, GeViewer, DAWN, Blender), the hard-won setup insights, and the
planned **"magnifying-lens" composite figure** are documented in:

**`UHNeutrinoGroup/Nu2026/poster/docs/ibd-event-display-rendering.md`**

> Renders come from a local RATPAC2 build (Geant4 11.1.2), not this repo's Python
> engine. Launch the Qt viewer with `QT_QPA_PLATFORM=xcb` (XWayland), `beamOn`,
> then `/vis/ogl/export` — see the doc for why headless export doesn't capture
> trajectories. Confirmed-working vis macros live with that build under `macros/mtv/`.
