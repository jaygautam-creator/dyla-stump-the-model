"""photo -> top-5 catalogue products, with per-stage timing.

Baseline (Phase 3): whole-image embedding straight into FAISS search. No localisation crop and no local
verification yet — those are Phase 5 improvements, measured against this baseline, not assumed better.
Refusal (NOT_IN_CATALOGUE) is also Phase 5; this returns raw top-K scores.
"""
import time
from pathlib import Path

import pandas as pd
from PIL import Image

from dyla_match.embed import Embedder
from dyla_match.index import search_products


class Matcher:
    def __init__(self, embedder: Embedder, index, meta: pd.DataFrame, top_k_images: int = 50, top_k_products: int = 5):
        self.embedder = embedder
        self.index = index
        self.meta = meta
        self.top_k_images = top_k_images
        self.top_k_products = top_k_products

    def match(self, photo_path: Path) -> dict:
        t0 = time.perf_counter()
        image = Image.open(photo_path).convert("RGB")
        t1 = time.perf_counter()
        query = self.embedder.embed([image])[0]
        t2 = time.perf_counter()
        results = search_products(query, self.index, self.meta, self.top_k_images, self.top_k_products)
        t3 = time.perf_counter()
        return {
            "results": results,
            "timings": {"load_s": t1 - t0, "embed_s": t2 - t1, "search_s": t3 - t2, "total_s": t3 - t0},
        }
