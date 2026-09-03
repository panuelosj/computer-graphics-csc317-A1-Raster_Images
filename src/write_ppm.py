import numpy as np


def write_ppm(filename, data):
    """Write an image to a plain-text ``.ppm`` file (P2 grayscale or P3 RGB).

    Parameters
    ----------
    filename : str
        Output path.
    data : (H, W) or (H, W, 3) uint8 array
        Grayscale or RGB image with intensities in ``[0, 255]``.

    The required file format is::

        P3            (use "P2" for a single-channel grayscale image)
        <width> <height>
        255
        r g b  r g b  ...   (whitespace-separated integers, one row per line)

    Hint: open the file in text mode and write the header, then loop over rows.
    """
    # TODO: choose "P2" (grayscale, data.ndim == 2) or "P3" (RGB), write the
    #       header (magic, width/height, max value 255), then the pixel values.
    raise NotImplementedError("Implement write_ppm")
