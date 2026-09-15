# Builds the matcher's data (catalogue images + FAISS index) at image-build time from the committed
# metadata, then serves it with uvicorn. Matches the README's "these are gitignored, rebuilt on demand"
# design -- applied to a container build instead of a local machine.
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY configs/ ./configs/
COPY data/catalogue/products.csv ./data/catalogue/products.csv
# Self-sourced items have no image_source_url (nothing to scrape them from) and are committed instead --
# scripts/hydrate_catalogue_images.py can't fetch these, they must be copied directly.
COPY data/catalogue/images/own_*.jpg ./data/catalogue/images/
COPY backend/ ./backend/

# torch's default PyPI wheel pulls in full CUDA/cuDNN dependencies (several GB) even on a CPU-only
# machine with no GPU -- install the CPU-only build from PyTorch's own index first so pip's resolver
# sees the constraint already satisfied and never reaches for the CUDA variant.
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -e ".[ml,api]"

# Bake the catalogue images and FAISS index into the image so the running container never needs
# network access to serve a request. This is the slow step (network-bound, one-time per build).
ENV KMP_DUPLICATE_LIB_OK=TRUE
RUN python -m scripts.hydrate_catalogue_images && \
    python -m dyla_match.cli build-index --config configs/default.yaml

ENV CORS_ORIGINS="*"
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
