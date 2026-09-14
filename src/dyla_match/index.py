"""FAISS index over catalogue image embeddings, aggregated to product level.

Flat inner-product index over L2-normalised vectors (= cosine similarity). At ~6k vectors, search is
sub-millisecond, so per-query latency is model time, not index time — measured separately in `matcher.py`.
"""
from pathlib import Path

import faiss
import numpy as np
import pandas as pd

INDEX_FILE = "catalogue.faiss"
META_FILE = "catalogue_meta.csv"


def build_index(embeddings: np.ndarray, meta: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings.astype(np.float32))
    faiss.write_index(index, str(out_dir / INDEX_FILE))
    meta.reset_index(drop=True).to_csv(out_dir / META_FILE, index=False)


def load_index(index_dir: Path) -> tuple[faiss.Index, pd.DataFrame]:
    index = faiss.read_index(str(index_dir / INDEX_FILE))
    meta = pd.read_csv(index_dir / META_FILE)
    return index, meta


def search_products(
    query: np.ndarray,
    index: faiss.Index,
    meta: pd.DataFrame,
    top_k_images: int = 50,
    top_k_products: int = 5,
) -> pd.DataFrame:
    """Image-level FAISS search, aggregated to product level by max image score."""
    scores, indices = index.search(query.reshape(1, -1).astype(np.float32), top_k_images)
    valid = indices[0] >= 0
    hits = meta.iloc[indices[0][valid]].copy()
    hits["score"] = scores[0][valid]
    product_scores = (
        hits.groupby(["vendor", "product_id"], as_index=False)
        .agg(score=("score", "max"), title=("title", "first"), design_group=("design_group", "first"))
        .sort_values("score", ascending=False)
    )
    return product_scores.head(top_k_products).reset_index(drop=True)
