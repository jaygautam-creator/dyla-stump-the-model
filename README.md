# Dyla: Stump the Model

A visual matcher for jewellery. Give it a phone photo of a piece and it returns the matching catalogue item
(top 5 with confidence), or says the piece isn't in the catalogue. The repo also includes a hand-shot set
of hard photos and an evaluation harness that breaks accuracy down by what made each photo hard.

Built for the Thuli Studios (Dyla) take-home, Problem 2. CPU/MPS only — tested on an Apple M2, 8GB RAM.

## Live demo

- Frontend: https://frontend-neon-nine-bl3oyccpzz.vercel.app
- Backend API: https://140-245-24-132.sslip.io

Deployed at zero recurring cost (no paid plan anywhere) on an Oracle Cloud Always Free VM + Vercel's free
tier. Slow (~15-18s per match — a 1GB free VM, no GPU) but genuinely live and functional. Full story,
including three rejected "free" platforms along the way, in `docs/DEPLOYMENT.md`.

## Result, in one line

CLIP (`openai/clip-vit-base-patch32`), plain whole-image cosine retrieval, no crop/re-rank/ensemble —
every one of those was tried and measured worse (see `DECISIONS.md`) — over a 7,272-image scraped
catalogue: **75.9% top-1 SKU accuracy** on 58 real hard phone photos of 3 items genuinely in the
catalogue (Wilson 95% CI [63.5%, 85.0%]). That number hides an important weakness: the one item that's a
genuine external catalogue match scores 0%. Full breakdown, rejected approaches, and where it fails:
`DECISIONS.md` and `eval/report_clip.md`.

## Quickstart (under 5 minutes on a clean machine)

```bash
git clone <this repo> && cd dyla
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[ml]"

# Rebuild the ~180MB of catalogue images from the URLs already recorded in data/catalogue/products.csv
# (images are gitignored; the metadata + source URL for every image is committed). Full catalogue
# (7,272 images) takes a few minutes over the network -- use --limit for a fast subset demo.
python -m scripts.hydrate_catalogue_images            # full catalogue
# python -m scripts.hydrate_catalogue_images --limit 500   # faster demo subset instead

# Embed the catalogue and build the FAISS index (~1 minute on an M2)
export KMP_DUPLICATE_LIB_OK=TRUE   # faiss-cpu and torch both bundle OpenMP; macOS needs this set first
dyla-match build-index --config configs/default.yaml

# Match one phone photo against the catalogue
dyla-match match --photo "data/stumper/photos/WhatsApp Image 2026-09-14 at 21.20.24.jpeg"
```

Expected output: top-5 candidate products with cosine scores, and the own-catalogued gold chain
(`own-gold-chain`) at rank 1.

## Evaluate on the hard-photo set

```bash
python -m eval.harness --config configs/default.yaml --out eval/report_clip.md
```

Reads `data/stumper/labels.csv` + `data/stumper/photos/`, runs every labelled photo through the matcher,
and writes top-1/5 accuracy (SKU + design level, Wilson 95% CI), per-condition breakdown, paired
clean-vs-hard drop, and per-item precision/recall/F1 — reported separately for the 58 real phone photos
and the synthetic augmentation used to pad the set past the brief's 100-photo minimum (see
"Stumper set" below). `eval/report*.md` in the repo are pre-generated for every backbone × preprocessing
combination that was actually measured.

## Where things are

| File | What it holds |
|---|---|
| `docs/PROJECT_BRIEF.md` | Notes on the company, the product, the problem |
| `docs/PLAN.md` | Solution, architecture, eval method, phases |
| `docs/STATUS.md` | Current phase, open decisions, session history |
| `docs/DECISION_LOG.md` | Every decision, with reasoning and who made the call |
| `docs/DEPLOYMENT.md` | What's actually deployed, how, and why (rejected platforms, real bugs hit) |
| `DECISIONS.md` | The ≤2-page write-up: architecture, trade-offs, where it breaks, next 2 weeks |
| `src/dyla_match/` | Embedding (`embed.py`), FAISS index (`index.py`), crop preprocessing (`preprocess.py`, tried and rejected — off by default), verification re-rank (`rerank.py`, tried and rejected), matcher (`matcher.py`), CLI (`cli.py`), catalogue scraper (`catalogue/`) |
| `eval/` | Metrics (`metrics.py`), harness (`harness.py`), ensemble experiment (`run_ensemble.py`), reports |
| `scripts/hydrate_catalogue_images.py` | Rebuilds `data/catalogue/images/` from committed metadata |
| `scripts/augment_stumper.py` | Pads the stumper set with tagged synthetic transforms (see below) |
| `data/stumper/` | 58 real hand-shot hard photos + labels; synthetic augmentation added on top |
| `logs/` | Exported AI session transcripts (required by the brief) |

## Stumper set: real vs synthetic

The brief asks for 100+ hard phone photos; only 3 items were available at zero budget (a self-sourced
gold chain, a gold ring, and a kada that turned out to be a genuine Swashaa product — verified exact SKU,
not self-sourced). 58 real photos were shot across those 3 items. `scripts/augment_stumper.py` pads the
count past 100 using crop/resize/rotate transforms of the real photos, each tagged `synthetic_*` in
`labels.csv` and reported **separately** from the real-photo numbers in every `eval/report*.md` — a
synthetic near-duplicate of a photo the matcher already saw is not independent evidence the way a new
real photo is, and blending it into the headline number without saying so would overstate accuracy.
Trust the "real phone photos only" section of each report; the "blended" section is there for the
100-photo-minimum requirement, not as the accuracy claim.

## Config

Everything in `configs/default.yaml` is swappable without touching code: backbone (`dinov2`/`clip`),
crop preprocessing on/off, top-k, device. `configs/*_crop.yaml` and `configs/clip.yaml` are the variants
actually measured against each other in `eval/report*.md` — crop measured worse for both backbones and
is off by default; plain whole-image CLIP is what ships.

## Web demo (backend + frontend)

A FastAPI backend (`backend/`) wraps the same matcher this README's quickstart uses, and a Next.js
frontend (`frontend/`) provides the upload UI. Both are separate from the core matcher/eval code above —
neither is required to run the CLI or the harness.

```bash
# Backend (from the repo root, after the Quickstart steps above have built data/index/)
.venv/bin/python -m uvicorn backend.main:app --port 8000
# needs: uv pip install -e ".[api]" --python .venv/bin/python   (once)

# Frontend (separate terminal)
cd frontend
npm install        # once
cp .env.example .env.local   # points it at http://localhost:8000 by default
npm run dev
```

Open `http://localhost:3000`, drop in a phone photo, see the top-5 matches. **Deployed live** (URLs
above) on an Oracle Cloud Always Free VM (backend, via `backend/Dockerfile` + `scripts/oci_provision.py`)
and Vercel (frontend, free Hobby tier) — see `docs/DEPLOYMENT.md` for the full deployment story,
including Render/Koyeb/Hugging Face Spaces being tried and ruled out first (none had enough RAM, or
stopped being free, for CLIP+torch), and `docs/PLAN.md` "Phase 6" for the original design brief.
