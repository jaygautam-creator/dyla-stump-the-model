"""FastAPI wrapper around the existing matcher (src/dyla_match/) for the web demo.

Deliberately thin: no matching logic lives here, only HTTP plumbing. The matcher, config, and
catalogue are the same ones eval/harness.py measures against -- this API returns exactly what
`dyla-match match --photo ...` would, just over HTTP. Model + FAISS index load once at startup, not
per-request (each is a real few-hundred-ms cost, per eval/report*.md's timings section).
"""
import os
import tempfile
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import yaml
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from dyla_match.embed import load_embedder
from dyla_match.index import load_index
from dyla_match.matcher import Matcher

CONFIG_PATH = os.environ.get("DYLA_CONFIG", "configs/default.yaml")
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15MB -- generous for a phone photo, small enough to bound memory/time
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}

app = FastAPI(title="Dyla Stump the Model API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_state: dict = {}


@app.on_event("startup")
def load_matcher() -> None:
    config = yaml.safe_load(open(CONFIG_PATH))
    index_dir = Path(config["index"]["dir"]) / config["backbone"]
    index, meta = load_index(index_dir)
    embedder = load_embedder(config)
    _state["matcher"] = Matcher(
        embedder, index, meta,
        top_k_images=config.get("top_k_images", 50),
        top_k_products=config.get("top_k", 5),
    )
    _state["catalogue_dir"] = Path(config["catalogue"]["dir"]).resolve()
    _state["config"] = config


@app.get("/health")
def health():
    return {"status": "ok", "backbone": _state.get("config", {}).get("backbone")}


@app.post("/match")
async def match(photo: UploadFile = File(...)):
    if photo.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, f"unsupported content type: {photo.content_type}")

    body = await photo.read()
    if len(body) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"file too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)}MB)")

    suffix = Path(photo.filename or "upload.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(body)
        tmp.flush()
        try:
            out = _state["matcher"].match(Path(tmp.name))
        except Exception:
            raise HTTPException(422, "could not read this file as an image")

    results = out["results"]
    return {
        "results": [
            {
                "vendor": row["vendor"],
                "product_id": str(row["product_id"]),
                "title": row["title"],
                "design_group": row["design_group"],
                "score": float(row["score"]),
                "image_url": f"/catalogue-image?product_id={row['product_id']}&vendor={row['vendor']}",
            }
            for _, row in results.iterrows()
        ],
        "timings": out["timings"],
    }


@app.get("/catalogue-image")
def catalogue_image(product_id: str, vendor: str):
    meta = _state["matcher"].meta
    rows = meta[(meta["product_id"].astype(str) == product_id) & (meta["vendor"] == vendor)]
    if rows.empty:
        raise HTTPException(404, "not found")
    local_path = rows.iloc[0]["local_path"]

    catalogue_dir = _state["catalogue_dir"]
    resolved = (catalogue_dir / local_path).resolve()
    if not str(resolved).startswith(str(catalogue_dir)):
        raise HTTPException(400, "invalid path")  # defends against a crafted local_path escaping the catalogue dir
    if not resolved.exists():
        raise HTTPException(404, "not found")
    return FileResponse(resolved)
