import numpy as np


def rgba_to_rgb(rgba):
    """Drop the alpha channel of an RGBA image.

    Parameters
    ----------
    rgba : (H, W, 4) uint8 array

    Returns
    -------
    (H, W, 3) uint8 array containing only the red, green and blue channels.
    """
    # TODO: return just the first three channels of `rgba`.
    raise NotImplementedError("Implement rgba_to_rgb")
