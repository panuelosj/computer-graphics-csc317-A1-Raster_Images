import numpy as np

from .rgb_to_hsv import rgb_to_hsv
from .hsv_to_rgb import hsv_to_rgb


def hue_shift(rgb, shift):
    """Rotate the hue of every pixel by ``shift`` degrees.

    Parameters
    ----------
    rgb : (H, W, 3) uint8 array
    shift : float
        Amount in degrees to add to each pixel's hue (must wrap modulo 360).

    Returns
    -------
    (H, W, 3) uint8 array.

    Hint: convert to float in [0,1], use your ``rgb_to_hsv``, add ``shift`` to
    the hue (wrapping into [0,360)), convert back with ``hsv_to_rgb``, then
    scale to [0,255].
    """
    # TODO: implement using rgb_to_hsv / hsv_to_rgb.
    raise NotImplementedError("Implement hue_shift")
