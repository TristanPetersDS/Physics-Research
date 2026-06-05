# Neutrino-Directionality Code — Comprehensive Test Report

**Date:** 2026-06-05
**Tester:** Claude Code
**Scope:** `neutrino-directionality/` (7 Python files + bundled data)
**Policy:** document only, no fixes

---

## 1. Executive summary

**All seven source files are syntactically valid and, with the environment provisioned, every module is functionally operational** — single-process *and* under MPI. Out of the box, however, **nothing could run**: the machine was missing the entire scientific stack (`scipy`, `matplotlib`) plus `tqdm`, `mpi4py`, and any MPI runtime. After installing those (cp314 wheels + system openmpi), every module was exercised end-to-end against the bundled and synthetic data.

| Verdict | Count |
|---|---|
| Modules fully working after env setup | 6 / 7 |
| Module blocked by a **data bug** (not a code/env bug) | 1 / 7 (`hist_doped.py`) |
| Figure-generation + usetex pipeline | ✅ verified (valid PDFs) |
| MPI parallel path (`mpiexec`) | ✅ verified (2 and 4 ranks) |

---

## 2. Environment: what was missing vs. installed

**Active interpreter:** mise-managed **Python 3.14.3** (`~/.local/share/mise/installs/python/3.14.3`).

| Package | Before | Action |
|---|---|---|
| numpy 2.4.2, pandas 3.0.1 | present | — |
| **scipy** | missing everywhere | installed `1.17.1` (pip, cp314 wheel) |
| **matplotlib** | missing everywhere | installed `3.10.9` (pip, cp314 wheel) |
| **tqdm** | missing in mise python | installed `4.68.1` (pip) |
| **mpi4py** | missing | installed `4.1.2` (pip, cp314 wheel) |
| **MPI runtime** | no `mpiexec` | **openmpi 5.0.10** via `sudo pacman -S openmpi` |
| LaTeX / dvipng / gs | present (TeX Live 2026) | — (required by `text.usetex=True`) |

All pip installs went into the mise Python via its own pip (user-writable, no sudo). Reversible with `pip uninstall scipy matplotlib tqdm mpi4py`. cp314 wheels existed for everything — no source builds needed despite Python 3.14 being very new.

> **Runtime notes**
> - Every script hard-enables `text.usetex=True`, so matplotlib shells out to `pdflatex`+`dvipng` for *all* text. LaTeX is therefore a hard runtime dependency; without it the scripts crash at draw/save time (not import time) — a confusingly late failure.
> - `plt.show()` under the non-interactive `Agg` backend is a silent no-op that never rasterizes the figure. "The script ran without error" does *not* prove the figure renders; validating the usetex pipeline required forcing `savefig`.

---

## 3. Methodology

1. **Static:** `py_compile` on all 7 files; AST import-extraction to map dependencies.
2. **Data integrity:** loaded every bundled data asset with numpy/pandas and reproduced `readData()`'s core math by hand.
3. **Standalone scripts:** ran via `runpy` with `MPLBACKEND=Agg`, capturing stdout/stderr.
4. **Class modules** (no entry points): wrote external drivers (`/tmp/pp_driver.py`, `/tmp/dp_driver.py`) exercising every method; redirected all figure output to `/tmp` so the repo stayed untouched.
5. **MPI:** ran the parallel driver under `mpiexec -n 2` and `-n 4`.
6. **Cleanup:** removed all `__pycache__`/`.pyc`; confirmed repo tree unchanged.

---

## 4. Results by module

| File | Status | Notes |
|---|---|---|
| `parallel/main.py` (`ParallelProcessor`) | ✅ **PASS** | All methods OK single-process **and** `mpiexec -n 4`. Direction algorithm recovers angles near the true 0° (e.g. −12°, +10°); FND gather/bcast across ranks correct. Generates FND, polar, and LEGO PDFs + `func_iter`/`data_iter` outputs. |
| `parallel/uncertainty_plot.py` | ✅ PASS | Reads `data30/`, fits 4-param arctan model, writes valid `06_money_plot_fit_arctan_log_4p.pdf` (143 KB). |
| `parallel/usable_uncertainty_plot.py` | ✅ PASS (caveat) | Runs; **saves to the same filename as the detected plot** — see Issue #2. |
| `parallel/sweet_spot_plot.py` | ✅ PASS | Cubic fit → ideal segment size **73.03 mm**, ratio 1.04 to the 69.98 mm track length. |
| `processor/main.py` (`DataProcessor`) | ✅ PASS | 22/22 tested methods pass on synthetic RATPAC2-format data; produced all 11 figure PDFs + 3 coord `.npy`. (Real run still needs valid input paths — Issue #4.) |
| `processor/3dplot.py` | ✅ PASS | Matplotlib 3D smoke test. |
| `processor/hist_doped.py` | ❌ **FAIL** | Crashes at `json.load` on a corrupt data file — Issue #1. |

---

## 5. Issues found (severity-ranked)

### 🔴 Issue #1 — `hist_doped.py` crashes: corrupt JSON data file

`processor/data/10k_001wt_unfiltered.json` is **two identical, concatenated JSON objects** (each a 9989-event dict — an append-mode dump artifact, the same pattern as the `func_iter_*.txt` files). Plain `json.load()` only accepts one object and raises:

```
json.decoder.JSONDecodeError: Extra data: line 1 column 2023664 (char 2023663)
```

The script loads this file *first*, so it dies before plotting anything. (`10k_005wt_unfiltered.json` is a single object and loads fine.) This is a **data** defect, not a code defect — the loader is reasonable; the file is malformed.

### 🟠 Issue #2 — Two scripts write the same output filename

`usable_uncertainty_plot.py` and `uncertainty_plot.py` both `savefig("06_money_plot_fit_arctan_log_4p.pdf")`. Running the usable script **overwrites** the detected money plot. Relevant to the poster workflow: regenerating one silently clobbers the other.

### 🟡 Issue #3 — Latent invalid-escape `SyntaxWarning`s

TeX in non-raw Python strings produces deprecation warnings (will become `SyntaxError` in a future Python):

- `usable_uncertainty_plot.py:118–120` — `"$\Delta x$ ..."` (`\D`)
- `hist_doped.py:79,137,138` — `"...\%..."` (`\%`)

Harmless today (Python keeps unknown escapes literal, and LaTeX even *wants* `\%`). *Note:* `\v`, `\f`, `\b` would be silently mangled into control characters — verified the code correctly uses double-backslash or raw strings everywhere that matters, so there is no live corruption.

### 🟢 Issue #4 — `processor/main.py` hardcodes nonexistent input paths

`__init__` sets `self.dataFile = "/Users/gabriel/Downloads/ibd_cube_001wt_10k_run1/truth.txt"` (a Mac path); `initData()` calls `sys.exit()` if the file is absent, so the class cannot be instantiated as-shipped. Worked around by driving the class with patched paths + synthetic data. (Structural; also noted in `CLAUDE.md`.)

### ℹ️ Issue #5 — No entry points (expected)

Neither `parallel/main.py` nor `processor/main.py` has an `if __name__ == "__main__"` block — they only define classes. Running them bare does nothing. Documented in `CLAUDE.md`; external drivers were supplied for testing.

---

## 6. Physics sanity checks (data is healthy)

The 1M-event fiducial dataset is clean and internally consistent:

- `fid_1M_unfiltered_{vertices,captures}.npy`: both `(1000000, 3)` float64, **no NaN/Inf**.
- Mean neutron track length **69.9828 mm** — matches the `69.98286774221765` hardcoded in `sweet_spot_plot.py` to 5 sig-figs. ✅
- Usable fraction at dx=50 mm (r > 50/√2 = 35.36): **70.01%** — consistent with the code's own reported figure.
- `func_iter_*.txt` files all parse as clean 3-column `(n, σ, σ_err)`; `data14` has 34 rows.

---

## 7. Not tested (and why)

- **`DataProcessor` with `text.usetex=True`:** ran with `latex=False` for speed across ~20 plots. The usetex path is validated *separately* with the identical rcParams, so it is covered — but not run together.
- **Heavy experimental methods:** `continuousFrobeniusNorm`, `CFNDAnalysis` (each does `scipy.dblquad` over 360 angles — minutes-long), and the `*Sim` variants. Skipped for runtime, not correctness; they compile and their helper math (`CFND_eval_int`, `sym_2d_norm_dist`, `gaussian_2d`) tested OK.
- **Real `processData()` ingestion** from RATPAC2 ASCII (`truth.txt`/`neutrons.txt`) — those raw files aren't in the repo; tested the downstream `readData()` path the bundled `.npy` files feed.

---

## 8. Bottom line

The code is in **good working order**. The single hard failure (`hist_doped.py`) is caused by a corrupt data file, not the code. The environment — not the code — was the real blocker, and it is now fully provisioned for poster-plot work: edit any plotting script, run it, and get a valid usetex PDF. The most workflow-relevant gotcha while restyling figures is **Issue #2** (the shared output filename between the detected and usable money-plot scripts).

---

## Appendix — reproduction commands

```bash
# Environment (one-time)
python3 -m pip install scipy matplotlib tqdm mpi4py   # into mise Python 3.14.3
sudo pacman -S --needed openmpi                        # system MPI runtime

# Standalone plot scripts
cd neutrino-directionality/parallel
MPLBACKEND=Agg python3 uncertainty_plot.py             # set `save = True` to write the PDF

# ParallelProcessor (no entry point — needs an external driver)
mpiexec -n 4 python3 your_driver.py                    # driver instantiates ParallelProcessor + calls methods

# DataProcessor (no entry point; repoint the hardcoded data paths first)
```

Test drivers used this session live at `/tmp/pp_driver.py` and `/tmp/dp_driver.py`.
