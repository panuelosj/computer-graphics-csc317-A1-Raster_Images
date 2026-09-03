#!/usr/bin/env python3
"""Score your work for Assignment 1 against the PUBLIC tests, grader-style.

This runs exactly the checks the autograder runs, but only against the public
fixture that ships with this assignment -- the one whose inputs and expected
outputs you can inspect yourself (see ``tests/expected/``). It prints a mark
sheet so you can see where you stand before submitting.

Your submitted mark is 30% this public suite and 70% a private suite that calls
the same functions with *different* inputs. Solve the problem in general;
matching these particular numbers is not enough.

Usage:
    python check_my_work.py                  # full mark sheet
    python check_my_work.py --only rgba_to_rgb
    python check_my_work.py --verbose        # full failure messages
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

from cgcommon.testkit import practice_main
from tests.checks import get_checks

if __name__ == "__main__":
    raise SystemExit(practice_main(get_checks()))
