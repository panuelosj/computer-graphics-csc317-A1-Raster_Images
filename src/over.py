import numpy as np


def over(A, B):
    """Composite RGBA image ``A`` over RGBA image ``B`` (Porter-Duff "over").

    For each pixel, with coverage (alpha) blending::

        Ca = Aa + Ba * (1 - Aa)
        Cc = (Aa * Ac + Ba * (1 - Aa) * Bc) / Ca     (use 0 where Ca == 0)

    where ``Aa``/``Ba`` are the alphas in [0,1] and ``Ac``/``Bc`` are colour
    channels.

    Parameters
    ----------
    A, B : (H, W, 4) uint8 arrays. ``A`` is the foreground layer.

    Returns
    -------
    (H, W, 4) uint8 array.
    """
    # TODO: implement the Porter-Duff over operator (guard against Ca == 0).
    raise NotImplementedError("Implement over")
