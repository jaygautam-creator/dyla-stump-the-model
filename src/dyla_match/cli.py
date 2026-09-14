"""CLI entry points for the matcher.

    python -m dyla_match.cli build-index --config configs/default.yaml
    python -m dyla_match.cli match --config configs/default.yaml --photo path/to/photo.jpg
"""
import argparse
import os
from pathlib import Path

# faiss-cpu and torch each bundle their own OpenMP runtime; on macOS loading both aborts the process
# unless this is set before either is imported. Documented workaround, not a silent hack — see
# https://github.com/facebookresearch/faiss/issues/1010
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import pandas as pd
import yaml

from dyla_match.embed import load_embedder
from dyla_match.index import build_index, load_index


def cmd_build_index(args):
    config = yaml.safe_load(open(args.config))
    catalogue_dir = Path(config["catalogue"]["dir"])
    meta = pd.read_csv(config["catalogue"]["csv"])
    if args.limit:
        meta = meta.head(args.limit)
    paths = [catalogue_dir / p for p in meta["local_path"]]

    embedder = load_embedder(config)
    index_dir = Path(config["index"]["dir"]) / config["backbone"]
    print(f"Embedding {len(paths)} catalogue images with {config['backbone']} on {embedder.device} ...")
    embeddings = embedder.embed_paths(paths, batch_size=config.get("batch_size", 16))
    build_index(embeddings, meta, index_dir)
    print(f"Index written to {index_dir}/")


def cmd_match(args):
    config = yaml.safe_load(open(args.config))
    index_dir = Path(config["index"]["dir"]) / config["backbone"]
    index, meta = load_index(index_dir)
    embedder = load_embedder(config)

    from dyla_match.matcher import Matcher

    matcher = Matcher(
        embedder, index, meta,
        top_k_images=config.get("top_k_images", 50),
        top_k_products=config.get("top_k", 5),
    )
    out = matcher.match(Path(args.photo))
    print(out["results"].to_string(index=False))
    print("timings (s):", {k: round(v, 4) for k, v in out["timings"].items()})


def main():
    ap = argparse.ArgumentParser(prog="dyla-match")
    sub = ap.add_subparsers(required=True)

    p_build = sub.add_parser("build-index", help="embed the catalogue and write a FAISS index")
    p_build.add_argument("--config", default="configs/default.yaml")
    p_build.add_argument("--limit", type=int, default=None, help="cap catalogue images, for a quick test run")
    p_build.set_defaults(func=cmd_build_index)

    p_match = sub.add_parser("match", help="match a phone photo against the catalogue index")
    p_match.add_argument("--config", default="configs/default.yaml")
    p_match.add_argument("--photo", required=True)
    p_match.set_defaults(func=cmd_match)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
