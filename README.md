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
- 🚫 Not tracked: large `*.zip` raw-data bundles (see `.gitignore`) and
  machine-local `.claude/settings.local.json`.

## Running the code
No `requirements.txt` exists yet. Dependencies: `numpy`, `scipy`, `matplotlib`,
`pandas`, `tqdm`, `mpi4py` — plus a **LaTeX toolchain** (the plotting scripts set
`text.usetex=True`) and a **system MPI** (OpenMPI/MPICH) for `mpi4py`.

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
