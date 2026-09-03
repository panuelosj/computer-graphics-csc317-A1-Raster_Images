import numpy as np


def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB. Inputs and outputs may be scalars or numpy arrays.

    Parameters
    ----------
    h : float or array, hue in degrees ``[0, 360)``
    s, v : float or array in ``[0, 1]``

    Returns
    -------
    (r, g, b) each in ``[0, 1]``.

    Hints
    -----
    With chroma ``C = v * s``, ``hh = h / 60`` and
    ``X = C * (1 - |hh mod 2 - 1|)``, the (r,g,b) before adding the lightness
    ``m = v - C`` are a piecewise function of which unit interval ``hh`` falls
    in. :func:`numpy.select` is handy for the six cases.
    """
    # TODO: implement the HSV -> RGB conversion (vectorized with numpy).
    raise NotImplementedError("Implement hsv_to_rgb")
