#!/usr/bin/env python3
"""Unpack this assignment's public test data into a browsable folder.

The unit checks compare your work against arrays kept in a compressed ``.npz``.
This script writes those same arrays out as readable text (and as ``.png``
images where that makes sense) under ``tests/expected/``, so that when a check
fails you can see exactly what was fed in and what was expected back.

The folder is already included, so you only need this if you want to
regenerate it.

Usage:
    python export_expected.py
"""

import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# `cgcommon` (shared helpers) normally sits next to this file. If several
# assignments are checked out together it lives two levels up instead.
if not os.path.isdir(os.path.join(HERE, "cgcommon")):
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from cgcommon.expected import export_npz


def main():
    hits = sorted(glob.glob(os.path.join(HERE, "tests", "golden", "*_golden.npz")))
    if not hits:
        print("No golden fixture found in tests/golden/", file=sys.stderr)
        return 2
    out_dir = os.path.join(HERE, "tests", "expected")
    n = export_npz(hits[0], out_dir, title=os.path.basename(HERE))
    print(f"Wrote {n} entries to {os.path.relpath(out_dir, HERE)}/")
    print("Start at its INDEX.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
