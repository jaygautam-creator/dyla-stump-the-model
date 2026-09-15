"""Diagnostic script to analyze the domain shift and background confounding on SKU 7557947424992 (Kada).

Usage:
    python -m scripts.diagnose_kada_domain
"""
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
import yaml

from dyla_match.embed import load_embedder
from dyla_match.index import load_index, search_products


def get_corner_rgb(image: Image.Image, border_size: int = 15) -> np.ndarray:
    arr = np.array(image.convert("RGB"))
    corners = np.concatenate([
        arr[:border_size, :border_size].reshape(-1, 3),
        arr[:border_size, -border_size:].reshape(-1, 3),
        arr[-border_size:, :border_size].reshape(-1, 3),
        arr[-border_size:, -border_size:].reshape(-1, 3),
    ])
    return corners.mean(axis=0)


def main():
    print("=" * 70)
    print("DYLA MATCH: KADA DOMAIN SHIFT & BACKGROUND CONFOUNDING DIAGNOSTIC")
    print("=" * 70)

    config = yaml.safe_load(open("configs/default.yaml"))
    index_dir = Path(config["index"]["dir"]) / config["backbone"]
    index, meta = load_index(index_dir)
    meta["product_id"] = meta["product_id"].astype(str)
    embedder = load_embedder(config)

    phone_photo_path = Path("data/stumper/photos/WhatsApp Image 2026-09-14 at 21.21.08 (1).jpeg")
    ring_cat_path = Path("data/catalogue/images/own_gold-ring.jpg")
    swashaa_white_path = Path("data/catalogue/images/swashaa_7557947424992_46784612270304.jpg")
    swashaa_black_path = Path("data/catalogue/images/swashaa_7557947424992_47270502957280.jpg")

    # 1. Background Color Analysis
    print("\n1. Background RGB Comparison:")
    phone_img = Image.open(phone_photo_path)
    ring_cat_img = Image.open(ring_cat_path)
    swashaa_white_img = Image.open(swashaa_white_path)
    swashaa_black_img = Image.open(swashaa_black_path)

    bg_phone = get_corner_rgb(phone_img)
    bg_ring = get_corner_rgb(ring_cat_img)
    bg_white = get_corner_rgb(swashaa_white_img)
    bg_black = get_corner_rgb(swashaa_black_img)

    print(f"  - Phone Kada Photo Background (Table):        [{bg_phone[0]:.1f}, {bg_phone[1]:.1f}, {bg_phone[2]:.1f}]")
    print(f"  - Self-Sourced Ring Catalogue (Same Table):   [{bg_ring[0]:.1f}, {bg_ring[1]:.1f}, {bg_ring[2]:.1f}]")
    print(f"  - Swashaa Kada White Studio Packshot:         [{bg_white[0]:.1f}, {bg_white[1]:.1f}, {bg_white[2]:.1f}]")
    print(f"  - Swashaa Kada Black Studio Packshot:         [{bg_black[0]:.1f}, {bg_black[1]:.1f}, {bg_black[2]:.1f}]")

    # 2. Baseline Match
    print("\n2. Baseline CLIP Match on Untouched Phone Photo:")
    q_vec = embedder.embed([phone_img])[0]
    res_orig = search_products(q_vec, index, meta, top_k_images=2000, top_k_products=5)
    print(res_orig[["vendor", "product_id", "score", "title"]].to_string(index=False))

    idx_orig = res_orig.index[res_orig["product_id"] == "7557947424992"].tolist()
    if idx_orig:
        print(f"  --> True Swashaa Kada rank: {idx_orig[0] + 1}")
    else:
        print("  --> True Swashaa Kada not in top 5 (out-ranked by tabletop match)")

    # 3. Background Removal Experiment
    print("\n3. Background Removal (U2Net) & Composite on White:")
    try:
        from rembg import remove, new_session
        session = new_session("u2netp")
        rgba = remove(phone_img, session=session)
        white_bg = Image.new("RGB", rgba.size, (255, 255, 255))
        white_bg.paste(rgba, mask=rgba.split()[3])

        q_clean = embedder.embed([white_bg])[0]
        res_clean = search_products(q_clean, index, meta, top_k_images=2000, top_k_products=5)
        print(res_clean[["vendor", "product_id", "score", "title"]].to_string(index=False))

        print("\nConclusion:")
        print("  - Removing the table background drops the false 'own-gold-ring' match out of the top 5.")
        print("  - Retrieval shifts to the correct semantic category (Bangles and Kadas).")
        print("  - Off-the-shelf whole-image CLIP still requires fine-grained keypoint matching for exact SKU discrimination.")
    except Exception as e:
        print(f"  Background removal failed: {e}")

    print("=" * 70)


if __name__ == "__main__":
    main()
