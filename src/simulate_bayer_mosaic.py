import numpy as np


def simulate_bayer_mosaic(rgb):
    """Sample a single colour per pixel following the GBRG Bayer pattern.

    The pattern over a 2x2 tile (top-left pixel at an even row and column) is::

        G B
        R G

    i.e. even rows: even columns keep Green, odd columns keep Blue; odd rows:
    even columns keep Red, odd columns keep Green.

    Parameters
    ----------
    rgb : (H, W, 3) uint8 array

    Returns
    -------
    (H, W) uint8 single-channel "mosaic" image.

    Hint: numpy strided slicing such as ``rgb[0::2, 1::2, 2]`` selects every
    other pixel.
    """
    # TODO: build the (H, W) mosaic by selecting the correct channel per pixel.
    raise NotImplementedError("Implement simulate_bayer_mosaic")
