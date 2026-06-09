# 10M Dataset Wiring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Process the 16 GB `res_10M_001wt_ref_merged.tar.gz` into `events/fid_10M_unfiltered_{vertices,captures}.npy` via the canonical `ParallelProcessor` class, and validate the result against the existing 1M arrays.

**Architecture:** Make `ParallelProcessor.__init__` parameterizable (filenames + `process`/`load` flags, defaults preserve current behavior), fix `processData()`'s header handling so it works on this 1-header-line merged file and guarantees equal vertex/capture counts, add a numpy-only `validation.py`, and drive it all from a new `process_10M.py`. TDD the parser and the validation with tiny synthetic fixtures before touching the 16 GB data.

**Tech Stack:** Python 3.14 (existing `.venv`), numpy, mpi4py (single-process), stdlib `unittest`. No new dependencies.

**Spec:** `UHNeutrinoGroup/docs/superpowers/specs/2026-06-08-10M-dataset-wiring-design.md`

---

## Conventions used in every command

- **Venv python (absolute):** `/home/beefboi/Desktop/Research/Physics-Research/.venv/bin/python`
- **Work dir for code/tests:** `/home/beefboi/Desktop/Research/Physics-Research/UHNeutrinoGroup/neutrino-directionality/parallel`
- **Git branch:** `feat/10M-dataset-wiring` (already created and checked out; the repo root is `/home/beefboi/Desktop/Research/Physics-Research`).
- **Raw extraction dir:** `/home/beefboi/Desktop/Research/Physics-Research/10M_raw`
- **Tarball:** `/home/beefboi/Desktop/Research/Physics-Research/UHNeutrinoGroup/res_10M_001wt_ref_merged.tar.gz`

Run all `python`/`git` commands from the work dir above unless stated otherwise.

## File Structure

- **Modify** `neutrino-directionality/parallel/main.py`
  - `__init__`: add keyword args `positron_file`, `neutron_file`, `vertices_file`, `captures_file`, `process`, `load` (defaults reproduce today's behavior); gate `processData()`/`readData()` on the flags.
  - `processData()`: replace the `if i < 4` header skip with integer-`Instance` detection, and flush the final event's capture at EOF so `len(vertices) == len(captures)`.
- **Create** `neutrino-directionality/parallel/validation.py` — numpy-only `summarize()` + `format_table()`. One responsibility: compute/compare descriptive stats of a (vertices, captures) pair. No import of `main`, so it is import-light and trivially testable.
- **Create** `neutrino-directionality/parallel/process_10M.py` — the driver: instantiate `ParallelProcessor` on the extracted paths with `process=True, load=False`, then `summarize` 10M vs 1M and assert pass criteria.
- **Create** `neutrino-directionality/parallel/test_processdata.py` — `unittest` tests for the constructor overrides and the parser.
- **Create** `neutrino-directionality/parallel/test_validation.py` — `unittest` test for `summarize`.
- **Modify** repo-root `.gitignore` (`/home/beefboi/Desktop/Research/Physics-Research/.gitignore`) — ignore `fid_10M_unfiltered_*.npy` and `10M_raw/`.

---

### Task 1: Parameterize `__init__` (filenames + `process`/`load` flags)

**Files:**
- Modify: `neutrino-directionality/parallel/main.py:26` (signature), `:50-55` (filename attrs), `:76-81` (rank-0 process/load block)
- Test: `neutrino-directionality/parallel/test_processdata.py`

- [ ] **Step 1: Write the failing test**

Create `neutrino-directionality/parallel/test_processdata.py`:

```python
import os
import tempfile
import unittest

import numpy as np

from main import ParallelProcessor

TRUTH = """Row Instance trackPDG trackProcess evid mcx mcy mcz mcu mcv mcw mcpdg
0 0 -11 0 0 0.0 0.0 0.0 0 0 0 -11
0 1 22 1 0 0.5 0.0 0.0 0 0 0 22
1 0 -11 0 1 5.0 1.0 0.0 0 0 0 -11
"""

NEUTRONS = """Row Instance trackPDG trackPosX trackPosY trackPosZ trackTime trackMomX trackMomY trackMomZ trackKE trackProcess
0 0 2112 1.0 0.0 0.0 0 0 0 0 0.01 0
0 1 2112 2.0 0.0 0.0 0.1 0 0 0 0.005 1
0 2 2112 3.0 4.0 0.0 0.2 0 0 0 0.001 1
1 0 2112 10.0 0.0 0.0 0 0 0 0 0.01 0
1 1 2112 13.0 4.0 0.0 0.1 0 0 0 0.001 1
"""


class TestProcessData(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.truth = os.path.join(self.d, "truth.txt")
        self.neut = os.path.join(self.d, "neutrons.txt")
        self.vfile = os.path.join(self.d, "v.npy")
        self.cfile = os.path.join(self.d, "c.npy")
        with open(self.truth, "w") as f:
            f.write(TRUTH)
        with open(self.neut, "w") as f:
            f.write(NEUTRONS)

    def _make(self):
        return ParallelProcessor(
            n=10, dx=50, gs=9,
            positron_file=self.truth, neutron_file=self.neut,
            vertices_file=self.vfile, captures_file=self.cfile,
            process=False, load=False,
        )

    def test_constructor_accepts_overrides_without_loading(self):
        pp = self._make()
        self.assertEqual(pp.vertices_file, self.vfile)
        self.assertEqual(pp.positron_file, self.truth)
        self.assertFalse(hasattr(pp, "coords"))  # load=False => readData() not run


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /home/beefboi/Desktop/Research/Physics-Research/UHNeutrinoGroup/neutrino-directionality/parallel
/home/beefboi/Desktop/Research/Physics-Research/.venv/bin/python test_processdata.py -v
```
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'positron_file'`.

- [ ] **Step 3: Modify `__init__` signature**

In `main.py`, replace the signature (line 26):
```python
    def __init__(self, n=1000, dx=50, gs=9, cent=True, bd="data"):
```
with:
```python
    def __init__(self, n=1000, dx=50, gs=9, cent=True, bd="data",
                 positron_file="truth.txt", neutron_file="neutrons.txt",
                 vertices_file="events/fid_1M_unfiltered_vertices.npy",
                 captures_file="events/fid_1M_unfiltered_captures.npy",
                 process=False, load=True):
```

- [ ] **Step 4: Use the new args for the filename attributes**

In `main.py`, replace these lines (currently ~50-55):
```python
        # Filenames for ASCII output from RATPAC2 to be processed into unfiltered coordinates.
        self.positron_file = "truth.txt"
        self.neutron_file = "neutrons.txt"

        # Load in a 10M event fiducial dataset.
        self.vertices_file = "events/fid_1M_unfiltered_vertices.npy"
        self.captures_file = "events/fid_1M_unfiltered_captures.npy"
```
with:
```python
        # Filenames for ASCII output from RATPAC2 to be processed into unfiltered coordinates.
        self.positron_file = positron_file
        self.neutron_file = neutron_file

        # Processed numpy datasets (1M by default; override for the 10M run).
        self.vertices_file = vertices_file
        self.captures_file = captures_file
```

- [ ] **Step 5: Gate process/load on the flags**

In `main.py`, replace the rank-0 block (currently ~76-81):
```python
        if self.rank == 0:
            # This should only be run once to process the RATPAC2 output files. After that processData() produces and saves numpy files with the IBD vertices and neutron capture vertices that may be read by readData() and used by the program much more expediently.
            #self.processData()

            # This reads the data from the numpy data files produced by processData(). The must run successfully to perform analysis using this code.
            self.readData()            
```
with:
```python
        if self.rank == 0:
            # processData() turns the raw RATPAC2 ASCII into the numpy files;
            # readData() loads those numpy files for analysis. Both are now
            # flag-gated so a 10M processing run can skip the (not-yet-existing)
            # load step. Defaults (process=False, load=True) preserve prior behavior.
            if process:
                self.processData()
            if load:
                self.readData()
```

- [ ] **Step 6: Run test to verify it passes**

Run:
```bash
/home/beefboi/Desktop/Research/Physics-Research/.venv/bin/python test_processdata.py -v
```
Expected: PASS (`test_constructor_accepts_overrides_without_loading ... ok`).

- [ ] **Step 7: Commit**

```bash
cd /home/beefboi/Desktop/Research/Physics-Research
git add UHNeutrinoGroup/neutrino-directionality/parallel/main.py \
        UHNeutrinoGroup/neutrino-directionality/parallel/test_processdata.py
git commit -m "Parameterize ParallelProcessor.__init__ with filenames and process/load flags"
```

---

### Task 2: Fix `processData()` header detection + EOF flush

**Files:**
- Modify: `neutrino-directionality/parallel/main.py` (`processData`, positron loop ~117-131 and neutron loop ~147-170)
- Test: `neutrino-directionality/parallel/test_processdata.py`

- [ ] **Step 1: Write the failing test (add a method to the existing test class)**

Append this method to `class TestProcessData` in `test_processdata.py` (above the `if __name__` block):

```python
    def test_processdata_equal_counts_and_values(self):
        pp = self._make()
        pp.processData()
        v = np.load(self.vfile)
        c = np.load(self.cfile)
        # Header is a single line here; both files describe 2 events.
        self.assertEqual(len(v), 2, "expected 2 vertices")
        self.assertEqual(len(c), 2, "expected 2 captures")
        self.assertEqual(len(v), len(c), "vertex/capture counts must match")
        # vertices = mc{x,y,z} of each Instance==0 positron row
        np.testing.assert_allclose(v, [[0.0, 0.0, 0.0], [5.0, 1.0, 0.0]])
        # captures = last track step of each event (3,4,0) and (13,4,0)
        np.testing.assert_allclose(c, [[3.0, 4.0, 0.0], [13.0, 4.0, 0.0]])
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
/home/beefboi/Desktop/Research/Physics-Research/.venv/bin/python test_processdata.py -v
```
Expected: FAIL — the `if i < 4` skip drops the single-line-header file's first data rows, so `len(v)` is 0 and `len(c)` is 1 (assertions fail).

- [ ] **Step 3: Replace the positron parsing loop**

In `main.py` `processData()`, replace this block:
```python
            i = 0
            for line in f:
                if i < 4:
                    pass
                else:
                    try:
                        elems = line.split()
                        if elems[1] == "0":
                            mcx, mcy, mcz = float(elems[5]), float(elems[6]), float(elems[7])
                            self.vertices.append([mcx, mcy, mcz])
                    except Exception as err:
                        print(elems)
                        print(err)

                i += 1
```
with:
```python
            for line in f:
                elems = line.split()
                if len(elems) < 8:
                    continue
                # Skip header line(s): a data row's Instance column is an int.
                try:
                    instance = int(elems[1])
                except ValueError:
                    continue
                if instance == 0:
                    mcx, mcy, mcz = float(elems[5]), float(elems[6]), float(elems[7])
                    self.vertices.append([mcx, mcy, mcz])
```

- [ ] **Step 4: Replace the neutron parsing loop**

In `main.py` `processData()`, replace this block:
```python
            i = 0
            prev_line = ""
            for line in f:
                if i < 4:
                    pass
                else:
                    try:
                        elems = line.split()
                        if elems[1] == "0":
                            prev_elems = prev_line.split()
                            if len(prev_elems) > 0:
                                px, py, pz = float(prev_elems[3]), float(prev_elems[4]), float(prev_elems[5])
                                self.captures.append([px, py, pz])
                    except Exception as err:
                        prev_elems = prev_line.split()
                        px, py, pz = float(prev_elems[3]), float(prev_elems[4]), float(prev_elems[5])
                        self.captures.append([px, py, pz])

                        print(elems)
                        print(err)

                prev_line = line
                
                i += 1
```
with:
```python
            prev_data_line = None  # last seen DATA line (never a header)
            for line in f:
                elems = line.split()
                if len(elems) < 6:
                    continue
                # Skip header line(s): a data row's Instance column is an int.
                try:
                    instance = int(elems[1])
                except ValueError:
                    continue
                # A new event (Instance 0) means the PREVIOUS event just ended;
                # its last track step is the neutron capture location.
                if instance == 0 and prev_data_line is not None:
                    pe = prev_data_line.split()
                    px, py, pz = float(pe[3]), float(pe[4]), float(pe[5])
                    self.captures.append([px, py, pz])
                prev_data_line = line
            # Flush the final event (its last step is the last line of the file).
            if prev_data_line is not None:
                pe = prev_data_line.split()
                px, py, pz = float(pe[3]), float(pe[4]), float(pe[5])
                self.captures.append([px, py, pz])
```

- [ ] **Step 5: Run test to verify it passes**

Run:
```bash
/home/beefboi/Desktop/Research/Physics-Research/.venv/bin/python test_processdata.py -v
```
Expected: PASS for both `test_constructor_accepts_overrides_without_loading` and `test_processdata_equal_counts_and_values`.

- [ ] **Step 6: Commit**

```bash
cd /home/beefboi/Desktop/Research/Physics-Research
git add UHNeutrinoGroup/neutrino-directionality/parallel/main.py \
        UHNeutrinoGroup/neutrino-directionality/parallel/test_processdata.py
git commit -m "Fix processData header detection and flush final capture for equal counts"
```

---

### Task 3: Add `validation.py` (`summarize` + `format_table`)

**Files:**
- Create: `neutrino-directionality/parallel/validation.py`
- Test: `neutrino-directionality/parallel/test_validation.py`

- [ ] **Step 1: Write the failing test**

Create `neutrino-directionality/parallel/test_validation.py`:

```python
import unittest

import numpy as np

from validation import summarize


class TestSummarize(unittest.TestCase):
    def test_known_values(self):
        v = np.array([[0.0, 0.0, 0.0], [5.0, 1.0, 0.0]])
        c = np.array([[3.0, 4.0, 0.0], [13.0, 4.0, 0.0]])
        # coords = c - v = [[3,4,0],[8,3,0]]; norms = [5, sqrt(73)]
        s = summarize(v, c, seg_size=5)
        self.assertEqual(s["n_vertices"], 2)
        self.assertEqual(s["n_captures"], 2)
        self.assertTrue(s["counts_equal"])
        self.assertAlmostEqual(s["avg_track_length"], (5.0 + np.sqrt(73)) / 2, places=6)
        np.testing.assert_allclose(s["coords_mean"], [5.5, 3.5, 0.0])
        np.testing.assert_allclose(s["coords_std"], [2.5, 0.5, 0.0])
        # r = [5, 8.544]; R = 5/sqrt(2) = 3.535; both usable -> 1.0
        self.assertAlmostEqual(s["usable_fraction"], 1.0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
/home/beefboi/Desktop/Research/Physics-Research/.venv/bin/python test_validation.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'validation'`.

- [ ] **Step 3: Write `validation.py`**

Create `neutrino-directionality/parallel/validation.py`:

```python
"""Numpy-only descriptive-stats helpers for validating processed IBD datasets.

`summarize` reduces a (vertices, captures) pair to the handful of numbers we
compare between the 1M and 10M runs; `format_table` renders two summaries
side by side. No dependency on main.py / mpi4py.
"""

import numpy as np


def summarize(vertices, captures, seg_size=50):
    vertices = np.asarray(vertices, dtype=float)
    captures = np.asarray(captures, dtype=float)
    coords = captures - vertices
    norms = np.linalg.norm(coords, axis=1)
    r = np.hypot(coords[:, 0], coords[:, 1])
    R = seg_size / np.sqrt(2)
    return {
        "n_vertices": len(vertices),
        "n_captures": len(captures),
        "counts_equal": len(vertices) == len(captures),
        "avg_track_length": float(np.mean(norms)),
        "coords_mean": np.mean(coords, axis=0),
        "coords_std": np.std(coords, axis=0),
        "usable_fraction": float(np.mean(r > R)),
    }


def format_table(s1, s10):
    rows = []
    rows.append(f"{'metric':<24}{'1M':>16}{'10M':>16}")
    rows.append("-" * 56)
    rows.append(f"{'n_vertices':<24}{s1['n_vertices']:>16}{s10['n_vertices']:>16}")
    rows.append(f"{'n_captures':<24}{s1['n_captures']:>16}{s10['n_captures']:>16}")
    rows.append(f"{'counts_equal':<24}{str(s1['counts_equal']):>16}{str(s10['counts_equal']):>16}")
    rows.append(f"{'avg_track_length(mm)':<24}{s1['avg_track_length']:>16.4f}{s10['avg_track_length']:>16.4f}")
    for i, ax in enumerate("xyz"):
        rows.append(f"{'coords_mean_' + ax:<24}{s1['coords_mean'][i]:>16.4f}{s10['coords_mean'][i]:>16.4f}")
    for i, ax in enumerate("xyz"):
        rows.append(f"{'coords_std_' + ax:<24}{s1['coords_std'][i]:>16.4f}{s10['coords_std'][i]:>16.4f}")
    rows.append(f"{'usable_frac(dx=50)':<24}{s1['usable_fraction']:>16.4f}{s10['usable_fraction']:>16.4f}")
    return "\n".join(rows)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
/home/beefboi/Desktop/Research/Physics-Research/.venv/bin/python test_validation.py -v
```
Expected: PASS (`test_known_values ... ok`).

- [ ] **Step 5: Commit**

```bash
cd /home/beefboi/Desktop/Research/Physics-Research
git add UHNeutrinoGroup/neutrino-directionality/parallel/validation.py \
        UHNeutrinoGroup/neutrino-directionality/parallel/test_validation.py
git commit -m "Add numpy-only validation summary helpers"
```

---

### Task 4: Add the `process_10M.py` driver

**Files:**
- Create: `neutrino-directionality/parallel/process_10M.py`

(No unit test — this is glue over the tested `processData` and `summarize`. It is exercised end-to-end in Task 6.)

- [ ] **Step 1: Write the driver**

Create `neutrino-directionality/parallel/process_10M.py`:

```python
#!/usr/bin/env python3
"""Process the 10M merged RATPAC2 bundle into events/fid_10M_unfiltered_*.npy
and validate it against the existing 1M arrays.

Prereq: extract truth.txt and neutrons.txt into RAW (see the implementation
plan / spec). Run from neutrino-directionality/parallel with the repo .venv:
    /.../.venv/bin/python process_10M.py
"""

import os
import sys

import numpy as np

from main import ParallelProcessor
from validation import summarize, format_table

RAW = "/home/beefboi/Desktop/Research/Physics-Research/10M_raw"
V10 = "events/fid_10M_unfiltered_vertices.npy"
C10 = "events/fid_10M_unfiltered_captures.npy"
V1 = "events/fid_1M_unfiltered_vertices.npy"
C1 = "events/fid_1M_unfiltered_captures.npy"


def main():
    truth = os.path.join(RAW, "truth.txt")
    neutrons = os.path.join(RAW, "neutrons.txt")
    for p in (truth, neutrons):
        if not os.path.exists(p):
            sys.exit(f"ERROR: {p} not found. Extract the tarball first (see plan Task 6).")

    # process=True runs the parser; load=False skips readData (10M npy doesn't exist yet).
    ParallelProcessor(
        n=1000, dx=50, gs=9,
        positron_file=truth, neutron_file=neutrons,
        vertices_file=V10, captures_file=C10,
        process=True, load=False,
    )

    s10 = summarize(np.load(V10), np.load(C10), seg_size=50)
    s1 = summarize(np.load(V1), np.load(C1), seg_size=50)
    print(format_table(s1, s10))

    assert s10["counts_equal"], "10M vertex/capture counts differ"
    rel = abs(s10["avg_track_length"] - s1["avg_track_length"]) / s1["avg_track_length"]
    assert rel < 0.05, f"avg track length deviates {rel:.1%} from 1M (>5%)"
    print("\nVALIDATION PASSED")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-check that it imports and reports the missing-raw guard**

Run (before extraction, the raw files are absent, so the guard should fire):
```bash
/home/beefboi/Desktop/Research/Physics-Research/.venv/bin/python process_10M.py
```
Expected: prints `ERROR: /.../10M_raw/truth.txt not found. Extract the tarball first ...` and exits non-zero. (This confirms imports resolve and the guard works without needing the 16 GB data.)

- [ ] **Step 3: Commit**

```bash
cd /home/beefboi/Desktop/Research/Physics-Research
git add UHNeutrinoGroup/neutrino-directionality/parallel/process_10M.py
git commit -m "Add process_10M driver with validation against the 1M arrays"
```

---

### Task 5: Ignore the 10M artifacts in git

**Files:**
- Modify: `/home/beefboi/Desktop/Research/Physics-Research/.gitignore`

- [ ] **Step 1: Append ignore rules**

Append to the repo-root `.gitignore` (`/home/beefboi/Desktop/Research/Physics-Research/.gitignore`):

```gitignore

# --- Generated 10M analysis arrays (each ~240 MB, over GitHub's limit) ----
fid_10M_unfiltered_*.npy

# --- Extracted raw 10M ASCII (tens of GB; re-extractable from the tarball) -
10M_raw/
```

- [ ] **Step 2: Verify the rules match**

Run:
```bash
cd /home/beefboi/Desktop/Research/Physics-Research
git check-ignore -v \
  UHNeutrinoGroup/neutrino-directionality/parallel/events/fid_10M_unfiltered_vertices.npy \
  10M_raw
```
Expected: two lines showing `.gitignore:<n>:fid_10M_unfiltered_*.npy ...` and `.gitignore:<n>:10M_raw/ ...` (both matched/ignored).

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "Ignore generated 10M npy arrays and extracted raw ASCII"
```

---

### Task 6: Extract the raw ASCII and run the real 10M processing

**Files:** none committed here — outputs (`events/fid_10M_unfiltered_*.npy`) and `10M_raw/` are git-ignored.

> **Runtime note:** `processData()` parses the ~16 GB ASCII line-by-line in pure Python; expect this to take **many minutes** and use a few GB of RAM. Consider running Step 3 in the background.

- [ ] **Step 1: Extract `truth.txt` and `neutrons.txt`**

Run:
```bash
mkdir -p /home/beefboi/Desktop/Research/Physics-Research/10M_raw
tar -xzf /home/beefboi/Desktop/Research/Physics-Research/UHNeutrinoGroup/res_10M_001wt_ref_merged.tar.gz \
    -C /home/beefboi/Desktop/Research/Physics-Research/10M_raw truth.txt neutrons.txt
ls -la /home/beefboi/Desktop/Research/Physics-Research/10M_raw
```
Expected: `truth.txt` and `neutrons.txt` present (tens of GB total).

- [ ] **Step 2: Verify `truth.txt` format matches the parser's assumptions**

Run:
```bash
head -3 /home/beefboi/Desktop/Research/Physics-Research/10M_raw/truth.txt
awk 'NR==2{print NF" columns"; exit}' /home/beefboi/Desktop/Research/Physics-Research/10M_raw/truth.txt
```
Expected: a header line `Row Instance trackPDG trackProcess evid mcx mcy mcz ...`, then data rows where column 2 (`Instance`) is an integer and columns 6-8 (`mcx mcy mcz`) are the positron vertex. **If the column layout differs**, stop and adjust the positron index (`elems[5:8]`) in `processData()` before continuing.

- [ ] **Step 3: Run the driver**

Run from the work dir:
```bash
cd /home/beefboi/Desktop/Research/Physics-Research/UHNeutrinoGroup/neutrino-directionality/parallel
/home/beefboi/Desktop/Research/Physics-Research/.venv/bin/python process_10M.py
```
Expected (final lines):
- a side-by-side table of `1M` vs `10M` stats,
- `n_vertices == n_captures` for the 10M column, with both ≈ 10,000,000,
- `avg_track_length(mm)` within ~5% of the 1M value (~69.98),
- a final `VALIDATION PASSED`.

- [ ] **Step 4: Confirm the output arrays exist**

Run:
```bash
ls -la /home/beefboi/Desktop/Research/Physics-Research/UHNeutrinoGroup/neutrino-directionality/parallel/events/fid_10M_unfiltered_*.npy
```
Expected: two files, each ~240 MB.

- [ ] **Step 5: Confirm git stays clean of large artifacts**

Run:
```bash
cd /home/beefboi/Desktop/Research/Physics-Research
git status --short
```
Expected: no `fid_10M_unfiltered_*.npy` and no `10M_raw/` entries appear (they are ignored). Nothing to commit for this task.

---

## Self-Review

**Spec coverage:**
- §3 Environment (use existing venv) → Conventions section + all commands use the venv python. ✓
- §4 Extraction → Task 6 Step 1. ✓
- §5a Parameterize `__init__` → Task 1 Steps 3-4. ✓
- §5b process/load flags → Task 1 Step 5. ✓
- §5c Header fix + EOF flush → Task 2 Steps 3-4. ✓
- §6 Driver → Task 4. ✓
- §7 Validation (counts, avg track length, coords mean/std, usable fraction) → `summarize` (Task 3) + driver asserts (Task 4) + run (Task 6 Step 3). ✓
- §8 Risk: truth.txt format → Task 6 Step 2 verifies before the long run. ✓
- §9 git hygiene (npy + 10M_raw ignored) → Task 5. ✓
- §10 Acceptance criteria → Task 6 Steps 3-4 cover (2)-(4); criterion (1) already verified during brainstorming. ✓

**Placeholder scan:** No TBD/TODO; every code step shows complete code; every run step shows the exact command and expected result. ✓

**Type/name consistency:** `summarize` returns keys `n_vertices, n_captures, counts_equal, avg_track_length, coords_mean, coords_std, usable_fraction`; `format_table` and `process_10M.py` use exactly those keys. Constructor kwargs `positron_file/neutron_file/vertices_file/captures_file/process/load` are used identically in the test, driver, and `__init__`. File paths `V10/C10/V1/C1` match the names in Task 1's defaults and Task 5's ignore rule (`fid_10M_unfiltered_*.npy`). ✓

---

## Notes for the implementer

- The repo has no prior test framework; these `unittest` files run directly with the venv python and need no `pytest`.
- Do **not** modify `requirements.txt`, `setup.sh`, or the `.venv` — the environment is already set up and verified.
- `processData()`'s body sits under an `if (self.rank == 0) and self.debug_L1:` guard; keep that guard — only the two inner loops change.
- The 1M arrays and all existing scripts/figures must remain untouched.
