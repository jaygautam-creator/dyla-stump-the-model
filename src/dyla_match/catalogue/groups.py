"""Group near-duplicate catalogue listings into design groups.

Jewellery sites list the same design more than once for things a photo can't tell apart:
metal colour (gold / rose gold / silver), plating, and size. This groups those listings so
the eval can report accuracy at the design level as well as the exact-SKU level (see
`docs/PLAN.md`, "SKU vs design accuracy").

Approach: text only (no embeddings yet — those are Phase 3). Strip known colour/plating/size
tokens from the title, then group by (vendor, product_type, normalised title). This is a
heuristic, not a guarantee: two genuinely different designs that happen to share a normalised
title would be wrongly merged, and a design with an unlisted variant word would be wrongly
split. Both are checked by hand below before trusting the output.

Usage:
    python -m dyla_match.catalogue.groups --catalogue data/catalogue
"""
import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

# Order matters: longer/more specific phrases first, so e.g. "rose gold" is stripped
# before a bare "gold" pass could leave a stray "rose".
VARIANT_TOKENS = [
    r"\bplatinum plated\b",
    r"\brose gold\b",
    r"\bwhite gold\b",
    r"\byellow gold\b",
    r"\b925 sterling silver\b",
    r"\bsterling silver\b",
    r"\bgold plated\b",
    r"\bgold vermeil\b",
    r"\bgolden\b",
    r"\bgold\b",
    r"\bsilver\b",
    r"\b14k\b",
    r"\b18k\b",
    r"\b22k\b",
    r"\(size\s*\d+\)",
    r"\bsize\s*\d+\b",
]


def normalise_title(title: str) -> str:
    t = title.lower()
    for pattern in VARIANT_TOKENS:
        t = re.sub(pattern, " ", t)
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    t = re.sub(r"\s+", " ", t)
    return t


def build_groups(products: list[dict]) -> dict[str, str]:
    """Map (vendor, product_id) -> design_group id."""
    buckets: dict[tuple, list[str]] = defaultdict(list)
    for p in products:
        key = (p["vendor"], p["product_type"], normalise_title(p["title"]))
        buckets[key].append(p["product_id"])

    assignment = {}
    for (vendor, product_type, norm_title), product_ids in buckets.items():
        group_id = f"{vendor}_dg_{abs(hash((vendor, product_type, norm_title))) % 10**8:08d}"
        for pid in product_ids:
            assignment[(vendor, pid)] = group_id
    return assignment


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogue", default="data/catalogue")
    args = ap.parse_args()

    catalogue_dir = Path(args.catalogue)
    csv_path = catalogue_dir / "products.csv"
    rows = list(csv.DictReader(open(csv_path)))

    seen = set()
    unique_products = []
    for r in rows:
        key = (r["vendor"], r["product_id"])
        if key in seen:
            continue
        seen.add(key)
        unique_products.append(r)

    assignment = build_groups(unique_products)
    for r in rows:
        r["design_group"] = assignment[(r["vendor"], r["product_id"])]

    fieldnames = list(rows[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    group_sizes = defaultdict(set)
    for (vendor, pid), gid in assignment.items():
        group_sizes[gid].add(pid)
    n_products = len(unique_products)
    n_groups = len(group_sizes)
    multi = sum(1 for ids in group_sizes.values() if len(ids) > 1)
    largest = max(len(ids) for ids in group_sizes.values())
    print(f"{n_products} products -> {n_groups} design groups ({multi} groups with >1 SKU, largest={largest})")
    print(f"design_group column added to {csv_path}")


if __name__ == "__main__":
    main()
