#!/usr/bin/env bash
#
# Set up the Python environment for the neutrino-directionality analysis.
#
# Usage:
#   ./setup.sh            # create .venv and install into it (default, recommended)
#   ./setup.sh --system   # install into the current Python environment instead
#
# Installs the pip-managed stack from requirements.txt, and CHECKS for the two
# system dependencies pip cannot provide:
#   * an MPI implementation (mpiexec)  — mpi4py compiles against it  (FATAL if missing)
#   * a LaTeX toolchain (pdflatex)     — plot scripts set text.usetex=True  (warning)
#
# It will NOT run sudo / install system packages for you; it prints the Arch
# pacman commands if something is missing.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

USE_VENV=1
[[ "${1:-}" == "--system" ]] && USE_VENV=0

bold() { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }

# --- 1. Python -----------------------------------------------------------
command -v python3 >/dev/null || { echo "python3 not found on PATH"; exit 1; }
bold "Python: $(python3 --version)"

# --- 2. System dependencies (cannot be pip-installed) --------------------
bold "Checking system dependencies"

if command -v mpiexec >/dev/null; then
  ok "MPI:   $(mpiexec --version 2>&1 | head -1)"
else
  warn "mpiexec not found — mpi4py cannot build without a system MPI."
  warn "Install it first, then re-run.  On Arch:"
  printf '         sudo pacman -S --needed openmpi\n'
  exit 1
fi

if command -v pdflatex >/dev/null; then
  ok "LaTeX: $(pdflatex --version 2>&1 | head -1)"
else
  warn "pdflatex not found — plot scripts use text.usetex=True and will crash"
  warn "on save until LaTeX is installed.  On Arch:"
  printf '         sudo pacman -S --needed texlive-bin texlive-latexextra\n'
  warn "Continuing anyway (the pip install does not need LaTeX)."
fi

# --- 3. Python environment ----------------------------------------------
if (( USE_VENV )); then
  bold "Creating virtual environment in .venv"
  [[ -d .venv ]] || python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  ok "active: $(python3 -c 'import sys; print(sys.prefix)')"
else
  bold "Installing into current environment"
  ok "target: $(python3 -c 'import sys; print(sys.prefix)')"
fi

# --- 4. Install the stack -----------------------------------------------
bold "Installing Python packages from requirements.txt"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# --- 5. Verify -----------------------------------------------------------
bold "Verifying imports"
python3 - <<'PY'
import importlib
mods = ["numpy", "scipy", "matplotlib", "pandas", "tqdm", "mpi4py"]
width = max(len(m) for m in mods)
for m in mods:
    mod = importlib.import_module(m)
    print(f"  ✓ {m:<{width}}  {getattr(mod, '__version__', '?')}")
PY

bold "Done."
if (( USE_VENV )); then
  echo "Activate it in new shells with:  source .venv/bin/activate"
fi
