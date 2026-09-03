#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Setup script for Raster Images (macOS / Linux).
#
# Creates a Python virtual environment in ./venv and installs this
# assignment's dependencies.
#
# Usage:
#     ./init.sh                  # create venv and install dependencies
#     source venv/bin/activate   # then activate it in your shell
#
# Run this once. Re-running is safe: it reinstalls/upgrades the dependencies.
# ---------------------------------------------------------------------------
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

if [ ! -d venv ]; then
    echo "==> Creating virtual environment in ./venv"
    "$PYTHON" -m venv venv
fi

echo "==> Installing dependencies"
# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt

echo ""
echo "Done. Activate the environment in each new shell with:"
echo ""
echo "    source venv/bin/activate"
echo ""
echo "Then:"
echo ""
echo "    python main.py           # run the demo backend"
echo "    python run_tests.py      # check your implementation"
echo "    python check_my_work.py  # see it scored as marks"
echo ""
