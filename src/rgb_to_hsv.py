import numpy as np


def rgb_to_hsv(r, g, b):
    """Convert RGB to HSV. Inputs and outputs may be scalars or numpy arrays.

    Parameters
    ----------
    r, g, b : float or array, each in ``[0, 1]``

    Returns
    -------
    (h, s, v) where hue ``h`` is in degrees ``[0, 360)`` and saturation ``s``
    and value ``v`` are in ``[0, 1]``.

    Hints
    -----
    Let ``M = max(r,g,b)``, ``m = min(r,g,b)`` and chroma ``C = M - m``.
    * ``v = M``
    * ``s = C / v`` (or 0 when ``v == 0``)
    * the hue depends on which channel is the maximum (see the reading).
    Write it vectorized with :func:`numpy.where` so it can process a whole
    image channel-array at once, and guard against dividing by zero when
    ``C == 0``.
    """
    # TODO: implement the RGB -> HSV conversion (vectorized with numpy).
    raise NotImplementedError("Implement rgb_to_hsv")
