import numpy as np


def rotate(input):
    """Rotate an image 90 degrees counter-clockwise.

    Parameters
    ----------
    input : (H, W) or (H, W, C) array

    Returns
    -------
    Array of shape (W, H) / (W, H, C). The output pixel ``out[j, i]`` should
    equal the input pixel ``input[i, W-1-j]``.
    """
    # TODO: produce the 90-degree counter-clockwise rotation. You can do this
    #       with slicing + an axis swap, or with numpy's rotation helper.
    raise NotImplementedError("Implement rotate")
