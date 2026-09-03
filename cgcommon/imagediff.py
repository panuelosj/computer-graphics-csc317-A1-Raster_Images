"""Write a visual comparison when an image check fails.

A message like "values differ by up to 37" tells you *that* an image is wrong
but not *where*, which is usually the part you need. When a check that compares
images fails, this writes three files -- what you produced, what was expected,
and a map of the difference -- and returns a sentence pointing at them.

Files land in ``out/test_diffs/`` inside the assignment, or in ``$CG_DIFF_DIR``
when the grader sets one so an instructor can collect them per submission.

Backend code: no assignment asks you to implement any of this.
"""

from __future__ import annotations

import os

import numpy as np


def diff_dir(default_root: str) -> str:
    """Where comparison images should be written."""
    return os.environ.get("CG_DIFF_DIR") or os.path.join(
        default_root, "out", "test_diffs"
    )


def _as_rgb(img: np.ndarray) -> np.ndarray:
    """Coerce a grayscale / RGB / RGBA uint8 image to plain RGB for viewing."""
    a = np.asarray(img)
    if a.ndim == 2:
        a = np.repeat(a[:, :, None], 3, axis=2)
    elif a.ndim == 3 and a.shape[2] == 4:
        a = a[:, :, :3]
    elif a.ndim == 3 and a.shape[2] == 1:
        a = np.repeat(a, 3, axis=2)
    return np.clip(a, 0, 255).astype(np.uint8)


def _heatmap(delta: np.ndarray) -> np.ndarray:
    """Per-pixel error as a black -> red -> yellow -> white ramp."""
    d = delta.astype(float)
    peak = float(d.max())
    if peak <= 0:
        return np.zeros(d.shape + (3,), dtype=np.uint8)
    # Emphasise small errors: they matter and would otherwise be invisible.
    t = np.sqrt(d / peak)
    r = np.clip(t * 3.0, 0, 1)
    g = np.clip(t * 3.0 - 1.0, 0, 1)
    b = np.clip(t * 3.0 - 2.0, 0, 1)
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)


def _display(path: str, root: str) -> str:
    """The most readable form of ``path``.

    When the grader collects diffs (``CG_DIFF_DIR``), paths are shown relative
    to the folder holding that submission's report, so a line reads
    ``public/foo.got.png``. Otherwise: relative to the working directory if
    that is tidy, then to the assignment, and only then absolute.
    """
    bases = []
    collected = os.environ.get("CG_DIFF_DIR")
    if collected:
        bases.append(os.path.dirname(os.path.abspath(collected)))
    for base in bases + [os.getcwd(), root]:
        try:
            rel = os.path.relpath(path, base)
        except ValueError:                      # different drive on Windows
            continue
        if not rel.startswith(".."):
            return rel
    return path


def report(name: str, got, expected, root: str, note: str = "") -> str:
    """Write got/expected/diff images and return a sentence describing them.

    Returns an empty string if anything goes wrong -- a diagnostic must never
    be the reason a test errors out.
    """
    try:
        from cgcommon.image import save_png

        g = np.asarray(got)
        e = np.asarray(expected)
        out = diff_dir(root)
        os.makedirs(out, exist_ok=True)

        if g.shape != e.shape:
            save_png(os.path.join(out, f"{name}.expected.png"), _as_rgb(e))
            if g.ndim in (2, 3) and g.size:
                save_png(os.path.join(out, f"{name}.got.png"), _as_rgb(g))
            return (f"\n    shapes differ: yours {g.shape}, expected {e.shape}"
                    f"\n    wrote {_display(out, root)}/{name}.*.png")

        gi = g.astype(np.int64)
        ei = e.astype(np.int64)
        delta = np.abs(gi - ei)
        per_pixel = delta.max(axis=2) if delta.ndim == 3 else delta
        n_bad = int((per_pixel > 0).sum())
        total = int(per_pixel.size)

        save_png(os.path.join(out, f"{name}.got.png"), _as_rgb(g))
        save_png(os.path.join(out, f"{name}.expected.png"), _as_rgb(e))
        save_png(os.path.join(out, f"{name}.diff.png"), _heatmap(per_pixel))

        rel = _display(out, root)
        where = ""
        if n_bad:
            ys, xs = np.nonzero(per_pixel)
            where = (f"\n    first differing pixel: row {int(ys[0])}, "
                     f"col {int(xs[0])} "
                     f"(yours {np.asarray(g[ys[0], xs[0]]).tolist()}, "
                     f"expected {np.asarray(e[ys[0], xs[0]]).tolist()})")
        return (f"\n    {n_bad}/{total} pixels differ, by up to "
                f"{int(per_pixel.max())}{where}"
                f"\n    wrote {rel}/{name}.got.png, .expected.png and .diff.png"
                f"\n    (in the diff, brighter = larger error)"
                + (f"\n    {note}" if note else ""))
    except Exception:
        return ""
