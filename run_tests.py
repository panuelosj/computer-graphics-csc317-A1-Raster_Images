#!/usr/bin/env python3
"""Run the unit checks for Assignment 1 and report how many pass.

Usage:
    python run_tests.py            # friendly table + "Validated X/Y"
    python run_tests.py --only rgb_to_gray   # focus on a single function
    python run_tests.py --json     # machine-readable (used by the grader)
"""

import os
import sys

# Make `src` (your code) and `cgcommon` (shared helpers) importable regardless
# of the directory this is launched from.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# `cgcommon` (shared helpers) normally sits next to this file. If several
# assignments are checked out together it lives two levels up instead.
if not os.path.isdir(os.path.join(HERE, "cgcommon")):
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from cgcommon.testkit import main
from tests.checks import get_checks

if __name__ == "__main__":
    raise SystemExit(main(get_checks()))
