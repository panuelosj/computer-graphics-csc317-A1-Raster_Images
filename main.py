#!/usr/bin/env python3
"""Assignment 1 demo backend.

Runs your ``src/`` functions end-to-end on one or more input images and writes
the results next to this script as ``.ppm`` (and ``.png`` previews). With no
arguments it uses the sample images in ``data/``.

Usage:
    python main.py                                  # use default data/*.png
    python main.py data/dog.png                     # single image
    python main.py data/sparkles.png data/dog.png   # composite a stack
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# `cgcommon` (shared helpers) normally sits next to this file. If several
# assignments are checked out together it lives two levels up instead.
if not os.path.isdir(os.path.join(HERE, "cgcommon")):
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from cgcommon.image import read_rgba_from_png, save_png

from src.rgba_to_rgb import rgba_to_rgb
from src.write_ppm import write_ppm
from src.reflect import reflect
from src.rotate import rotate
from src.rgb_to_gray import rgb_to_gray
from src.simulate_bayer_mosaic import simulate_bayer_mosaic
from src.demosaic import demosaic
from src.hue_shift import hue_shift
from src.desaturate import desaturate
from src.over import over

DEFAULT_INPUTS = [
    os.path.join(HERE, "data", "dog.png"),
    os.path.join(HERE, "data", "glasses.png"),
    os.path.join(HERE, "data", "laser-beams.png"),
    os.path.join(HERE, "data", "sparkles.png"),
]


def emit(name, image):
    """Write ``image`` as both a .ppm (assignment format) and a .png preview."""
    out_dir = os.path.join(HERE, "out")
    os.makedirs(out_dir, exist_ok=True)
    write_ppm(os.path.join(out_dir, name + ".ppm"), image)
    save_png(os.path.join(out_dir, name + ".png"), image)
    print(f"  wrote out/{name}.ppm and out/{name}.png")


def main(argv):
    inputs = argv[1:] if len(argv) > 1 else DEFAULT_INPUTS

    rgba = read_rgba_from_png(inputs[0])
    rgb = rgba_to_rgb(rgba)
    emit("rgb", rgb)
    emit("reflected", reflect(rgb))
    emit("rotated", rotate(rgb))
    emit("gray", rgb_to_gray(rgb))

    bayer = simulate_bayer_mosaic(rgb)
    emit("bayer", bayer)
    emit("demosaicked", demosaic(bayer))

    emit("shifted", hue_shift(rgb, 180.0))
    emit("desaturated", desaturate(rgb, 0.25))

    # Alpha-composite the stack of inputs (foreground first).
    composite = read_rgba_from_png(inputs[0])
    for f in inputs[1:]:
        nxt = read_rgba_from_png(f)
        if nxt.shape != composite.shape:
            print(f"  skipping {f}: size mismatch")
            continue
        composite = over(nxt, composite)
    emit("composite", rgba_to_rgb(composite))

    print("\nDone. Open the PNGs in out/ to view your results.")


if __name__ == "__main__":
    main(sys.argv)
