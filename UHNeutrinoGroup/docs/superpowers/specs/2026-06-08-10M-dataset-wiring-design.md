# Design: Wire the 10M dataset into the analysis pipeline

**Date:** 2026-06-08
**Status:** Draft (awaiting user review)
**Scope owner:** Tristan Peters / UH Mānoa neutrino group

## 1. Goal & scope

Turn the freshly-pulled 16 GB merged 10M-event RATPAC2 bundle into validated
NumPy arrays that the existing `parallel/main.py` analysis consumes, **using the
canonical `ParallelProcessor` class** (Approach B). Produce:

- `neutrino-directionality/parallel/events/fid_10M_unfiltered_vertices.npy`
- `neutrino-directionality/parallel/events/fid_10M_unfiltered_captures.npy`

and validate them against the existing 1M results.

**Explicitly out of scope (deferred to later sessions):**
- The Okabe-Ito colorblind-palette recolor of the plots.
- Running the `calcUncertainty` analysis campaign / regenerating any
  `func_iter_*` data or money-plot figures from the 10M set.

## 2. Inputs (verified)

- **Source archive:** `UHNeutrinoGroup/res_10M_001wt_ref_merged.tar.gz`
  (16,246,798,845 bytes, gzip integrity OK, git-ignored via `*_merged.tar.gz`).
- **Archive layout (flat):** `neutrons.txt`, `truth.txt`, plus four parse/merge
  shell scripts (`parsePositrons.sh`, `parseMCTruth.sh`, `parseNeutrons.sh`,
  `merge_parsed_files.sh`). Only `truth.txt` (positrons / IBD vertices) and
  `neutrons.txt` (neutron capture tracks) are needed.
- **`neutrons.txt` format (confirmed):** 12 whitespace-separated columns
  `Row Instance trackPDG trackPosX trackPosY trackPosZ trackTime trackMomX
  trackMomY trackMomZ trackKE trackProcess`, with a **single** header line.
  This matches what `processData()` expects (`elems[1]` = Instance,
  `elems[3:6]` = trackPos), **except** the header is 1 line, not the 4 the
  current code assumes (see §5).
- **`truth.txt` format:** per the `processData()` comment, positron rows are
  `Row Instance trackPDG trackProcess evid mcx mcy mcz mcu mcv mcw mcpdg`
  (`elems[1]` = Instance, `elems[5:8]` = `mc{x,y,z}`). **To be re-verified on
  first extraction** (header length + column positions) — see §8 risks.

## 3. Environment — already set up (no install)

The git repo root is `/home/beefboi/Desktop/Research/Physics-Research/` (the
parent of `UHNeutrinoGroup/`), and it already contains a working `.venv`,
`setup.sh`, and `requirements.txt` (commit `27dd6ae`). The venv is
**Python 3.14.4** with the full verified stack installed and importing:

    numpy 2.4.6  scipy 1.17.1  matplotlib 3.10.9  pandas 3.0.3  tqdm 4.68.1  mpi4py 4.1.2

(The earlier "scipy/mpi4py missing" reading came from the *system* `python3`;
the packages live in the venv.) OpenMPI 5.0.10 + `mpiexec` are present, so
`mpi4py` is fully functional. **Nothing to install or reconstruct** — just
activate the existing venv, and leave `requirements.txt`/`setup.sh` untouched:

```bash
source /home/beefboi/Desktop/Research/Physics-Research/.venv/bin/activate
```

## 4. Extraction

Extract both data files to a persistent parent-dir scratch (kept on disk for
reprocessing, per user choice):
```bash
mkdir -p /home/beefboi/Desktop/Research/Physics-Research/10M_raw
tar -xzf UHNeutrinoGroup/res_10M_001wt_ref_merged.tar.gz \
    -C /home/beefboi/Desktop/Research/Physics-Research/10M_raw truth.txt neutrons.txt
```
Uncompressed size is tens of GB; 412 GB is free. This dir is outside the repo,
so no `.gitignore` entry is needed for it.

## 5. Code changes — `neutrino-directionality/parallel/main.py`

Minimal and backward-compatible. Defaults preserve all current behavior.

### 5a. Parameterize `__init__`
Add optional keyword args, each defaulting to the current hardcoded 1M value:
- `positron_file="truth.txt"`
- `neutron_file="neutrons.txt"`
- `vertices_file="events/fid_1M_unfiltered_vertices.npy"`
- `captures_file="events/fid_1M_unfiltered_captures.npy"`

### 5b. Selectable process/load
Add flags `process=False`, `load=True`. In `__init__` (rank 0):
- `if process: self.processData()`
- `if load: self.readData()`

(Today `readData()` is hardwired and `processData()` is commented out; this
makes them selectable without editing the file per run, and lets us process the
10M set when the target `.npy` does not yet exist — `load=False`.)

### 5c. Fix the header / count bug in `processData()`
Replace the brittle `if i < 4: pass` line-skip (tuned to the original 1M files'
4-line header) with **robust header detection**: skip leading lines until the
first row whose `Instance` field (`elems[1]`) parses as an integer; never carry
a header line into `prev_line`. Additionally, **flush the final event's capture
at EOF** (the current code drops the last event because a capture is only
recorded when the *next* event's `Instance==0` line is seen).

Result: `len(vertices) == len(captures)` is guaranteed (otherwise
`coords = captures - vertices` raises), and the parser is correct for both the
original 1M files and this 1-header-line merged file. The physical extraction
rules are unchanged:
- **vertices:** for each positron row with `Instance==0`, take `mc{x,y,z}`.
- **captures:** at each new-event boundary, record the previous track step's
  `trackPos` (the neutron capture location); flush the last event at EOF.

## 6. Driver — `neutrino-directionality/parallel/process_10M.py` (new)

```python
pp = ParallelProcessor(
    n=1000, dx=50, gs=9,
    positron_file="/home/beefboi/Desktop/Research/Physics-Research/10M_raw/truth.txt",
    neutron_file ="/home/beefboi/Desktop/Research/Physics-Research/10M_raw/neutrons.txt",
    vertices_file="events/fid_10M_unfiltered_vertices.npy",
    captures_file="events/fid_10M_unfiltered_captures.npy",
    process=True, load=False,
)
validate_against_1M(pp)   # see §7
```
Run from `neutrino-directionality/parallel/` with the venv active:
`python3 process_10M.py` (single process; mpi4py works without `mpiexec`).
The 10M output names parallel the 1M names, so **nothing is clobbered**.

## 7. Validation against the 1M results

NumPy-only routine (in the driver) that loads the new 10M arrays and the
existing 1M arrays and prints a comparison table:

| Check | 10M expectation | 1M reference |
|---|---|---|
| `len(vertices) == len(captures)` | equal | equal (1,000,000) |
| event count | ≈ 10,000,000 (~10×) | 1,000,000 |
| avg neutron track length `mean(‖coords‖)` | ≈ 1M value | **69.98 mm** (sweet_spot constant) |
| coords mean per axis (x,y,z) | consistent with 1M | from `fid_1M_*` |
| coords std per axis | consistent with 1M | from `fid_1M_*` |
| usable fraction at Δx=50 (`r > 50/√2`) | consistent with 1M | from `fid_1M_*` |

`coords = captures − vertices`; `‖coords‖` via `np.linalg.norm(coords, axis=1)`;
usable fraction via `np.mean(np.hypot(coords[:,0], coords[:,1]) > 50/√2)`.

**Pass criteria:** counts equal and ≈10M, and the physics statistics
statistically consistent with the 1M baseline (avg track length within a few %
of 69.98 mm; means/stds same order and sign).

## 8. Risks & mitigations

- **`truth.txt` format differs from the comment** (header length / column
  order). *Mitigation:* robust header detection handles any header length;
  validation (equal counts, sane avg track length) catches column-order errors.
  Verify `head` of `truth.txt` on first extraction before the full run.
- **Pure-Python parse over a 16 GB file is slow** (line-by-line). *Mitigation:*
  acceptable for a one-time run; ASCII is kept on disk so re-runs skip
  re-extraction. (Vectorizing the parser is a possible later improvement, out of
  scope here.)
- **`readData()`'s usable-event loop is pure-Python** over all coords (10M
  iterations). *Mitigation:* validation uses a vectorized usable-fraction calc
  in the driver instead of relying on `readData`; we run the driver with
  `load=False`.

## 9. Artifacts & git hygiene

Repo root is `Physics-Research/`; `UHNeutrinoGroup/` is a subdirectory. The root
`.gitignore` already ignores `.venv/` and `*.zip` but **tracks `.tar.gz`
intentionally**, so:

- **Tracked (in repo):** `parallel/main.py` edits, `parallel/process_10M.py`,
  this spec. (`.venv`, `requirements.txt`, `setup.sh` already exist — untouched.)
- **Must be ignored:**
  - the 16 GB merged tarball — already handled by the nested
    `UHNeutrinoGroup/.gitignore` rule `*_merged.tar.gz` (overrides the
    track-`.tar.gz` default; confirmed ignored). *Optional tidy: consolidate
    this into the root `.gitignore` "Raw data archives" section and drop the
    nested file.*
  - `events/fid_10M_unfiltered_*.npy` — **each file ~240 MB** (10M×3×float64),
    far over GitHub's 100 MB limit → must be ignored (add a rule).
  - `10M_raw/` — the kept-on-disk extracted ASCII (tens of GB), at repo root →
    must be ignored (add a rule).
- The 16 GB tarball stays as the re-extractable archive.

## 10. Acceptance criteria

1. The existing `.venv` activates and `import scipy, matplotlib, tqdm, mpi4py`
   succeeds (already verified: scipy 1.17.1, matplotlib 3.10.9, mpi4py 4.1.2).
2. `process_10M.py` runs to completion and writes both
   `events/fid_10M_unfiltered_*.npy`.
3. Validation table prints with **equal** vertex/capture counts ≈ 10M and avg
   track length consistent with the 1M 69.98 mm.
4. The 1M arrays and all existing scripts/figures are untouched.
