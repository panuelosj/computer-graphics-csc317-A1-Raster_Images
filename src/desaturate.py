import numpy as np

from .rgb_to_hsv import rgb_to_hsv
from .hsv_to_rgb import hsv_to_rgb


def desaturate(rgb, factor):
    """Reduce the saturation of every pixel by ``factor``.

    Parameters
    ----------
    rgb : (H, W, 3) uint8 array
    factor : float in ``[0, 1]``
        ``0`` leaves the image unchanged; ``1`` makes it fully gray. Multiply
        each pixel's saturation by ``(1 - factor)``.

    Returns
    -------
    (H, W, 3) uint8 array.
    """
    # TODO: implement using rgb_to_hsv / hsv_to_rgb, scaling the saturation.
    raise NotImplementedError("Implement desaturate")
