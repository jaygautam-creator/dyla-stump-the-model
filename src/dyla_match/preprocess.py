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


def _dense_extent(density: np.ndarray, frac_of_max: float = 0.3, min_run_frac: float = 0.02) -> tuple[int, int]:
    """Union bounding extent of every run where a 1-D density profile clears a fraction of its peak.

    A plain min/max over every foreground pixel's coordinates breaks on scattered background noise
    (a handful of outlier pixels near a far corner blow the bbox out to nearly the whole frame) -- fixed
    by only counting *runs*, not individual pixels. But taking just the single *largest* run (the first
    version of this function) breaks differently on annular jewellery (rings, bangles, hoop earrings):
    the hollow centre makes the density profile dip in the middle, so "largest run" picks one rim and
    discards the other, bisecting the item into a degenerate sliver (found via an independent audit,
    2026-09-15, see docs/ANTIGRAVITY_AUDIT.md -- a ring catalogue image cropped to 203x132 as a plain
    bbox but a bangle image cropped to 56x269 once it had a real hollow centre). Taking the union extent
    of every run that clears `min_run_frac` (filtering short noise blips, not the whole rim) spans the
    full item including its hollow centre.
    """
    n = len(density)
    threshold = density.max() * frac_of_max
    min_run = max(1, int(n * min_run_frac))
    above = density > threshold
    runs = []
    cur_start = cur_len = 0
    for i, v in enumerate(above):
        if v:
            if cur_len == 0:
                cur_start = i
            cur_len += 1
        else:
            if cur_len >= min_run:
                runs.append((cur_start, cur_start + cur_len))
            cur_len = 0
    if cur_len >= min_run:
        runs.append((cur_start, cur_start + cur_len))
    if not runs:
        return 0, 0
    return min(r[0] for r in runs), max(r[1] for r in runs)


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

    y0, y1 = _dense_extent(mask.mean(axis=1))
    x0, x1 = _dense_extent(mask.mean(axis=0))
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
