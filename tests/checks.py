"""Unit checks for Assignment 1 (Raster Images).

Each check exercises one function in ``src/`` against the golden fixtures in
``tests/golden/a1_golden.npz``. The same checks are used by ``run_tests.py``
(for students) and by the grader. Marks per check mirror the marking scheme.
"""

import os

import numpy as np

from cgcommon.testkit import Check, fixture_path
from cgcommon.imagediff import report as _image_report

ASSIGN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_GOLDEN = None


def golden():
    global _GOLDEN
    if _GOLDEN is None:
        path = fixture_path(
            os.path.join(os.path.dirname(__file__), "golden", "a1_golden.npz")
        )
        _GOLDEN = np.load(path)
    return _GOLDEN


def _param(g, key, default):
    """Read a scalar test parameter from the fixture, if it carries one.

    The public and private fixtures use *different* parameter values (e.g. the
    hue-shift angle), so an implementation that special-cases the public
    numbers will not survive grading.
    """
    return float(g[key]) if key in g.files else default


def _assert_uint8_close(got, expected, atol, msg):
    """Compare two uint8 images, writing a visual diff when they disagree."""
    got = np.asarray(got)
    expected = np.asarray(expected)
    name = msg.split()[0].strip("():")
    if got.shape != expected.shape:
        raise AssertionError(
            f"{msg}: wrong shape {got.shape}, expected {expected.shape}"
            + _image_report(name, got, expected, ASSIGN)
        )
    diff = np.abs(got.astype(np.int64) - expected.astype(np.int64))
    if diff.max() > atol:
        raise AssertionError(
            f"{msg}: values differ by up to {int(diff.max())} (allowed {atol})"
            + _image_report(name, got, expected, ASSIGN)
        )


# --- individual checks ------------------------------------------------------

def check_rgba_to_rgb():
    from src.rgba_to_rgb import rgba_to_rgb
    g = golden()
    _assert_uint8_close(rgba_to_rgb(g["img4"]), g["rgba_to_rgb"], 0, "rgba_to_rgb")


def check_write_ppm():
    import tempfile
    from src.write_ppm import write_ppm
    from cgcommon.image import read_ppm
    g = golden()
    with tempfile.TemporaryDirectory() as d:
        # RGB -> P3
        p3 = os.path.join(d, "rgb.ppm")
        write_ppm(p3, g["img3"])
        with open(p3) as f:
            assert f.read(2) == "P3", "write_ppm: RGB image must start with P3"
        _assert_uint8_close(read_ppm(p3), g["img3"], 0, "write_ppm (RGB round-trip)")
        # grayscale -> P2
        p2 = os.path.join(d, "gray.ppm")
        write_ppm(p2, g["rgb_to_gray"])
        with open(p2) as f:
            assert f.read(2) == "P2", "write_ppm: grayscale image must start with P2"
        _assert_uint8_close(read_ppm(p2), g["rgb_to_gray"], 0, "write_ppm (gray round-trip)")


def check_reflect():
    from src.reflect import reflect
    g = golden()
    _assert_uint8_close(reflect(g["img3"]), g["reflect3"], 0, "reflect")


def check_rotate():
    from src.rotate import rotate
    g = golden()
    _assert_uint8_close(rotate(g["img3"]), g["rotate3"], 0, "rotate")


def check_rgb_to_gray():
    from src.rgb_to_gray import rgb_to_gray
    g = golden()
    _assert_uint8_close(rgb_to_gray(g["img3"]), g["rgb_to_gray"], 1, "rgb_to_gray")


def check_rgb_to_hsv():
    from src.rgb_to_hsv import rgb_to_hsv
    g = golden()
    rgb_in = g["hsv_rgb_in"]
    h, s, v = rgb_to_hsv(rgb_in[:, 0], rgb_in[:, 1], rgb_in[:, 2])
    got = np.stack([np.asarray(h), np.asarray(s), np.asarray(v)], axis=-1)
    assert np.allclose(got, g["rgb_to_hsv"], atol=1e-4), (
        "rgb_to_hsv: output differs from expected on canonical colours"
    )


def check_hsv_to_rgb():
    from src.hsv_to_rgb import hsv_to_rgb
    g = golden()
    hsv_in = g["hsv_in"]
    r, gg, b = hsv_to_rgb(hsv_in[:, 0], hsv_in[:, 1], hsv_in[:, 2])
    got = np.stack([np.asarray(r), np.asarray(gg), np.asarray(b)], axis=-1)
    assert np.allclose(got, g["hsv_to_rgb"], atol=1e-4), (
        "hsv_to_rgb: output differs from expected"
    )


def check_hue_shift():
    from src.hue_shift import hue_shift
    g = golden()
    deg = _param(g, "hue_shift_deg", 180.0)
    _assert_uint8_close(hue_shift(g["img3"], deg), g["hue_shift"], 2, "hue_shift")


def check_desaturate():
    from src.desaturate import desaturate
    g = golden()
    f = _param(g, "desaturate_factor", 0.25)
    _assert_uint8_close(desaturate(g["img3"], f), g["desaturate"], 2, "desaturate")


def check_simulate_bayer_mosaic():
    from src.simulate_bayer_mosaic import simulate_bayer_mosaic
    g = golden()
    _assert_uint8_close(
        simulate_bayer_mosaic(g["img3"]), g["simulate_bayer_mosaic"], 0,
        "simulate_bayer_mosaic",
    )


def check_demosaic():
    from src.demosaic import demosaic
    g = golden()
    bayer = g["demosaic_bayer"]
    out = np.asarray(demosaic(bayer))
    assert out.shape == g["demosaic"].shape, "demosaic: wrong output shape"
    # Exact colour samples must be preserved at their GBRG positions.
    assert np.array_equal(out[0::2, 0::2, 1], bayer[0::2, 0::2]), \
        "demosaic: green sample not preserved at (even,even) pixels"
    assert np.array_equal(out[0::2, 1::2, 2], bayer[0::2, 1::2]), \
        "demosaic: blue sample not preserved at (even,odd) pixels"
    assert np.array_equal(out[1::2, 0::2, 0], bayer[1::2, 0::2]), \
        "demosaic: red sample not preserved at (odd,even) pixels"
    assert np.array_equal(out[1::2, 1::2, 1], bayer[1::2, 1::2]), \
        "demosaic: green sample not preserved at (odd,odd) pixels"
    # Reconstruction of a smooth image should be close to the reference.
    err = np.mean(np.abs(out.astype(np.int64) - g["demosaic"].astype(np.int64)))
    assert err < 4.0, f"demosaic: reconstruction too far from reference (mean abs err {err:.2f})"


def check_over():
    from src.over import over
    g = golden()
    _assert_uint8_close(over(g["img4"], g["B4"]), g["over"], 1, "over")


def get_checks():
    """Return the ordered list of checks for this assignment."""
    return [
        Check("rgba_to_rgb", 10, check_rgba_to_rgb, "drops the alpha channel"),
        Check("write_ppm", 10, check_write_ppm, "writes valid P2/P3 .ppm files"),
        Check("reflect", 10, check_reflect, "mirrors the image horizontally"),
        Check("rotate", 10, check_rotate, "rotates 90 degrees counter-clockwise"),
        Check("rgb_to_gray", 10, check_rgb_to_gray, "perceptual grayscale"),
        Check("rgb_to_hsv", 10, check_rgb_to_hsv, "RGB to HSV conversion"),
        Check("hsv_to_rgb", 10, check_hsv_to_rgb, "HSV to RGB conversion"),
        Check("hue_shift", 10, check_hue_shift, "rotates hue by 180 degrees"),
        Check("desaturate", 5, check_desaturate, "reduces saturation"),
        Check("simulate_bayer_mosaic", 5, check_simulate_bayer_mosaic, "GBRG mosaic"),
        Check("demosaic", 5, check_demosaic, "reconstructs RGB from mosaic"),
        Check("over", 5, check_over, "Porter-Duff over compositing"),
    ]
