"""Redownload catalogue images from the source URLs already recorded in products.csv.

`products.csv` (metadata only, ~1MB) is committed; the 7,272 images (~180MB) are gitignored per
`docs/PLAN.md`'s disk-budget note, so a fresh clone needs this to rebuild `data/catalogue/images/`
before an index can be built. Unlike `scrape.py` (which paginates each shop's live `/products.json`
feed at one request/second to be polite to the storefront's API), this only re-fetches static CDN
image files that are already known -- so it uses a small thread pool to make the README's <5-minute
clean-machine budget realistic. `--limit` builds a fast subset for a quick demo without the full
catalogue.

Usage:
    python -m scripts.hydrate_catalogue_images
    python -m scripts.hydrate_catalogue_images --limit 300   # quick subset for a fast demo
"""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from dyla_match.catalogue.scrape import USER_AGENT, download_and_resize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogue", default="data/catalogue")
    ap.add_argument("--limit", type=int, default=None, help="cap total images, for a quick demo subset")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    catalogue_dir = Path(args.catalogue)
    with open(catalogue_dir / "products.csv") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[: args.limit]

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    # products.csv has ~1,500 duplicate local_path rows (several product variants sharing one listing
    # image) -- dedupe by destination before submitting to the thread pool, or multiple workers race on
    # writing/reading the exact same file (see src/dyla_match/catalogue/scrape.py's atomic-write fix).
    seen_dest = set()
    to_fetch = []
    for r in rows:
        dest = catalogue_dir / r["local_path"]
        if dest not in seen_dest:
            seen_dest.add(dest)
            to_fetch.append((r["image_source_url"], dest))

    already = sum(1 for _, dest in to_fetch if dest.exists())
    missing_no_url = [dest for url, dest in to_fetch if not dest.exists() and not url]
    pending = [(url, dest) for url, dest in to_fetch if not dest.exists() and url]
    print(f"{len(to_fetch)} unique images needed, {already} already on disk, {len(pending)} to download ...")
    if missing_no_url:
        # Self-sourced items (own_*.jpg) have no image_source_url -- they're committed to git directly,
        # not scraped, so this script can't fetch them. Missing here means the clone is incomplete.
        print(f"  warning: {len(missing_no_url)} image(s) have no source URL and aren't on disk either "
              f"(expected for self-sourced items, which should already be committed): {missing_no_url}")

    ok, failed = 0, 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download_and_resize, url, dest, session): dest for url, dest in pending}
        for i, fut in enumerate(as_completed(futures), 1):
            if fut.result():
                ok += 1
            else:
                failed += 1
                print(f"  failed: {futures[fut]}")
            if i % 500 == 0:
                print(f"  {i}/{len(pending)} done")

    print(f"done: {ok} downloaded, {failed} failed, {already} already present.")


if __name__ == "__main__":
    main()
