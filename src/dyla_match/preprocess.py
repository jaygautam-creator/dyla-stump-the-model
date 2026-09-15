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

    ys, xs = np.where(mask)
    y0, y1 = int(ys.min()), int(ys.max())
    x0, x1 = int(xs.min()), int(xs.max())
    pad_y = int((y1 - y0) * pad_frac)
    pad_x = int((x1 - x0) * pad_frac)
    y0 = max(0, y0 - pad_y)
    y1 = min(h, y1 + pad_y)
    x0 = max(0, x0 - pad_x)
    x1 = min(w, x1 + pad_x)
    if y1 <= y0 or x1 <= x0:
        return image
    return image.crop((x0, y0, x1, y1))
