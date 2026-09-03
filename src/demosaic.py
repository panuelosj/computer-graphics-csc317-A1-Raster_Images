import numpy as np


def demosaic(bayer):
    """Reconstruct a full RGB image from a GBRG Bayer mosaic.

    For each pixel keep the colour that was actually sampled, and fill in the
    two missing colours by averaging the available neighbours (the 4 cardinal
    neighbours for a "cross" estimate and the 4 diagonal neighbours for an "x"
    estimate). Pixels on the image boundary should just average whatever
    neighbours exist ("do something reasonable").

    Parameters
    ----------
    bayer : (H, W) uint8 array following the GBRG pattern.

    Returns
    -------
    (H, W, 3) uint8 RGB array.

    Hint: work in float, build small helpers for the cross / diagonal /
    horizontal / vertical neighbour averages, then loop over the four pixel
    types (even/even, even/odd, odd/even, odd/odd).
    """
    # TODO: implement linear-interpolation demosaicing.
    raise NotImplementedError("Implement demosaic")
