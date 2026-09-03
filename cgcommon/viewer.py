"""Thin convenience wrappers around `polyscope` for the interactive demos.

These helpers keep window/boilerplate out of the assignment ``main.py`` files
and make every interactive backend degrade gracefully when no display or GPU
context is available (e.g. on a headless grading machine): in that case the
backend should catch :class:`ViewerUnavailable` and continue in a non-interactive
mode.
"""

from __future__ import annotations

import numpy as np


class ViewerUnavailable(RuntimeError):
    """Raised when a polyscope window cannot be created (e.g. headless)."""


_INITIALIZED = False


def ensure_init() -> None:
    """Initialise polyscope once, raising :class:`ViewerUnavailable` on failure."""
    global _INITIALIZED
    if _INITIALIZED:
        return
    try:
        import polyscope as ps

        ps.init()
        ps.set_up_dir("y_up")
        ps.set_ground_plane_mode("shadow_only")
        _INITIALIZED = True
    except Exception as exc:  # noqa: BLE001
        raise ViewerUnavailable(str(exc)) from exc


def show() -> None:
    """Open the interactive window (blocks until the user closes it).

    Raises :class:`ViewerUnavailable` if the window cannot be shown
    (symmetry with :func:`ensure_init`).
    """
    try:
        import polyscope as ps

        ps.show()
    except Exception as exc:  # noqa: BLE001
        raise ViewerUnavailable(str(exc)) from exc


def triangulate(F):
    """Fan-triangulate a face array/list to ``m×3`` (polyscope wants triangles
    or a consistent arity). Quad arrays are handled directly by polyscope, so
    this is only needed for mixed-arity meshes.

    Kept for backwards compatibility; delegates to
    :func:`cgcommon.objio.triangulate`."""
    from cgcommon.objio import triangulate as _triangulate

    return _triangulate(F)
