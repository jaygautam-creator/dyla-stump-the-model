"""Measure the verification re-rank (src/dyla_match/rerank.py) against the frozen stumper set.

Run once per config change, not repeatedly against different fusion weights or thresholds to chase a
better number -- that would be tuning on the test split. The 0.5/0.5 fusion weight and candidate_pool
size are fixed in rerank.py before this was ever run against real accuracy.
"""
import os
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import pandas as pd
import yaml

from dyla_match.embed import load_embedder
from dyla_match.index import load_index
from dyla_match.rerank import verify_rerank
from eval.harness import load_labels, summarize, write_report


def main():
    # Plain (uncropped) CLIP config -- verify_rerank does its own explicit tight-crop pass internally
    # and disables the embedder's own crop flag while it runs, so this must not be *_crop.yaml (that
    # caused a double-crop bug, fixed 2026-09-15, see docs/ANTIGRAVITY_AUDIT.md).
    config = yaml.safe_load(open("configs/clip.yaml"))
    index, meta = load_index(Path(config["index"]["dir"]) / config["backbone"])
    embedder = load_embedder(config)
    catalogue_dir = Path(config["catalogue"]["dir"])

    labels = load_labels(Path("data/stumper/labels.csv"))
    photos_dir = Path("data/stumper/photos")

    records = []
    for i, (_, row) in enumerate(labels.iterrows()):
        results = verify_rerank(photos_dir / row["file"], embedder, index, meta, catalogue_dir)
        record = row.to_dict()
        record["top_sku_ids"] = [str(pid) for pid in results["product_id"]][:5]
        record["top_design_groups"] = list(results["design_group"])[:5]
        record["top1_score"] = float(results["score"].iloc[0]) if len(results) else float("nan")
        records.append(record)
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{len(labels)} photos matched")
    matches = pd.DataFrame(records)

    is_synthetic = matches["conditions"].str.contains("synthetic")
    real_matches = matches[~is_synthetic].reset_index(drop=True)

    summary_all = summarize(matches, k=5)
    summary_real = summarize(real_matches, k=5)

    out_path = Path("eval/report_rerank.md")
    fake_config = {"backbone": "clip + verification re-rank (crop)", "models": {"clip + verification re-rank (crop)": {"hf_id": "openai/clip-vit-base-patch32, tight-crop second pass"}}}
    tmp_real = out_path.with_suffix(".real.tmp.md")
    tmp_all = out_path.with_suffix(".all.tmp.md")
    write_report(summary_real, fake_config, tmp_real)
    write_report(summary_all, fake_config, tmp_all)
    combined = (
        "# Evaluation report (CLIP + crop + verification re-rank)\n\n"
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
