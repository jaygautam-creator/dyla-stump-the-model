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
COPY backend/ ./backend/

RUN pip install --no-cache-dir -e ".[ml,api]"

# Bake the catalogue images and FAISS index into the image so the running container never needs
# network access to serve a request. This is the slow step (network-bound, one-time per build).
ENV KMP_DUPLICATE_LIB_OK=TRUE
RUN python -m scripts.hydrate_catalogue_images && \
    python -m dyla_match.cli build-index --config configs/default.yaml

ENV CORS_ORIGINS="*"
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
