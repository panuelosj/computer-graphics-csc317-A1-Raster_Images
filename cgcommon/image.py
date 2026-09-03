"""Image I/O helpers shared by the raster and ray-tracing assignments.

Conventions used throughout the course:

* Images are ``numpy`` arrays of shape ``(height, width, channels)`` (or
  ``(height, width)`` for grayscale).
* ``uint8`` arrays hold integer intensities in ``[0, 255]``.
* ``float`` arrays hold intensities in ``[0, 1]``.

These helpers keep PNG decoding (Pillow) and the simple text ``.ppm`` writer
out of student code so the students can focus on the algorithms.
"""

from __future__ import annotations

import numpy as np
from PIL import Image


def read_rgba_from_png(filename: str) -> np.ndarray:
    """Load a PNG as an ``(H, W, 4)`` ``uint8`` RGBA array."""
    img = Image.open(filename).convert("RGBA")
    return np.asarray(img, dtype=np.uint8)


def read_rgb_from_png(filename: str) -> np.ndarray:
    """Load a PNG as an ``(H, W, 3)`` ``uint8`` RGB array."""
    img = Image.open(filename).convert("RGB")
    return np.asarray(img, dtype=np.uint8)


def save_png(filename: str, data: np.ndarray) -> None:
    """Save a ``uint8`` array (grayscale, RGB, or RGBA) as a PNG."""
    arr = np.asarray(data)
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    Image.fromarray(arr).save(filename)


def write_ppm(filename: str, data: np.ndarray) -> None:
    """Write a P2 (grayscale) or P3 (RGB) text ``.ppm`` file.

    ``data`` must be a ``uint8`` array of shape ``(H, W)``, ``(H, W, 1)``
    (treated as grayscale), or ``(H, W, 3)``. The format is deliberately
    simple and uncompressed, so output can be inspected in a text editor.
    """
    arr = np.asarray(data)
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)

    if arr.ndim == 3 and arr.shape[2] == 1:
        arr = arr[:, :, 0]  # single-channel image -> grayscale

    if arr.ndim == 2:
        height, width = arr.shape
        magic = "P2"
        flat = arr.reshape(height, width)
    elif arr.ndim == 3 and arr.shape[2] == 3:
        height, width = arr.shape[:2]
        magic = "P3"
        flat = arr.reshape(height, width * 3)
    else:
        raise ValueError(".ppm only supports (H,W) grayscale or (H,W,3) RGB arrays")

    with open(filename, "w") as f:
        f.write(f"{magic}\n{width} {height}\n255\n")
        for row in flat:
            f.write(" ".join(str(int(v)) for v in row))
            f.write("\n")


def read_ppm(filename: str) -> np.ndarray:
    """Read a P2/P3 text ``.ppm`` file into a ``uint8`` array (used by tests).

    ``#`` comment lines (and inline ``# ...`` trailers) are stripped per the
    PPM spec before tokenizing.
    """
    with open(filename, "r") as f:
        lines = [line.split("#", 1)[0] for line in f]
    tokens = " ".join(lines).split()
    magic = tokens[0]
    width, height, _maxval = int(tokens[1]), int(tokens[2]), int(tokens[3])
    values = np.array(tokens[4:], dtype=np.uint8)
    if magic == "P2":
        return values.reshape(height, width)
    if magic == "P3":
        return values.reshape(height, width, 3)
    raise ValueError(f"Unsupported PPM magic {magic!r}")
