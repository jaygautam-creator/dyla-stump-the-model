"""Stumper evaluation harness: labels.csv + matcher -> eval/report.md.

Reads `data/stumper/labels.csv` (schema in `docs/PLAN.md`), runs every labelled photo through the
matcher, and turns the results into the metrics in `eval/metrics.py`: top-1/5 accuracy at SKU and
design level (per condition, with Wilson CI), paired drop against each item's clean photo, and the
FAR/FRR trade-off curve for refusal. ECE needs a calibrated confidence, which doesn't exist yet
(`calibrate.py` is Phase 5) — this reports raw top-1 cosine score instead and says so, rather than
treating an uncalibrated score as a probability.

Needs real photos in `data/stumper/photos/` + a real `labels.csv` to produce real numbers. Those are
Phase 2 and don't exist yet. Run this module directly (`python -m eval.harness`) for a wiring check
against real catalogue images relabelled as if they were photos — that only proves the pipeline runs,
not that the matcher works on real hard photos; it is never written into `data/stumper/`.
"""
import os
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import pandas as pd
import yaml

from dyla_match.matcher import Matcher
from eval.metrics import far_frr_curve, topk_accuracy, wilson_ci


def load_labels(labels_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(labels_csv, dtype=str).fillna("")
    df["in_catalogue"] = df["in_catalogue"].str.lower().isin(["true", "1", "yes"])
    return df


def run_matches(matcher: Matcher, labels: pd.DataFrame, photos_dir: Path, top_k: int = 5) -> pd.DataFrame:
    """Run the matcher over every labelled photo. Adds top-K product/design hits and top-1 score."""
    records = []
    for _, row in labels.iterrows():
        out = matcher.match(photos_dir / row["file"])
        results = out["results"]
        record = row.to_dict()
        record["top_sku_ids"] = [str(pid) for pid in results["product_id"]][:top_k]
        record["top_design_groups"] = list(results["design_group"])[:top_k]
        record["top1_score"] = float(results["score"].iloc[0]) if len(results) else float("nan")
        record["embed_s"] = out["timings"]["embed_s"]
        record["search_s"] = out["timings"]["search_s"]
        records.append(record)
    return pd.DataFrame(records)


def _hit_rate_with_ci(hits: list[bool]) -> dict:
    if not hits:
        return {"n": 0, "accuracy": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}
    acc = topk_accuracy(hits)
    lo, hi = wilson_ci(sum(hits), len(hits))
    return {"n": len(hits), "accuracy": acc, "ci_low": lo, "ci_high": hi}


def summarize(matches: pd.DataFrame, k: int = 5) -> dict:
    """Overall + per-condition SKU/design accuracy (top-1, top-k), paired drop, FAR/FRR curve.

    Known limitation: SKU ids are compared without the vendor, so a same-numbered SKU from a
    different vendor would be a false hit. Not observed in the current catalogue (checked when
    `groups.py` was written), but worth widening `labels.csv` with a vendor column if that changes.
    """
    positives = matches[matches["in_catalogue"]]

    def hits(row, key, field, n):
        return row[key] in row[field][:n]

    top1_sku = [hits(r, "sku_id", "top_sku_ids", 1) for _, r in positives.iterrows()]
    topk_sku = [hits(r, "sku_id", "top_sku_ids", k) for _, r in positives.iterrows()]
    top1_design = [hits(r, "design_group", "top_design_groups", 1) for _, r in positives.iterrows()]
    topk_design = [hits(r, "design_group", "top_design_groups", k) for _, r in positives.iterrows()]

    overall = {
        "top1_sku": _hit_rate_with_ci(top1_sku),
        f"top{k}_sku": _hit_rate_with_ci(topk_sku),
        "top1_design": _hit_rate_with_ci(top1_design),
        f"top{k}_design": _hit_rate_with_ci(topk_design),
    }

    per_condition = {}
    all_conditions = sorted(set(c for cs in matches["conditions"] for c in cs.split(";") if c))
    for cond in all_conditions:
        cond_positives = positives[positives["conditions"].str.contains(rf"(?:^|;){cond}(?:;|$)")]
        cond_hits = [hits(r, "sku_id", "top_sku_ids", 1) for _, r in cond_positives.iterrows()]
        per_condition[cond] = _hit_rate_with_ci(cond_hits)

    paired_drop = {}
    paired = positives[positives["pair_id"] != ""]
    for pair_id, group in paired.groupby("pair_id"):
        clean = group[group["conditions"] == "clean"]
        hard = group[group["conditions"] != "clean"]
        if clean.empty or hard.empty:
            continue
        clean_hit = hits(clean.iloc[0], "sku_id", "top_sku_ids", 1)
        hard_hit_rate = sum(hits(r, "sku_id", "top_sku_ids", 1) for _, r in hard.iterrows()) / len(hard)
        paired_drop[pair_id] = {"clean_hit": clean_hit, "hard_hit_rate": hard_hit_rate}

    scores = matches["top1_score"].tolist()
    labels = matches["in_catalogue"].tolist()
    curve = far_frr_curve(scores, labels, n_thresholds=21) if len(set(labels)) > 1 else []

    return {
        "overall": overall,
        "per_condition": per_condition,
        "paired_drop": paired_drop,
        "far_frr_curve": curve,
        "n_photos": len(matches),
        "n_positives": len(positives),
        "n_negatives": len(matches) - len(positives),
    }


def write_report(summary: dict, config: dict, out_path: Path) -> None:
    lines = [
        "# Evaluation report",
        "",
        f"Backbone: `{config['backbone']}` ({config['models'][config['backbone']]['hf_id']})",
        f"Photos: {summary['n_photos']} ({summary['n_positives']} positive, {summary['n_negatives']} negative)",
        "",
        "## Overall (SKU and design level, positives only)",
        "",
        "| metric | n | accuracy | 95% CI |",
        "|---|---|---|---|",
    ]
    for name, r in summary["overall"].items():
        lines.append(f"| {name} | {r['n']} | {r['accuracy']:.3f} | [{r['ci_low']:.3f}, {r['ci_high']:.3f}] |")

    lines += ["", "## Per-condition top-1 SKU accuracy", "", "| condition | n | accuracy | 95% CI |", "|---|---|---|---|"]
    for cond, r in summary["per_condition"].items():
        lines.append(f"| {cond} | {r['n']} | {r['accuracy']:.3f} | [{r['ci_low']:.3f}, {r['ci_high']:.3f}] |")

    if summary["paired_drop"]:
        lines += ["", "## Paired drop (hard vs this item's own clean photo)", "", "| pair_id | clean hit | hard hit rate |", "|---|---|---|"]
        for pair_id, d in summary["paired_drop"].items():
            lines.append(f"| {pair_id} | {d['clean_hit']} | {d['hard_hit_rate']:.3f} |")

    if summary["far_frr_curve"]:
        lines += ["", "## FAR/FRR curve (raw top-1 cosine score — no calibration yet, Phase 5)", "", "| threshold | FAR | FRR |", "|---|---|---|"]
        for t, far, frr in summary["far_frr_curve"]:
            lines.append(f"| {t:.3f} | {far:.3f} | {frr:.3f} |")

    out_path.write_text("\n".join(lines) + "\n")


def _dry_run_check():
    """Wiring check only: real catalogue images standing in for photos, never written to data/stumper/.

    Confirms the harness runs end-to-end and the numbers are internally consistent — not a claim about
    matcher accuracy on real hard photos, which needs Phase 2's real stumper set.
    """
    from dyla_match.embed import load_embedder
    from dyla_match.index import load_index

    config = yaml.safe_load(open("configs/default.yaml"))
    index_dir = Path(config["index"]["dir"]) / config["backbone"]
    index, meta = load_index(index_dir)
    embedder = load_embedder(config)
    matcher = Matcher(embedder, index, meta, top_k_images=config["top_k_images"], top_k_products=config["top_k"])

    catalogue_dir = Path(config["catalogue"]["dir"])
    products = meta.drop_duplicates(subset=["vendor", "product_id"]).reset_index(drop=True)
    sample = products.sample(n=10, random_state=0)

    rows = []
    for i, (_, p) in enumerate(sample.iterrows()):
        rows.append({
            "photo_id": f"dryrun_{i}",
            "file": p["local_path"],
            "sku_id": str(p["product_id"]),
            "design_group": p["design_group"],
            "in_catalogue": "true",
            "conditions": "clean" if i % 2 == 0 else "odd_angle",
            "pair_id": "",
            "split": "test",
            "notes": "dry run — a catalogue image standing in for a photo, not a real stumper photo",
        })
    labels = pd.DataFrame(rows)
    labels["in_catalogue"] = labels["in_catalogue"].str.lower().isin(["true"])

    matches = run_matches(matcher, labels, catalogue_dir, top_k=config["top_k"])
    summary = summarize(matches, k=config["top_k"])
    print(f"dry run: {summary['n_photos']} photos, top-1 SKU accuracy = {summary['overall']['top1_sku']['accuracy']:.3f}")
    assert summary["overall"]["top1_sku"]["accuracy"] == 1.0, "matcher should trivially self-retrieve a catalogue image"
    print("eval/harness.py: dry run passed (pipeline wiring only, not a real evaluation)")


if __name__ == "__main__":
    _dry_run_check()
