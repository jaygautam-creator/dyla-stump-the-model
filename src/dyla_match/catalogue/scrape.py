"""Build the jewellery catalogue from public Shopify storefronts.

Giva and Palmonas both expose the standard Shopify `/products.json` endpoint (checked their
robots.txt first: neither disallows it). This script paginates that feed, downloads every product
image, resizes it to keep disk use down on an 8 GB machine, and writes one row per (product, image)
to data/catalogue/products.csv with the original source URL kept for every image.

Usage:
    python -m dyla_match.catalogue.scrape --shop giva --out data/catalogue
    python -m dyla_match.catalogue.scrape --shop palmonas --out data/catalogue
"""
import argparse
import csv
import re
import time
from pathlib import Path

import requests
from PIL import Image

SHOPS = {
    "giva": "https://www.giva.co",
    "palmonas": "https://palmonas.com",
    "swashaa": "https://www.swashaa.com",
}

USER_AGENT = "dyla-takehome-catalogue-builder/0.1 (personal project, jaygautam561@gmail.com)"
PAGE_LIMIT = 250          # Shopify's max page size for /products.json
REQUEST_DELAY_S = 1.0     # be polite — one request per second per shop
MAX_IMAGE_SIDE = 512      # resize long side to this before saving (disk budget on an 8GB machine)


def fetch_all_products(base_url: str) -> list[dict]:
    products, page = [], 1
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    while True:
        resp = session.get(f"{base_url}/products.json", params={"limit": PAGE_LIMIT, "page": page}, timeout=15)
        resp.raise_for_status()
        batch = resp.json().get("products", [])
        if not batch:
            break
        products.extend(batch)
        print(f"  page {page}: {len(batch)} products (total {len(products)})")
        page += 1
        time.sleep(REQUEST_DELAY_S)
    return products


def fetch_product_by_handle(base_url: str, handle: str) -> dict:
    """Fetch one specific product by its URL handle, instead of paginating the whole catalogue.

    Used when a particular real-world item needs to be in the catalogue (its exact SKU is known
    from the product page URL) without scraping the vendor's entire listing to reach it — e.g. a
    stumper item whose product happens to sit near the end of a 1,800+ product catalogue.
    """
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    resp = session.get(f"{base_url}/products/{handle}.json", timeout=15)
    resp.raise_for_status()
    return resp.json()["product"]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]


def download_and_resize(url: str, dest: Path, session: requests.Session, retries: int = 2) -> bool:
    if dest.exists():
        return True
    for attempt in range(retries + 1):
        try:
            resp = session.get(url, timeout=30)
        except requests.exceptions.RequestException:
            if attempt == retries:
                return False
            time.sleep(1.0)
            continue
        if resp.status_code != 200:
            return False
        break
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    tmp.write_bytes(resp.content)
    try:
        img = Image.open(tmp).convert("RGB")
        img.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE), Image.LANCZOS)
        img.save(dest, "JPEG", quality=90)
    finally:
        tmp.unlink(missing_ok=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shop", choices=SHOPS.keys(), required=True)
    ap.add_argument("--out", default="data/catalogue")
    ap.add_argument("--limit-products", type=int, default=None, help="cap for a quick test run")
    ap.add_argument("--handle", default=None, help="fetch one specific product by its URL handle, not the full list")
    args = ap.parse_args()

    out_dir = Path(args.out)
    images_dir = out_dir / "images"
    csv_path = out_dir / "products.csv"
    base_url = SHOPS[args.shop]

    if args.handle:
        print(f"Fetching single product '{args.handle}' from {base_url} ...")
        products = [fetch_product_by_handle(base_url, args.handle)]
    else:
        print(f"Fetching product list from {base_url} ...")
        products = fetch_all_products(base_url)
        if args.limit_products:
            products = products[: args.limit_products]
    print(f"{len(products)} products found for {args.shop}")

    out_dir.mkdir(parents=True, exist_ok=True)
    base_fieldnames = [
        "vendor", "product_id", "sku", "title", "product_type", "handle",
        "price", "product_url", "image_id", "image_position", "image_source_url", "local_path",
    ]
    if csv_path.exists():
        # groups.py may have already added design_group to an existing file — match its shape
        # (as a blank field for new rows) rather than writing a shorter row and corrupting the CSV.
        with open(csv_path) as f:
            fieldnames = next(csv.reader(f))
        write_header = False
    else:
        fieldnames = base_fieldnames
        write_header = True
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        n_images = 0
        for p in products:
            sku = (p.get("variants") or [{}])[0].get("sku", "")
            price = (p.get("variants") or [{}])[0].get("price", "")
            product_url = f"{base_url}/products/{p['handle']}"
            for img in p.get("images", []):
                local_name = f"{args.shop}_{p['id']}_{img['id']}.jpg"
                local_path = images_dir / local_name
                ok = download_and_resize(img["src"], local_path, session)
                if not ok:
                    continue
                row = {
                    "vendor": args.shop, "product_id": p["id"], "sku": sku, "title": p["title"],
                    "product_type": p.get("product_type", ""), "handle": p["handle"], "price": price,
                    "product_url": product_url, "image_id": img["id"], "image_position": img.get("position", ""),
                    "image_source_url": img["src"], "local_path": str(local_path.relative_to(out_dir)),
                }
                writer.writerow(row)
                n_images += 1
                if n_images % 100 == 0:
                    print(f"  ... {n_images} images downloaded")
                time.sleep(0.1)  # gentle on the CDN too

    print(f"Done. {n_images} images written for {args.shop}. See {csv_path}")


if __name__ == "__main__":
    main()
