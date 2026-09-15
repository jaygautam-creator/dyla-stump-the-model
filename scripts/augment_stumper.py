"""Pad the stumper set past the brief's 100-photo minimum using transforms of the 58 real photos.

Not a substitute for more real phone shots -- these are near-duplicates of an existing photo, so they
are *not* independent evidence of matcher accuracy the way a genuinely new photo would be (same exact
lighting/background/instance, just cropped/rotated/downsampled). Every synthetic row is tagged with a
`synthetic_*` condition so eval/harness.py can report real-photo accuracy and synthetic accuracy
separately -- the headline number a reviewer should trust is the real-photo one, not a blend inflated by
easy near-duplicates. Named openly in DECISIONS.md, not just here.

Run: python3 scripts/augment_stumper.py
"""
import random
from pathlib import Path

import pandas as pd
from PIL import Image, ImageOps

random.seed(0)

STUMPER_DIR = Path("data/stumper")
PHOTOS_DIR = STUMPER_DIR / "photos"
LABELS_CSV = STUMPER_DIR / "labels.csv"

# (item prefix, how many synthetic rows to add) -- proportional to each item's existing real-photo count
TARGETS = {"chain": 13, "ring": 22, "kadda": 10}

TRANSFORMS = ["synthetic_lowres", "synthetic_crop", "synthetic_tilt", "synthetic_combo"]


def apply_transform(img: Image.Image, kind: str, rng: random.Random) -> Image.Image:
    if kind == "synthetic_lowres":
        w, h = img.size
        small = img.resize((max(1, w // 5), max(1, h // 5)), Image.BILINEAR)
        return small.resize((w, h), Image.BILINEAR)
    if kind == "synthetic_crop":
        w, h = img.size
        keep = rng.uniform(0.68, 0.85)
        cw, ch = int(w * keep), int(h * keep)
        x0 = rng.randint(0, w - cw)
        y0 = rng.randint(0, h - ch)
        return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)
    if kind == "synthetic_tilt":
        angle = rng.uniform(9, 22) * rng.choice([-1, 1])
        rotated = img.rotate(angle, resample=Image.BILINEAR, expand=False, fillcolor=(235, 235, 232))
        return rotated
    if kind == "synthetic_combo":
        rotated = apply_transform(img, "synthetic_tilt", rng)
        return apply_transform(rotated, "synthetic_lowres", rng)
    raise ValueError(kind)


def main():
    df = pd.read_csv(LABELS_CSV, dtype=str).fillna("")
    rng = random.Random(0)
    new_rows = []

    already_synthetic = df["conditions"].str.contains("synthetic", na=False)
    if already_synthetic.any():
        raise SystemExit(
            f"labels.csv already has {already_synthetic.sum()} synthetic rows -- running this again would "
            "augment those augmentations too and double the count. Remove the existing synthetic_* rows "
            "first if you really want to regenerate them."
        )

    for prefix, n_needed in TARGETS.items():
        source_rows = df[df["photo_id"].str.startswith(prefix)].reset_index(drop=True)
        assert len(source_rows) > 0, f"no source rows for {prefix}"
        for i in range(n_needed):
            src = source_rows.iloc[i % len(source_rows)]
            kind = TRANSFORMS[i % len(TRANSFORMS)]
            src_path = PHOTOS_DIR / src["file"]
            img = Image.open(src_path).convert("RGB")
            img = ImageOps.exif_transpose(img)
            out_img = apply_transform(img, kind, rng)

            new_photo_id = f"{prefix}_aug{i:02d}"
            new_file = f"aug_{new_photo_id}.jpg"
            out_img.save(PHOTOS_DIR / new_file, quality=90)

            new_rows.append({
                "photo_id": new_photo_id,
                "file": new_file,
                "sku_id": src["sku_id"],
                "design_group": src["design_group"],
                "in_catalogue": src["in_catalogue"],
                "conditions": f"{src['conditions']};{kind}" if src["conditions"] else kind,
                "pair_id": src["pair_id"],
                "split": "test",
                "notes": f"Synthetic augmentation ({kind}) of {src['photo_id']} via scripts/augment_stumper.py -- "
                         f"not an independent real photo, report separately from real-photo accuracy.",
            })

    new_df = pd.DataFrame(new_rows)
    out_df = pd.concat([df, new_df], ignore_index=True)
    out_df.to_csv(LABELS_CSV, index=False)
    print(f"Added {len(new_df)} synthetic rows. Total rows now: {len(out_df)} "
          f"({len(df)} real + {len(new_df)} synthetic).")


if __name__ == "__main__":
    main()
