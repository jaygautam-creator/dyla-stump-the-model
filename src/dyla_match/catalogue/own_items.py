"""Register a zero-cost, self-sourced item as a catalogue entry.

Used for the 3 home jewellery pieces (gold ring, chain, kadda) that stand in for a purchased item:
no receipt, no known brand, so there's no scraped catalogue to match them against. Instead each one
gets added here as its own catalogue entry, with the one clean reference photo taken for it acting as
what a scraped studio photo would be. See docs/SHOT_LIST.md and docs/DECISION_LOG.md ("D1 superseded").

This does not touch the scraped Giva/Palmonas rows — it only appends. Run `dyla-match build-index`
afterwards so the new item is actually searchable.

Usage:
    python -m dyla_match.catalogue.own_items --title "Gold Ring" --category ring --photo path/to/photo.jpg
"""
import argparse
import csv
import re
from pathlib import Path

from PIL import Image

MAX_IMAGE_SIDE = 512  # match scrape.py's disk budget


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]


def add_own_item(title: str, category: str, photo_path: Path, catalogue_dir: Path) -> None:
    csv_path = catalogue_dir / "products.csv"
    images_dir = catalogue_dir / "images"
    slug = slugify(title)
    product_id = f"own-{slug}"
    image_id = f"own-{slug}-1"
    local_name = f"own_{slug}.jpg"
    local_path = images_dir / local_name

    images_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(photo_path).convert("RGB")
    img.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE), Image.LANCZOS)
    img.save(local_path, "JPEG", quality=90)

    rows = list(csv.DictReader(open(csv_path))) if csv_path.exists() else []
    fieldnames = list(rows[0].keys()) if rows else [
        "vendor", "product_id", "sku", "title", "product_type", "handle",
        "price", "product_url", "image_id", "image_position", "image_source_url",
        "local_path", "design_group",
    ]
    if any(r["vendor"] == "own" and r["product_id"] == product_id for r in rows):
        raise ValueError(f"'{title}' (product_id={product_id}) is already registered")

    rows.append({
        "vendor": "own",
        "product_id": product_id,
        "sku": "",
        "title": title,
        "product_type": category,
        "handle": slug,
        "price": "",
        "product_url": "",
        "image_id": image_id,
        "image_position": 1,
        "image_source_url": "",
        "local_path": str(local_path.relative_to(catalogue_dir)),
        "design_group": f"own_dg_{slug}",
    })

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Added '{title}' as {product_id} -> {local_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True, help='e.g. "Gold Ring"')
    ap.add_argument("--category", required=True, help='e.g. "ring", "chain", "bracelet"')
    ap.add_argument("--photo", required=True, type=Path, help="path to the one clean reference photo")
    ap.add_argument("--catalogue", default="data/catalogue")
    args = ap.parse_args()
    add_own_item(args.title, args.category, args.photo, Path(args.catalogue))


if __name__ == "__main__":
    main()
