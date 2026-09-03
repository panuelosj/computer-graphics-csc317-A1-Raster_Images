"""Minimal Wavefront ``.obj`` reading helpers (non-student infrastructure).

Students implement their *own* ``write_obj`` in the Meshes assignment; this
module is only used by the backend to *load* sample meshes and by the grader.

Faces may be triangles or quads. ``read_obj`` returns vertex positions and a
face list. When all faces share the same arity, a rectangular integer array is
returned; otherwise a list of index lists is returned.
"""

from __future__ import annotations

from typing import List, Tuple, Union

import numpy as np


def read_obj(filename: str) -> Tuple[np.ndarray, Union[np.ndarray, List[List[int]]]]:
    """Read positions ``V`` (``n×3``) and faces ``F`` from an ``.obj`` file.

    Only ``v`` and ``f`` lines are consulted; texture/normal indices in
    ``f a/b/c`` tokens are ignored (only the position index is kept). Face
    indices in the returned array are 0-based. Negative (relative) face
    indices are resolved per the OBJ spec, and leading whitespace on lines
    is tolerated.
    """
    verts: List[List[float]] = []
    faces: List[List[int]] = []
    with open(filename, "r") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "v":
                verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == "f":
                idx = []
                for tok in parts[1:]:
                    # handle "v", "v/vt", "v//vn", "v/vt/vn"
                    i = int(tok.split("/")[0])
                    # negative indices are relative to the vertices read so far
                    idx.append(len(verts) + i if i < 0 else i - 1)
                faces.append(idx)

    V = np.array(verts, dtype=float)
    arities = {len(face) for face in faces}
    if len(arities) == 1:
        F = np.array(faces, dtype=int)
    else:
        F = faces
    return V, F


def triangulate(F: Union[np.ndarray, List[List[int]]]) -> np.ndarray:
    """Fan-triangulate a face list into an ``m×3`` triangle index array."""
    tris: List[List[int]] = []
    for face in F:
        face = list(face)
        for k in range(1, len(face) - 1):
            tris.append([face[0], face[k], face[k + 1]])
    return np.array(tris, dtype=int)
