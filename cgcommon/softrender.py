"""A tiny software rasteriser for headless previews.

The interactive viewers need a display; continuous integration, the grading
sandbox and the README images do not have one. This module draws a shaded
triangle mesh straight into a numpy image so every backend can produce a
picture without a GPU or a window.

It is deliberately simple -- an orthographic camera, a z-buffer and Gouraud
(per-vertex colour) interpolation -- but that is enough to make the results of
the assignments legible.

This is backend code; no assignment asks you to implement it.
"""

from __future__ import annotations

import numpy as np


def _as_triangles(F) -> np.ndarray:
    """Return an (m,3) triangle array, fanning any polygon with >3 sides."""
    F = np.asarray(F)
    if F.ndim == 2 and F.shape[1] == 3:
        return F.astype(int)
    tris = []
    for face in F:
        face = [int(i) for i in np.asarray(face).ravel()]
        for k in range(1, len(face) - 1):
            tris.append([face[0], face[k], face[k + 1]])
    return np.asarray(tris, dtype=int).reshape(-1, 3)


def look_at_rotation(direction) -> np.ndarray:
    """A rotation whose -z axis points along ``direction`` (a view direction)."""
    f = np.asarray(direction, dtype=float)
    f = f / (np.linalg.norm(f) or 1.0)
    up = np.array([0.0, 1.0, 0.0])
    if abs(f @ up) > 0.99:
        up = np.array([0.0, 0.0, 1.0])
    r = np.cross(up, f)
    r = r / (np.linalg.norm(r) or 1.0)
    u = np.cross(f, r)
    return np.stack([r, u, f])          # rows: right, up, forward


def _sample_texture(tex, u, v, wrap=True):
    """Bilinearly sample ``tex`` at coordinates ``u``, ``v`` in [0,1]."""
    h, w = tex.shape[:2]
    # .obj puts the texture origin bottom-left; images index from the top
    y = (1.0 - np.asarray(v, dtype=float))
    x = np.asarray(u, dtype=float)
    if wrap:
        x = np.mod(x, 1.0)
        y = np.mod(y, 1.0)
    else:
        x = np.clip(x, 0.0, 1.0)
        y = np.clip(y, 0.0, 1.0)
    fx = x * (w - 1)
    fy = y * (h - 1)
    x0 = np.floor(fx).astype(np.int64)
    y0 = np.floor(fy).astype(np.int64)
    x1 = np.minimum(x0 + 1, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)
    tx = (fx - x0)[..., None]
    ty = (fy - y0)[..., None]
    top = tex[y0, x0] * (1 - tx) + tex[y0, x1] * tx
    bot = tex[y1, x0] * (1 - tx) + tex[y1, x1] * tx
    return top * (1 - ty) + bot * ty


def render_mesh(V, F, colors, size=512, background=(0.02, 0.02, 0.03),
                view=(0.0, 0.0, 1.0), margin=1.08, shade_backfaces=True,
                center=None, extent=None, uv=None, texture=None,
                texture_wrap=True, segments=None,
                segment_color=(1.0, 1.0, 1.0), segment_width=1.0,
                segment_depth_test=False, overlays=None, supersample=1):
    """Rasterise a coloured mesh to an ``(size, size, 3)`` uint8 image.

    Parameters
    ----------
    V : (n,3) positions.
    F : (m,3) or (m,4) faces (quads are fanned into triangles).
    colors : (n,3) per-vertex RGB in [0,1], or a single RGB triple.
    view : the direction the camera looks *from* toward the origin.
    margin : padding around the geometry, used only when auto-fitting.
    center, extent : an explicit **static** camera -- ``center`` is the
        world-space point the frame is centred on and ``extent`` the half-width
        of the visible square, in world units. Pass both to stop the camera
        re-fitting itself: an auto-fitted camera silently zooms and pans from
        frame to frame, which turns an animation into a wobble. Use
        :func:`fit_camera` to compute values that hold for a whole sequence.
    uv, texture : per-vertex texture coordinates ``(n,2)`` and an image as a
        float ``(H,W,3)`` array in [0,1]. When both are given the *texture
        coordinates* are what gets interpolated across each triangle and the
        texture is sampled per pixel, so the result is as sharp as the image
        rather than as coarse as the mesh. ``colors`` then acts as a per-vertex
        shading multiplier on the sampled texel.
    texture_wrap : tile the texture for coordinates outside [0,1] (the default)
        instead of clamping to the edge.
    segments : ``(k,2,3)`` world-space line segments drawn over the mesh, or
        ``None``. Use :func:`box_segments` to turn bounding boxes into these
        and :func:`mesh_edges` for a mesh's own triangle edges.
    segment_color : one RGB triple, or ``(k,3)`` for a colour per segment.
    segment_width : stroke width in pixels (before ``supersample``).
    segment_depth_test : hide the parts of a segment that the mesh covers. The
        default draws them on top, which is what makes an enclosing hierarchy
        of boxes readable -- most of it is behind the surface.
    overlays : a list of ``dict(segments=..., color=..., width=...,
        depth_test=..., alpha=...)`` drawn in order after the mesh, for when
        one picture
        needs strokes with different rules -- a mesh's own edges hidden by its
        surface, with the bounding boxes laid over the top of both.
    supersample : render this many times larger and average down. Costs
        ``supersample ** 2`` the work and is what keeps thin lines from
        crawling; 1 (the default) leaves every existing caller untouched.
    """
    ss = max(1, int(supersample))
    if ss > 1:
        big = render_mesh(
            V, F, colors, size=size * ss, background=background, view=view,
            margin=margin, shade_backfaces=shade_backfaces, center=center,
            extent=extent, uv=uv, texture=texture,
            texture_wrap=texture_wrap,
            segments=segments, segment_color=segment_color,
            segment_width=segment_width * ss,
            segment_depth_test=segment_depth_test,
            overlays=[dict(o, width=o.get("width", 1.0) * ss)
                      for o in (overlays or [])],
            supersample=1,
        )
        return (big.reshape(size, ss, size, ss, 3)
                   .mean(axis=(1, 3)).round().astype(np.uint8))
    V = np.asarray(V, dtype=float)
    tris = _as_triangles(F)
    C = np.asarray(colors, dtype=float)
    if C.ndim == 1:
        C = np.tile(C.reshape(1, 3), (V.shape[0], 1))
    C = np.clip(C, 0.0, 1.0)

    tex = None
    if texture is not None and uv is not None:
        tex = np.asarray(texture, dtype=float)
        if tex.dtype != np.float64 or tex.max() > 1.0:
            tex = tex.astype(float) / (255.0 if tex.max() > 1.0 else 1.0)
        UV = np.asarray(uv, dtype=float).reshape(-1, 2)

    # Orthographic camera: rotate the world so the view direction is +z.
    R = look_at_rotation(view)
    P = V @ R.T                                   # (n,3): x right, y up, z depth

    img = np.zeros((size, size, 3), dtype=np.float64)
    img[:, :] = np.asarray(background, dtype=float)
    zbuf = np.full((size, size), -np.inf)
    if (V.size == 0 or tris.size == 0) and segments is None and not overlays:
        return (np.clip(img, 0, 1) * 255).astype(np.uint8)

    # Static camera when given one; otherwise fit this frame's geometry.
    if center is not None and extent is not None:
        centre = (np.asarray(center, dtype=float) @ R.T)[:2]
        half = float(extent) or 1.0
    else:
        _src = segments if segments is not None else np.concatenate(
            [np.asarray(o["segments"], float).reshape(-1, 2, 3)
             for o in overlays]) if overlays else np.zeros((0, 2, 3))
        ref = P[:, :2] if P.size else np.asarray(_src, float).reshape(-1, 3) @ R.T
        ref = ref[:, :2] if ref.shape[1] == 3 else ref
        centre = 0.5 * (ref.max(axis=0) + ref.min(axis=0))
        half = 0.5 * float((ref.max(axis=0) - ref.min(axis=0)).max())
        half = (half or 1.0) * margin
    def to_pixels(Q):
        """Camera-space -> pixel coordinates (x right, y down, z toward eye)."""
        ax = ((Q[:, 0] - centre[0]) / half + 1.0) * 0.5 * (size - 1)
        ay = (1.0 - (Q[:, 1] - centre[1]) / half) * 0.5 * (size - 1)
        return np.stack([ax, ay, Q[:, 2]], axis=1)

    _p = to_pixels(P) if P.size else np.zeros((0, 3))
    px, py, pz = _p[:, 0], _p[:, 1], _p[:, 2]

    for tri in tris:
        i0, i1, i2 = tri
        x0, y0 = px[i0], py[i0]
        x1, y1 = px[i1], py[i1]
        x2, y2 = px[i2], py[i2]

        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if area == 0.0:
            continue
        if area > 0 and not shade_backfaces:
            continue

        lo_x = max(int(np.floor(min(x0, x1, x2))), 0)
        hi_x = min(int(np.ceil(max(x0, x1, x2))), size - 1)
        lo_y = max(int(np.floor(min(y0, y1, y2))), 0)
        hi_y = min(int(np.ceil(max(y0, y1, y2))), size - 1)
        if lo_x > hi_x or lo_y > hi_y:
            continue

        ys, xs = np.mgrid[lo_y:hi_y + 1, lo_x:hi_x + 1]
        xs = xs + 0.5
        ys = ys + 0.5
        # Barycentric coordinates over the bounding box.
        w0 = ((x1 - xs) * (y2 - ys) - (x2 - xs) * (y1 - ys)) / area
        w1 = ((x2 - xs) * (y0 - ys) - (x0 - xs) * (y2 - ys)) / area
        w2 = 1.0 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not inside.any():
            continue

        z = w0 * pz[i0] + w1 * pz[i1] + w2 * pz[i2]
        sub_z = zbuf[lo_y:hi_y + 1, lo_x:hi_x + 1]
        visible = inside & (z > sub_z)
        if not visible.any():
            continue

        rgb = (w0[..., None] * C[i0] + w1[..., None] * C[i1]
               + w2[..., None] * C[i2])
        if tex is not None:
            # Interpolate the *texture coordinates* over the triangle, then
            # look the texture up once per pixel. Interpolating the colour
            # instead would cap the detail at one texel per vertex.
            uu = w0 * UV[i0, 0] + w1 * UV[i1, 0] + w2 * UV[i2, 0]
            vv = w0 * UV[i0, 1] + w1 * UV[i1, 1] + w2 * UV[i2, 1]
            rgb = rgb * _sample_texture(tex, uu, vv, texture_wrap)
        sub_img = img[lo_y:hi_y + 1, lo_x:hi_x + 1]
        sub_img[visible] = np.clip(rgb[visible], 0.0, 1.0)
        sub_z[visible] = z[visible]

    layers = []
    if segments is not None:
        layers.append(dict(segments=segments, color=segment_color,
                           width=segment_width, depth_test=segment_depth_test))
    layers.extend(overlays or [])
    for layer in layers:
        seg = np.asarray(layer["segments"], dtype=float).reshape(-1, 2, 3)
        if not seg.size:
            continue
        a = to_pixels(seg[:, 0] @ R.T)
        b = to_pixels(seg[:, 1] @ R.T)
        sc = np.asarray(layer.get("color", (1.0, 1.0, 1.0)), dtype=float)
        sc = (np.tile(sc.reshape(1, 3), (seg.shape[0], 1))
              if sc.ndim == 1 else sc)
        _stroke(img, zbuf, a, b, np.clip(sc, 0.0, 1.0),
                float(layer.get("width", 1.0)),
                bool(layer.get("depth_test", False)), size,
                float(layer.get("alpha", 1.0)))

    return (np.clip(img, 0.0, 1.0) * 255).astype(np.uint8)


def _stroke(img, zbuf, a, b, colors, width, depth_test, size, alpha=1.0):
    """Draw 3D line segments already projected to pixel space.

    Segments are sorted by on-screen length and handled in blocks so that one
    long edge does not force every short one to be sampled at its resolution --
    a hierarchy's deepest level is thousands of very short segments.
    """
    length = np.linalg.norm(b[:, :2] - a[:, :2], axis=1)
    order = np.argsort(length)
    half_w = max(0, int(np.ceil(width / 2.0 - 0.5)))
    offs = [(dx, dy)
            for dy in range(-half_w, half_w + 1)
            for dx in range(-half_w, half_w + 1)
            if dx * dx + dy * dy <= (width / 2.0) ** 2 + 0.25]

    for start in range(0, order.size, 1024):
        idx = order[start:start + 1024]
        n = int(min(4096, max(2, np.ceil(length[idx].max()) * 2 + 2)))
        t = np.linspace(0.0, 1.0, n).reshape(1, n, 1)
        pts = a[idx][:, None, :] * (1.0 - t) + b[idx][:, None, :] * t
        xs = np.rint(pts[:, :, 0]).astype(np.int64).ravel()
        ys = np.rint(pts[:, :, 1]).astype(np.int64).ravel()
        zs = pts[:, :, 2].ravel()
        cols = np.repeat(colors[idx], n, axis=0)
        for dx, dy in offs:
            gx, gy = xs + dx, ys + dy
            ok = (gx >= 0) & (gx < size) & (gy >= 0) & (gy < size)
            if depth_test:
                ok &= zs >= zbuf[np.clip(gy, 0, size - 1),
                                 np.clip(gx, 0, size - 1)] - 1e-9
            if not ok.any():
                continue
            if alpha >= 1.0:
                img[gy[ok], gx[ok]] = cols[ok]
            else:
                # Blend, so a thicket of overlapping boxes stays translucent
                # instead of flooding to solid white.
                yy, xx = gy[ok], gx[ok]
                img[yy, xx] = (1.0 - alpha) * img[yy, xx] + alpha * cols[ok]


def box_segments(boxes) -> np.ndarray:
    """The 12 edges of each axis-aligned box, as ``(12k,2,3)`` segments.

    ``boxes`` is an iterable of ``(min_corner, max_corner)`` pairs.
    """
    EDGES = [(0, 1), (1, 3), (3, 2), (2, 0),        # min-z face
             (4, 5), (5, 7), (7, 6), (6, 4),        # max-z face
             (0, 4), (1, 5), (2, 6), (3, 7)]        # the four uprights
    out = []
    for lo, hi in boxes:
        lo = np.asarray(lo, dtype=float)
        hi = np.asarray(hi, dtype=float)
        if not (np.all(np.isfinite(lo)) and np.all(np.isfinite(hi))):
            continue
        corner = np.array([[lo[0] if not (k & 4) else hi[0],
                            lo[1] if not (k & 2) else hi[1],
                            lo[2] if not (k & 1) else hi[2]] for k in range(8)])
        for i, j in EDGES:
            out.append([corner[i], corner[j]])
    return (np.asarray(out, dtype=float) if out
            else np.zeros((0, 2, 3), dtype=float))


def mesh_edges(V, F) -> np.ndarray:
    """Every unique polygon edge of a mesh, as ``(k,2,3)`` segments.

    Faces are used exactly as given: a quad contributes its four sides and
    *not* the diagonal that triangulating it would introduce, so a quad cage
    (a subdivision control mesh, say) draws as the quad cage it is. For a
    triangle mesh this is the same set of edges as before.
    """
    V = np.asarray(V, dtype=float)
    F = np.asarray(F)
    if F.size == 0:
        return np.zeros((0, 2, 3), dtype=float)
    if F.ndim == 2:
        k = F.shape[1]
        pairs = np.concatenate(
            [np.stack([F[:, i], F[:, (i + 1) % k]], axis=1) for i in range(k)])
    else:                                   # ragged: mixed polygon sizes
        acc = []
        for face in F:
            idx = [int(i) for i in np.asarray(face).ravel()]
            acc += [[idx[i], idx[(i + 1) % len(idx)]] for i in range(len(idx))]
        pairs = np.asarray(acc, dtype=int)
    pairs = np.unique(np.sort(pairs.astype(int), axis=1), axis=0)
    return np.stack([V[pairs[:, 0]], V[pairs[:, 1]]], axis=1)


def fit_camera(frames, view=(0.0, 0.0, 1.0), margin=1.12):
    """Find one camera that frames *every* pose in ``frames``.

    ``frames`` is an iterable of ``(n,3)`` vertex arrays -- one per frame of an
    animation, or simply every object in a static scene. Returns
    ``(center, extent)`` to hand to :func:`render_mesh`, chosen so the union of
    all the geometry fits with a little room to spare and the camera never
    moves.
    """
    R = look_at_rotation(view)
    lo = np.array([np.inf, np.inf])
    hi = np.array([-np.inf, -np.inf])
    for V in frames:
        V = np.asarray(V, dtype=float)
        if V.size == 0:
            continue
        P = (V @ R.T)[:, :2]
        lo = np.minimum(lo, P.min(axis=0))
        hi = np.maximum(hi, P.max(axis=0))
    if not np.all(np.isfinite(lo)):
        return [0.0, 0.0, 0.0], 1.0
    cx, cy = 0.5 * (lo + hi)
    half = 0.5 * float((hi - lo).max()) * margin
    # Map the camera-space centre back to a world point (R's rows are the
    # camera's right/up/forward axes, so this is just a change of basis).
    center = cx * R[0] + cy * R[1]
    return center.tolist(), (half or 1.0)


def render_mesh_png(path, V, F, colors, **kwargs):
    """Rasterise a mesh and save it as a .png."""
    from cgcommon.image import save_png

    img = render_mesh(V, F, colors, **kwargs)
    save_png(path, img)
    return img
