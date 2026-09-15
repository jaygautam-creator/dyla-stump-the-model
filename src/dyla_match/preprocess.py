"""Crop-to-object preprocessing (Phase 5): the whole-image weakness PLAN.md predicted and Phase 4
diagnosed directly -- the kadda's own clean photo didn't rank in the top 30 against Swashaa's studio
photo, because a small object on a big plain background dilutes the embedding with background pixels.

No object detector -- 8GB RAM, no time budget to add a model, and it isn't needed here: every stumper
photo and every catalogue product photo is a single item on a plain surface. Background-subtraction
via the image corners (assumed background) against a brightness threshold is enough, and it's simple
enough to explain and change live. Falls back to the untouched image whenever the foreground fraction
looks wrong (near-0 = no object found, near-1 = no plain background to subtract, e.g. a busy lifestyle
catalogue shot) rather than risk cropping something wrongly.
"""
import numpy as np
from PIL import Image


def _largest_dense_run(density: np.ndarray, frac_of_max: float = 0.3) -> tuple[int, int]:
    """Largest contiguous stretch where a 1-D density profile stays above a fraction of its own peak.

    A plain min/max over every foreground pixel's coordinates breaks badly on a phone photo with
    scattered background noise (shadows, dust, a stray dark patch far from the item) -- a handful of
    outlier pixels near a far corner blow the bounding box out to nearly the whole frame. This is the
    axis-aligned stand-in for "find the main connected blob" without pulling in scipy for one function.
    """
    threshold = density.max() * frac_of_max
    above = density > threshold
    best_start = best_len = cur_start = cur_len = 0
    for i, v in enumerate(above):
        if v:
            if cur_len == 0:
                cur_start = i
            cur_len += 1
            if cur_len > best_len:
                best_len, best_start = cur_len, cur_start
        else:
            cur_len = 0
    return best_start, best_start + best_len


def object_crop(image: Image.Image, pad_frac: float = 0.12, min_frac: float = 0.015, max_frac: float = 0.92) -> Image.Image:
    arr = np.asarray(image.convert("L"), dtype=np.float32)
    h, w = arr.shape
    border = max(2, min(h, w) // 40)
    corners = np.concatenate([
        arr[:border, :border].ravel(), arr[:border, -border:].ravel(),
        arr[-border:, :border].ravel(), arr[-border:, -border:].ravel(),
    ])
    bg = float(np.median(corners))
    diff = np.abs(arr - bg)
    thresh = max(15.0, float(diff.std()) * 1.5)
    mask = diff > thresh

    frac = float(mask.mean())
    if frac < min_frac or frac > max_frac:
        return image

    y0, y1 = _largest_dense_run(mask.mean(axis=1))
    x0, x1 = _largest_dense_run(mask.mean(axis=0))
    min_side = 20  # guards against a degenerate few-pixel-wide crop on a near-uniform or noisy image
    if y1 - y0 < min_side or x1 - x0 < min_side:
        return image

    pad_y = int((y1 - y0) * pad_frac)
    pad_x = int((x1 - x0) * pad_frac)
    y0 = max(0, y0 - pad_y)
    y1 = min(h, y1 + pad_y)
    x0 = max(0, x0 - pad_x)
    x1 = min(w, x1 + pad_x)
    if y1 <= y0 or x1 <= x0:
        return image
    return image.crop((x0, y0, x1, y1))
