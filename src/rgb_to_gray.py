import numpy as np


def rgb_to_gray(rgb):
    """Convert an RGB image to grayscale with a perceptual weighted average.

    Uses the luminance weights that account for the human eye being most
    sensitive to green::

        gray = 0.2126 * R + 0.7152 * G + 0.0722 * B

    Parameters
    ----------
    rgb : (H, W, 3) uint8 array

    Returns
    -------
    (H, W) uint8 array.
    """
    # TODO: compute the weighted sum of the R, G, B channels (work in float,
    #       then convert back to uint8).
    raise NotImplementedError("Implement rgb_to_gray")
