"""Export a golden ``.npz`` fixture into human-readable files.

The unit checks compare your functions against arrays stored in a compressed
``.npz``. That format is compact and exact, but you cannot *look* at it. This
module unpacks one into a browsable folder:

* image-shaped ``uint8`` arrays become ``.png`` files you can open;
* every array also gets a ``.txt`` dump (values, or a truncated head plus
  summary statistics when it is very large);
* an ``INDEX.md`` lists every entry with its shape, dtype and range.

Used by the repo-root ``export_expected.py`` script.
"""

from __future__ import annotations

import os

import numpy as np

# Arrays with more elements than this are truncated in the .txt dump.
MAX_TEXT_ELEMENTS = 4000
# Rows shown when truncating.
HEAD_ROWS = 24


def _is_image(arr: np.ndarray) -> bool:
    """True when ``arr`` looks like something worth writing as a PNG."""
    if arr.dtype != np.uint8:
        return False
    if arr.ndim == 2:
        return min(arr.shape) >= 4
    if arr.ndim == 3 and arr.shape[2] in (3, 4):
        return min(arr.shape[:2]) >= 4
    return False


def _describe(arr: np.ndarray) -> str:
    """A one-line summary of an array's shape, dtype and value range."""
    if arr.dtype.kind in "fiu" and arr.size:
        finite = arr[np.isfinite(arr)] if arr.dtype.kind == "f" else arr
        if finite.size:
            return (f"shape {arr.shape}, dtype {arr.dtype}, "
                    f"range [{finite.min():.6g}, {finite.max():.6g}]")
    return f"shape {arr.shape}, dtype {arr.dtype}"


def _write_text(path: str, name: str, arr: np.ndarray) -> bool:
    """Write a readable dump of ``arr``. Returns True if it was truncated."""
    truncated = False
    with open(path, "w") as f:
        f.write(f"# {name}\n# {_describe(arr)}\n#\n")
        if arr.ndim == 0:
            f.write(f"{arr.item()}\n")
        elif arr.size <= MAX_TEXT_ELEMENTS:
            f.write(np.array2string(arr, threshold=arr.size + 1,
                                    max_line_width=100, precision=8,
                                    suppress_small=False))
            f.write("\n")
        else:
            truncated = True
            flat_rows = arr.reshape(arr.shape[0], -1) if arr.ndim > 1 else arr
            f.write(f"# TRUNCATED: showing the first {HEAD_ROWS} of "
                    f"{arr.shape[0]} rows.\n")
            f.write(f"# Load the full array with:\n"
                    f"#   import numpy as np\n"
                    f"#   g = np.load('<this assignment>/tests/golden/"
                    f"<id>_golden.npz')\n"
                    f"#   g['{name}']\n#\n")
            f.write(np.array2string(np.asarray(flat_rows[:HEAD_ROWS]),
                                    threshold=10 ** 9, max_line_width=100,
                                    precision=8))
            f.write("\n")
    return truncated


def export_npz(npz_path: str, out_dir: str, title: str = "",
               notes: dict | None = None) -> int:
    """Unpack ``npz_path`` into ``out_dir``. Returns the number of entries."""
    from cgcommon.image import save_png

    notes = notes or {}
    data = np.load(npz_path, allow_pickle=True)
    os.makedirs(out_dir, exist_ok=True)
    txt_dir = os.path.join(out_dir, "arrays")
    img_dir = os.path.join(out_dir, "images")
    os.makedirs(txt_dir, exist_ok=True)

    rows = []
    n_images = 0
    for name in sorted(data.files):
        arr = np.asarray(data[name])
        png = ""
        if _is_image(arr):
            os.makedirs(img_dir, exist_ok=True)
            png_name = f"{name}.png"
            save_png(os.path.join(img_dir, png_name), arr)
            png = f"images/{png_name}"
            n_images += 1
        truncated = _write_text(os.path.join(txt_dir, f"{name}.txt"), name, arr)
        rows.append((name, _describe(arr), f"arrays/{name}.txt", png,
                     truncated, notes.get(name, "")))

    with open(os.path.join(out_dir, "INDEX.md"), "w") as f:
        f.write(f"# Public test data{': ' + title if title else ''}\n\n")
        f.write(
            "These are the exact arrays the public unit checks compare your\n"
            "functions against — the inputs they feed in and the outputs they\n"
            "expect back. Everything here is generated from\n"
            f"`{os.path.basename(npz_path)}`; nothing here is secret, and you\n"
            "are meant to look at it when a check fails.\n\n"
            "* `arrays/<name>.txt` — the values, in readable form.\n"
            "* `images/<name>.png` — the same array as a viewable image, for\n"
            "  the entries that are pictures.\n\n"
            "To load an array yourself:\n\n"
            "```python\n"
            "import numpy as np\n"
            f"g = np.load('tests/golden/{os.path.basename(npz_path)}')\n"
            "print(g.files)          # every available name\n"
            "img = g['<name>']       # one array\n"
            "```\n\n"
            "Regenerate this folder with `python export_expected.py "
            "<assignment>` from the repository root.\n\n"
        )
        f.write("| entry | what it is | values | picture |\n")
        f.write("|---|---|---|---|\n")
        for name, desc, txt, png, truncated, note in rows:
            what = note or ""
            if truncated:
                what = (what + " " if what else "") + "_(txt truncated)_"
            pic = f"[view]({png})" if png else "—"
            f.write(f"| `{name}` | {what or desc} | [{os.path.basename(txt)}]"
                    f"({txt}) | {pic} |\n")

    return len(rows)
