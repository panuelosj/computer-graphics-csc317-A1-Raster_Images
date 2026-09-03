"""Mouse grab-and-drag helpers for the interactive polyscope demos.

This module provides the "click a point and drag it in 3D" interaction style
used by two of the assignments:

* the **Kinematics** backend lets you grab the IK target and pull the arm around;
* the **Mass-Springs** backend lets you grab any cloth vertex and drag it.

The geometric core is two small pure functions (:func:`pick_point_near_ray`,
:func:`ray_plane_intersect`) that are unit-testable without a window. The
:class:`PointDragger` class is thin polyscope glue around them: on left-click it
casts a ray through the mouse, grabs the nearest candidate point within a
world-space radius, disables the default camera controls, and while the button
is held reports positions on the *view plane* through the grabbed point, i.e.
it unprojects at the selection's depth.

Nothing here is graded; students never edit this file.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "pick_point_near_ray",
    "ray_plane_intersect",
    "PointDragger",
]


# --------------------------------------------------------------------------
# pure geometry (no polyscope required)
# --------------------------------------------------------------------------

def ray_plane_intersect(origin, direction, plane_point, plane_normal):
    """Intersect the ray ``origin + t * direction`` with a plane.

    Returns the intersection point, or ``plane_point`` unchanged when the ray
    is (numerically) parallel to the plane or the hit would be behind the ray
    origin — both are harmless fallbacks for dragging.
    """
    o = np.asarray(origin, dtype=float).reshape(3)
    d = np.asarray(direction, dtype=float).reshape(3)
    p0 = np.asarray(plane_point, dtype=float).reshape(3)
    n = np.asarray(plane_normal, dtype=float).reshape(3)

    denom = float(d @ n)
    if abs(denom) < 1e-12:
        return p0.copy()
    t = float((p0 - o) @ n) / denom
    if t <= 0.0:
        return p0.copy()
    return o + t * d


def pick_point_near_ray(points, origin, direction, max_dist):
    """Find the candidate point closest to a picking ray.

    Parameters
    ----------
    points : (n, 3) array of candidate positions.
    origin, direction : the picking ray (direction need not be unit length).
    max_dist : world-space grab radius; points farther from the ray miss.

    Returns
    -------
    (index, distance) of the best point, or ``(None, inf)`` if nothing is
    within ``max_dist``. Points behind the ray origin are ignored. Among the
    points within the radius, the one *nearest the camera* wins, so grabbing
    in a cluttered view picks the front-most point.
    """
    P = np.asarray(points, dtype=float).reshape(-1, 3)
    o = np.asarray(origin, dtype=float).reshape(3)
    d = np.asarray(direction, dtype=float).reshape(3)
    d = d / (np.linalg.norm(d) + 1e-30)

    v = P - o
    t = v @ d                                # distance along the ray
    perp = np.linalg.norm(v - np.outer(t, d), axis=1)
    ok = (t > 0) & (perp <= max_dist)
    if not np.any(ok):
        return None, float("inf")
    # nearest to the camera among the candidates inside the grab radius
    t_masked = np.where(ok, t, np.inf)
    idx = int(np.argmin(t_masked))
    return idx, float(perp[idx])


# --------------------------------------------------------------------------
# polyscope glue
# --------------------------------------------------------------------------

def _mouse_pos(io):
    mp = io.MousePos
    if hasattr(mp, "x"):
        return float(mp.x), float(mp.y)
    return float(mp[0]), float(mp[1])


def _mouse_ray(coords):
    """Return (origin, direction) of the world-space ray under the mouse."""
    import polyscope as ps

    res = np.asarray(ps.screen_coords_to_world_ray(coords), dtype=float)
    if res.shape == (2, 3):
        return res[0], res[1]
    # binding returns the direction only; the origin is the camera position
    params = ps.get_view_camera_parameters()
    origin = np.asarray(params.get_position(), dtype=float).reshape(3)
    return origin, res.reshape(3)


def _camera_look_dir():
    import polyscope as ps

    params = ps.get_view_camera_parameters()
    for name in ("get_look_dir", "get_look_direction"):
        fn = getattr(params, name, None)
        if fn is not None:
            return np.asarray(fn(), dtype=float).reshape(3)
    return None


class PointDragger:
    """Left-click grab-and-drag of one point from a candidate set.

    Call :meth:`update` once per frame from the polyscope user callback with
    the current candidate positions. It returns one of:

    * ``("grab", index, position)``   — the mouse just grabbed point ``index``;
    * ``("drag", index, position)``   — held: ``position`` is the new location
      on the view plane through the grab point;
    * ``("release", index, None)``    — the button was let go;
    * ``(None, None, None)``          — nothing happening.

    While a drag is active the default polyscope camera interaction is
    disabled so the view doesn't orbit underneath the drag.
    """

    def __init__(self, grab_radius):
        self.grab_radius = float(grab_radius)
        self.index = None
        self._plane_point = None
        self._plane_normal = None

    @property
    def active(self):
        return self.index is not None

    def _set_camera_interaction(self, enabled):
        import polyscope as ps

        fn = getattr(ps, "set_do_default_mouse_interaction", None)
        if fn is not None:
            fn(bool(enabled))

    def update(self, points):
        import polyscope.imgui as psim

        io = psim.GetIO()

        if self.index is None:
            # Only start a grab on a fresh click that ImGui isn't consuming.
            if psim.IsMouseClicked(0) and not io.WantCaptureMouse:
                coords = _mouse_pos(io)
                origin, direction = _mouse_ray(coords)
                idx, _ = pick_point_near_ray(
                    points, origin, direction, self.grab_radius
                )
                if idx is not None:
                    self.index = idx
                    self._plane_point = np.asarray(points, dtype=float)[idx].copy()
                    normal = _camera_look_dir()
                    if normal is None:
                        normal = np.asarray(direction, dtype=float)
                    self._plane_normal = normal
                    self._set_camera_interaction(False)
                    return "grab", idx, self._plane_point.copy()
            return None, None, None

        if psim.IsMouseDown(0):
            coords = _mouse_pos(io)
            origin, direction = _mouse_ray(coords)
            pos = ray_plane_intersect(
                origin, direction, self._plane_point, self._plane_normal
            )
            return "drag", self.index, pos

        idx = self.index
        self.index = None
        self._plane_point = None
        self._plane_normal = None
        self._set_camera_interaction(True)
        return "release", idx, None


def key_pressed(name):
    """True if the named key (e.g. ``"A"``, ``"Space"``) was pressed this frame.

    Wraps ImGui's key API defensively so demos degrade to buttons-only when
    a constant is missing from the binding.
    """
    import polyscope.imgui as psim

    key = getattr(psim, f"ImGuiKey_{name}", None)
    if key is None:
        return False
    try:
        return bool(psim.IsKeyPressed(key, False))
    except TypeError:
        try:
            return bool(psim.IsKeyPressed(key))
        except Exception:  # noqa: BLE001
            return False


if __name__ == "__main__":
    # Headless self-test of the pure-geometry helpers.
    P = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, -5]])
    o = np.array([0.0, 0, 10.0])
    d = np.array([0.0, 0, -1.0])

    idx, dist = pick_point_near_ray(P, o, d, 0.25)
    assert idx == 0 and dist < 1e-12, (idx, dist)   # on-axis, front-most wins
    idx, _ = pick_point_near_ray(P + [0.05, 0, 0], o, d, 0.25)
    assert idx == 0, idx
    idx, _ = pick_point_near_ray(P, o, d, 1e-3)     # tiny radius: only exact hits
    assert idx == 0, idx
    idx, _ = pick_point_near_ray(P[1:3], o, d, 0.5)  # all miss
    assert idx is None, idx
    idx, _ = pick_point_near_ray(P, o, -d, 0.25)     # everything behind the ray
    assert idx is None, idx

    hit = ray_plane_intersect(o, d, np.zeros(3), np.array([0.0, 0, 1.0]))
    assert np.allclose(hit, [0, 0, 0]), hit
    hit = ray_plane_intersect(o, np.array([0.1, 0, -1.0]), np.zeros(3),
                              np.array([0.0, 0, 1.0]))
    assert np.allclose(hit, [1.0, 0, 0]), hit        # oblique ray lands off-axis
    hit = ray_plane_intersect(o, np.array([1.0, 0, 0]), np.zeros(3),
                              np.array([0.0, 0, 1.0]))
    assert np.allclose(hit, [0, 0, 0]), hit          # parallel: fallback

    print("interact.py self-test: OK")
