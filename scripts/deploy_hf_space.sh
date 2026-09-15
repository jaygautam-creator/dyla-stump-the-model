#!/usr/bin/env bash
# Populate a Hugging Face Space (Docker SDK) with everything the backend needs, from a clean clone of
# that Space's own git repo. Free CPU Spaces give 16GB RAM with no card required -- Render's free tier
# (~512MB) can't hold CLIP+torch without OOM-crashing, this can.
#
# Usage: scripts/deploy_hf_space.sh /path/to/cloned/space/repo
set -euo pipefail

SPACE_DIR="${1:?Usage: scripts/deploy_hf_space.sh /path/to/cloned/space/repo}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -d "$SPACE_DIR/.git" ]; then
  echo "error: $SPACE_DIR doesn't look like a git repo (no .git/) -- clone the Space first, see README." >&2
  exit 1
fi

mkdir -p "$SPACE_DIR/src" "$SPACE_DIR/scripts" "$SPACE_DIR/configs" "$SPACE_DIR/backend" "$SPACE_DIR/data/catalogue"
cp -R "$REPO_ROOT/src/." "$SPACE_DIR/src/"
cp -R "$REPO_ROOT/scripts/." "$SPACE_DIR/scripts/"
cp -R "$REPO_ROOT/configs/." "$SPACE_DIR/configs/"
cp -R "$REPO_ROOT/backend/." "$SPACE_DIR/backend/"
cp "$REPO_ROOT/data/catalogue/products.csv" "$SPACE_DIR/data/catalogue/products.csv"
cp "$REPO_ROOT/pyproject.toml" "$SPACE_DIR/pyproject.toml"

# HF Spaces reads Docker-SDK config from YAML frontmatter at the top of THIS repo's own README.md --
# separate file from the main project README.md, never touches it.
cat > "$SPACE_DIR/README.md" <<'EOF'
---
title: Dyla Stump the Model API
emoji: 💍
colorFrom: yellow
colorTo: pink
sdk: docker
app_port: 8000
pinned: false
---

FastAPI backend for the Dyla "Stump the Model" jewellery visual matcher. See the main project repo
for the matcher, evaluation harness, and full write-up: this Space only serves `/health`, `/match`,
and `/catalogue-image` over HTTP for the deployed frontend to call.
EOF

# HF Spaces' Docker SDK expects the Dockerfile at the Space repo's root, building with that root as
# context -- the copied layout above (src/, scripts/, configs/, backend/, data/catalogue/) mirrors our
# main repo's root closely enough that backend/Dockerfile's COPY paths work unchanged.
cp "$REPO_ROOT/backend/Dockerfile" "$SPACE_DIR/Dockerfile"

echo "Populated $SPACE_DIR. Next:"
echo "  cd $SPACE_DIR && git add -A && git commit -m 'Deploy backend' && git push"
