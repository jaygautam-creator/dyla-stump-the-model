"""Ensemble eval: combine DINOv2 + CLIP product-level scores (equal-weight average of raw cosine
scores) with crop preprocessing on both, then run the same harness metrics as a single-backbone run.

The weight (0.5 / 0.5) is fixed a priori, not searched against stumper accuracy -- that would be
tuning on the frozen test split, which docs/CLAUDE.md rules out. If the split-weighted version ever
needs revisiting, it has to happen on a calibration set that doesn't yet exist, not this one.
"""
import os
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import pandas as pd
import yaml

from dyla_match.embed import load_embedder
from dyla_match.index import load_index, search_products
from eval.harness import load_labels, summarize, write_report
from PIL import Image


def match_ensemble(image, embedders, indexes, metas, top_k_images, top_k_products):
    per_backbone = {}
    for name, embedder in embedders.items():
        query = embedder.embed([image])[0]
        per_backbone[name] = search_products(query, indexes[name], metas[name], top_k_images, top_k_products * 4)

    merged = None
    for name, df in per_backbone.items():
        df = df[["vendor", "product_id", "score", "title", "design_group"]].rename(columns={"score": f"score_{name}"})
        merged = df if merged is None else merged.merge(df, on=["vendor", "product_id", "title", "design_group"], how="outer")
    merged = merged.fillna(0.0)
    score_cols = [c for c in merged.columns if c.startswith("score_")]
    merged["score"] = merged[score_cols].mean(axis=1)
    return merged.sort_values("score", ascending=False).head(top_k_products).reset_index(drop=True)


def run_matches_ensemble(embedders, indexes, metas, labels, photos_dir, top_k_images, top_k):
    records = []
    for _, row in labels.iterrows():
        image = Image.open(photos_dir / row["file"]).convert("RGB")
        results = match_ensemble(image, embedders, indexes, metas, top_k_images, top_k)
        record = row.to_dict()
        record["top_sku_ids"] = [str(pid) for pid in results["product_id"]][:top_k]
        record["top_design_groups"] = list(results["design_group"])[:top_k]
        record["top1_score"] = float(results["score"].iloc[0]) if len(results) else float("nan")
        records.append(record)
    return pd.DataFrame(records)


def main():
    configs = {
        "dinov2": yaml.safe_load(open("configs/dinov2_crop.yaml")),
        "clip": yaml.safe_load(open("configs/clip_crop.yaml")),
    }
    embedders = {name: load_embedder(cfg) for name, cfg in configs.items()}
    indexes, metas = {}, {}
    for name, cfg in configs.items():
        idx, meta = load_index(Path(cfg["index"]["dir"]) / cfg["backbone"])
        indexes[name], metas[name] = idx, meta

    labels = load_labels(Path("data/stumper/labels.csv"))
    matches = run_matches_ensemble(embedders, indexes, metas, labels, Path("data/stumper/photos"), top_k_images=50, top_k=5)

    is_synthetic = matches["conditions"].str.contains("synthetic")
    real_matches = matches[~is_synthetic].reset_index(drop=True)

    summary_all = summarize(matches, k=5)
    summary_real = summarize(real_matches, k=5)

    out_path = Path("eval/report_ensemble_crop.md")
    fake_config = {"backbone": "dinov2+clip ensemble (crop, equal-weight)", "models": {"dinov2+clip ensemble (crop, equal-weight)": {"hf_id": "facebook/dinov2-small + openai/clip-vit-base-patch32"}}}
    tmp_all = out_path.with_suffix(".all.tmp.md")
    tmp_real = out_path.with_suffix(".real.tmp.md")
    write_report(summary_real, fake_config, tmp_real)
    write_report(summary_all, fake_config, tmp_all)
    combined = (
        "# Evaluation report (dinov2 + clip ensemble, crop preprocessing, equal weight)\n\n"
        "## Headline: real phone photos only (excludes synthetic augmentation)\n\n"
        + "\n".join(tmp_real.read_text().splitlines()[2:])
        + "\n\n---\n\n## Blended: real + synthetic augmentation\n\n"
        + "\n".join(tmp_all.read_text().splitlines()[2:])
    )
    out_path.write_text(combined)
    tmp_all.unlink()
    tmp_real.unlink()
    print(f"wrote {out_path} (real n={summary_real['n_photos']}, blended n={summary_all['n_photos']})")


if __name__ == "__main__":
    main()
