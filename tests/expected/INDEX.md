# Public test data: A1-Raster_Images

These are the exact arrays the public unit checks compare your
functions against — the inputs they feed in and the outputs they
expect back. Everything here is generated from
`a1_golden.npz`; nothing here is secret, and you
are meant to look at it when a check fails.

* `arrays/<name>.txt` — the values, in readable form.
* `images/<name>.png` — the same array as a viewable image, for
  the entries that are pictures.

To load an array yourself:

```python
import numpy as np
g = np.load('tests/golden/a1_golden.npz')
print(g.files)          # every available name
img = g['<name>']       # one array
```

Regenerate this folder with `python export_expected.py <assignment>` from the repository root.

| entry | what it is | values | picture |
|---|---|---|---|
| `B4` | shape (6, 5, 4), dtype uint8, range [0, 255] | [B4.txt](arrays/B4.txt) | [view](images/B4.png) |
| `demosaic` | shape (24, 24, 3), dtype uint8, range [7, 246] | [demosaic.txt](arrays/demosaic.txt) | [view](images/demosaic.png) |
| `demosaic_bayer` | shape (24, 24), dtype uint8, range [7, 246] | [demosaic_bayer.txt](arrays/demosaic_bayer.txt) | [view](images/demosaic_bayer.png) |
| `demosaic_clean` | shape (24, 24, 3), dtype uint8, range [7, 246] | [demosaic_clean.txt](arrays/demosaic_clean.txt) | [view](images/demosaic_clean.png) |
| `desaturate` | shape (6, 5, 3), dtype uint8, range [19, 248] | [desaturate.txt](arrays/desaturate.txt) | [view](images/desaturate.png) |
| `desaturate_factor` | shape (), dtype float64, range [0.25, 0.25] | [desaturate_factor.txt](arrays/desaturate_factor.txt) | — |
| `hsv_in` | shape (8, 3), dtype float64, range [0.058568, 320.216] | [hsv_in.txt](arrays/hsv_in.txt) | — |
| `hsv_rgb_in` | shape (7, 3), dtype float64, range [0, 1] | [hsv_rgb_in.txt](arrays/hsv_rgb_in.txt) | — |
| `hsv_to_rgb` | shape (8, 3), dtype float64, range [0.00642642, 0.876484] | [hsv_to_rgb.txt](arrays/hsv_to_rgb.txt) | — |
| `hue_shift` | shape (6, 5, 3), dtype uint8, range [0, 248] | [hue_shift.txt](arrays/hue_shift.txt) | [view](images/hue_shift.png) |
| `hue_shift_deg` | shape (), dtype float64, range [180, 180] | [hue_shift_deg.txt](arrays/hue_shift_deg.txt) | — |
| `img3` | shape (6, 5, 3), dtype uint8, range [0, 248] | [img3.txt](arrays/img3.txt) | [view](images/img3.png) |
| `img4` | shape (6, 5, 4), dtype uint8, range [0, 248] | [img4.txt](arrays/img4.txt) | [view](images/img4.png) |
| `over` | shape (6, 5, 4), dtype uint8, range [0, 255] | [over.txt](arrays/over.txt) | [view](images/over.png) |
| `reflect3` | shape (6, 5, 3), dtype uint8, range [0, 248] | [reflect3.txt](arrays/reflect3.txt) | [view](images/reflect3.png) |
| `rgb_to_gray` | shape (6, 5), dtype uint8, range [41, 242] | [rgb_to_gray.txt](arrays/rgb_to_gray.txt) | [view](images/rgb_to_gray.png) |
| `rgb_to_hsv` | shape (7, 3), dtype float64, range [0, 240] | [rgb_to_hsv.txt](arrays/rgb_to_hsv.txt) | — |
| `rgba_to_rgb` | shape (6, 5, 3), dtype uint8, range [0, 248] | [rgba_to_rgb.txt](arrays/rgba_to_rgb.txt) | [view](images/rgba_to_rgb.png) |
| `rotate3` | shape (5, 6, 3), dtype uint8, range [0, 248] | [rotate3.txt](arrays/rotate3.txt) | [view](images/rotate3.png) |
| `simulate_bayer_mosaic` | shape (6, 5), dtype uint8, range [7, 245] | [simulate_bayer_mosaic.txt](arrays/simulate_bayer_mosaic.txt) | [view](images/simulate_bayer_mosaic.png) |
