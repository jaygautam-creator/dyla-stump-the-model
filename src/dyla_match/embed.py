"""Pretrained image embeddings — DINOv2 or CLIP, no fine-tuning.

5k catalogue images with only a few views per product would overfit a fine-tuned model, and there's no
time budget to do fine-tuning honestly. Both backbones come straight from Hugging Face via `transformers`.
Which one wins at exact-item retrieval (not "a gold necklace" but "this gold necklace") is a Phase 4
measurement, not something decided here.
"""
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from dyla_match.preprocess import object_crop


def pick_device(requested: str = "auto") -> str:
    if requested != "auto":
        return requested
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@dataclass
class Embedder:
    backbone: str
    hf_id: str
    device: str
    use_object_crop: bool = False
    processor: object = field(init=False, repr=False)
    model: object = field(init=False, repr=False)

    def __post_init__(self):
        if self.backbone == "clip":
            from transformers import CLIPModel, CLIPProcessor

            self.processor = CLIPProcessor.from_pretrained(self.hf_id)
            self.model = CLIPModel.from_pretrained(self.hf_id).to(self.device).eval()
        elif self.backbone == "dinov2":
            from transformers import AutoImageProcessor, AutoModel

            self.processor = AutoImageProcessor.from_pretrained(self.hf_id)
            self.model = AutoModel.from_pretrained(self.hf_id).to(self.device).eval()
        else:
            raise ValueError(f"unknown backbone: {self.backbone!r} (expected 'dinov2' or 'clip')")

    @torch.inference_mode()
    def embed(self, images: list[Image.Image]) -> np.ndarray:
        if self.use_object_crop:
            images = [object_crop(img) for img in images]
        inputs = self.processor(images=images, return_tensors="pt").to(self.device)
        if self.backbone == "clip":
            # transformers>=5's get_image_features returns the vision tower's output object, with the
            # projected embedding in .pooler_output — not a bare tensor.
            feats = self.model.get_image_features(**inputs).pooler_output
        else:
            feats = self.model(**inputs).last_hidden_state[:, 0]  # CLS token
        feats = feats.float().cpu().numpy()
        feats /= np.linalg.norm(feats, axis=1, keepdims=True) + 1e-9
        return feats

    def embed_paths(self, paths: list[Path], batch_size: int = 16) -> np.ndarray:
        vectors = []
        for i in range(0, len(paths), batch_size):
            batch = [Image.open(p).convert("RGB") for p in paths[i : i + batch_size]]
            vectors.append(self.embed(batch))
        return np.concatenate(vectors, axis=0)


def load_embedder(config: dict) -> Embedder:
    backbone = config["backbone"]
    model_cfg = config["models"][backbone]
    device = pick_device(config.get("device", "auto"))
    use_object_crop = config.get("preprocess", {}).get("object_crop", False)
    return Embedder(backbone=backbone, hf_id=model_cfg["hf_id"], device=device, use_object_crop=use_object_crop)
