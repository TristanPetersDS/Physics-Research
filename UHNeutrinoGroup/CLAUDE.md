# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Neutrino-directionality research for the University of Hawai'i at Mānoa neutrino group (Dr. John G. Learned). It has two coupled halves:

- **`neutrino-directionality/`** — the Python analysis/plotting engine that processes simulated RATPAC2 IBD (inverse beta decay) data and produces every physics figure.
- **`Nu2026/`** — the conference deliverables (Neutrino 2026 poster + Paper B). **`Nu2026/poster/` holds only the *figures*, logos, and planning docs — not the poster's LaTeX source.** The `poster.tex` / `config/_preamble.tex` / `content/blockN.tex` files described in `Nu2026/poster/docs/superpowers/` live in a separate (non-git) build directory; this repo is the data + figure + code side of that workflow.

The large `*.zip` and `vis_macros.tar.gz` files at the repo root are archived raw data / simulation bundles, not working files.

## The central workflow: updating poster plots

**"Updating the plots in the poster" = editing matplotlib styling in the analysis scripts, re-running them to regenerate PDFs, then copying those PDFs into `Nu2026/poster/fig/`.** There is no figure that the poster generates itself — they are all produced upstream by the Python code below and embedded by filename.

Figure → producing script:

| Poster figure | Produced by |
|---|---|
| `fig/parallel/06_money_plot_fit_arctan_log_4p.pdf` (the "money plot", detected events) | `neutrino-directionality/parallel/uncertainty_plot.py` |
| usable-events money plot | `neutrino-directionality/parallel/usable_uncertainty_plot.py` |
| `fig/parallel/sweet_spot.pdf` (ideal segment size) | `neutrino-directionality/parallel/sweet_spot_plot.py` (a copy also lives at `Nu2026/poster/fig/parallel/sweet_spot_plot.py`) |
| `fig/parallel/FND_n_*_dx_50.pdf` (FND-vs-angle panels) | `parallel/main.py` → `directionAlgorithm(plot=True, save=True)` |
| polar angle-distribution plots | `parallel/main.py` → `calcUncertainty(plot=True, save=True)` |
| `fig/bin_dist_*`, capture/cloud histograms, 2D/3D track plots | `neutrino-directionality/processor/main.py` |
| doped-vs-doped track-length histograms | `neutrino-directionality/processor/hist_doped.py` |

When asked to change labels/colors, edit the matplotlib calls in the relevant script and re-run it — do not hand-edit the PDFs.

## Plot styling conventions (read before changing labels/colors)

These are repeated across nearly every script and are what label/color edits touch:

- **LaTeX rendering is always on:** every script sets `plt.rc("font", family="serif", size=16)` (sweet_spot uses 18), `plt.rcParams["text.usetex"]=True`, and `mathtext.fontset="cm"` (Computer Modern). **This requires a working LaTeX install** (`pdflatex` + the usual math packages) or the scripts crash on `plt.show()`/`savefig`. To run without LaTeX, set `self.latex=False` (classes) or comment those three lines (standalone scripts).
- **Segment-size → color mapping** (in `uncertainty_plot.py`, `usable_uncertainty_plot.py`): `Δx = 5 mm → red ("r")`, `50 mm → green ("g")`, `150 mm → blue ("b")`. The poster's open TODO calls for a *colorblind-friendly palette* — changing this mapping consistently across both scripts is the likely intent of a "color settings" task.
- **Axis-label idiom:** angle is `$\vartheta$`, angular uncertainty is `$\delta\vartheta$ (${}^\circ$)`, segment size is `$\Delta x$ (mm)`, counts is `$n$`. Note the uppercase-Greek footgun documented for the poster (`\Delta` needs special handling under beamerposter) does **not** apply here — these are plain matplotlib mathtext.
- Scripts end with a literal `exit()` and call `plt.show()`; flip the `save` boolean at the top of a standalone script to write the PDF instead of only displaying it.

## Running the code

Dependencies (no requirements file exists): `numpy`, `scipy`, `matplotlib`, `pandas`, `tqdm`, `mpi4py`, plus a LaTeX toolchain for the usetex rendering. `mpi4py` additionally needs a system MPI (e.g. OpenMPI/MPICH providing `mpiexec`).

- **Parallel direction algorithm** (`parallel/main.py`):
  ```bash
  cd neutrino-directionality/parallel
  mpiexec -n 10 python3 main.py     # parallel over 10 cores
  python3 main.py                   # also runs single-core
  ```
  ⚠️ **`main.py` has no `if __name__ == "__main__"` driver** — it only defines the `ParallelProcessor` class. To actually run an analysis you must instantiate it and call methods at the bottom of the file, e.g.:
  ```python
  pp = ParallelProcessor(n=1000, dx=50, gs=9, cent=True, bd="data30")
  pp.calcUncertainty(iterations=300, vary="counts", center=True)
  ```
  The number of MPI ranks just slices the `[-180, 180)` angle search; results are identical regardless of `-n`.

- **Standalone plotting scripts** (`parallel/{uncertainty,usable_uncertainty,sweet_spot}_plot.py`, `processor/hist_doped.py`, `processor/3dplot.py`): plain `python3 <script>.py`. Each hardcodes its input data directory near the top (e.g. `uncertainty_plot.py` reads `data30/`, `usable_uncertainty_plot.py` reads `data32/`, `sweet_spot_plot.py` reads `data14/`).

- **Processor** (`processor/main.py`): the `DataProcessor` class reads RATPAC2 ASCII track files whose paths are hardcoded in `__init__` (currently absolute `/Users/...` paths — repoint these before running). Like the parallel code, you instantiate the class and call plotting methods.

There is no test suite, linter config, or build script — verification is visual inspection of the generated PDFs.

## Analysis architecture (parallel/main.py)

The direction algorithm is the scientific core. Data flow:

1. **Ingest:** `processData()` parses raw RATPAC2 ASCII (`truth.txt` positrons, `neutrons.txt`) into `events/fid_1M_unfiltered_{vertices,captures}.npy`. Run once; it's commented out of `__init__` by default.
2. **Load:** `readData()` loads the `.npy` files and computes `coords = captures − vertices` (capture position relative to the IBD vertex). It then derives two datasets used everywhere downstream:
   - **`detected`** — all events (includes the center segment).
   - **`usable`** — events with radius `r > seg_size/√2`, i.e. excluding the central segment (the "prompt" region a real detector can't resolve direction from). `center=True` selects `detected`; `center=False` selects `usable`.
3. **Single direction estimate** (`directionAlgorithm`): sample `2n` events, bin half into a `grid_size × grid_size` 2D histogram as the *reference*, rotate the other half through each integer angle in `[-180, 180)`, bin each rotation, and compute the **Frobenius Norm of the Difference (FND)** vs the reference. MPI splits the angle range across ranks (`np.array_split`) and `gather`s the norms on rank 0, which fits `abs_sine()` (an `|sin|`) to find the minimizing angle. Non-convergent fits are randomized to fairly represent directional uncertainty.
4. **Uncertainty** (`calcUncertainty`): repeats step 3 for `iterations` runs, wraps the resulting angles to `(-180, 180]`, and fits a **von Mises** distribution (`vonmises_circ_std_fit_method`, cross-checked by a manual mean-resultant-length calc) to get the circular standard deviation `σ` (the angular uncertainty) and its error `σ/√(valid iterations)`.
5. **Sampling discipline:** `sampleData()` uses a shuffle-without-replacement scheme (draw → move to buffer → refill from buffer when depleted) to minimize oversampling of the finite fiducial dataset.

`processor/main.py` (`DataProcessor`) is the pandas-based, single-process companion: it reads per-track ASCII into DataFrames and produces the descriptive figures (capture/cloud/track plots, binning colormaps) and the **Continuous FND (CFND)** analytic comparison — the closed-form integral that the discrete FND approximates (see `processor/history.txt` for the research narrative).

## Data directory conventions

- **`dataNN/` directories** (e.g. `data14`, `data30`, `data32`) are numbered analysis runs. `calcUncertainty` writes into the dir passed as the `bd=` constructor arg (`self.base_dir`).
- **`func_iter_dx_{seg}_{detected|usable}.txt`** — three whitespace-separated columns: `n`, `sigma_deg`, `sigma_err`. **Written in append mode (`"a"`)** — re-running `calcUncertainty` *adds* rows rather than overwriting, so a dir accumulates one row per run. The uncertainty plotters read these and, per a comment, drop the first row (its error bar is too large).
- **`func_iter_n_{n}.txt`** — same format but the first column is segment size `Δx` (used by `sweet_spot_plot.py`, which fits a cubic and reports the minimizing "ideal" segment size).
- **`data_iter_dx_{seg}_n_{n}.npy`** — the raw per-iteration angle array behind a given `(seg_size, n)` point.
- The `data30/33` (detected) and `data32/34` (usable) split: the lower-numbered dir is the paper dataset; the higher-numbered is a higher-statistics rerun, toggled by commented-out filename blocks at the top of the plotters.

## Poster figure regeneration loop

When regenerating a figure for the poster:
1. Edit the matplotlib styling in the producing script (table above), keeping the label/color conventions consistent across the detected **and** usable variants when they share a plot family.
2. Set the script's `save` flag (or pass `save=True`) and run it; confirm the PDF visually.
3. Copy the new PDF into `Nu2026/poster/fig/` (or `Nu2026/poster/fig/parallel/`) under the **exact existing filename** — the poster embeds figures by hardcoded name, so renaming silently breaks the poster build elsewhere.

The poster's own layout/build details (beamer + beamerposter, knob-driven layout, the uppercase-Greek/`\Delta` footgun, two-pass `pdflatex`) are documented in `Nu2026/poster/docs/superpowers/` and apply to that separate LaTeX source, not to anything in this repo.
