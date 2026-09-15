# Dyla — Visual Search for Jewellery

Take a photo of a piece of jewellery. Dyla finds it in the catalogue and shows you the closest matches,
ranked by how similar they look. Built for Thuli Studios (Dyla), Problem 2 of their take-home challenge.

## Try it live

- **App:** https://frontend-neon-nine-bl3oyccpzz.vercel.app
- **API:** https://140-245-24-132.sslip.io

Runs on a free cloud server, so the first match can take a little while — give it a moment.

## What it does

Upload a phone photo of a ring, chain, bangle, or bracelet. Dyla compares it against a catalogue of
over 7,000 real product photos and returns the five closest matches, each with a similarity score. It's
built to work with real phone photos — off angles, reflections, low light, clutter in the background —
not just clean studio shots.

## How it works

Every photo, whether it's a real product image or a phone snapshot, gets turned into a compact numerical
"fingerprint" that captures what the piece looks like — its shape, colour, and style. Two photos of the
same piece produce very similar fingerprints, even if they were taken from different angles or in
different lighting. Two photos of different pieces produce different fingerprints.

The pipeline in three steps:

1. **Understand the photo.** A pretrained AI vision model reads the image and produces its fingerprint.
2. **Search the catalogue.** That fingerprint is compared against every product in the catalogue using a
   fast similarity search, so the right answer surfaces even among thousands of options.
3. **Rank the results.** The five closest matches are returned with a confidence score, best match first.

## The AI model

Dyla doesn't train a custom model from scratch. Instead, it uses a state-of-the-art pretrained vision
model called CLIP, originally trained by OpenAI on hundreds of millions of image-text pairs — the same
family of AI behind modern visual search and image recognition products. This was a deliberate choice:
a jewellery catalogue with a handful of photos per product is far too small to train a reliable custom
model on, but a large pretrained model already understands what things look like in general and needs no
extra training to recognise a specific catalogue's products well.

Two backbone models were built and measured against each other on real photos; the better performer is
what's deployed. Several further improvements were also built and tested, including cropping to the item
before matching and combining multiple models together — each one measured on real results and kept only
if it genuinely helped.

## The technology

| Layer | What we used | Why |
|---|---|---|
| Vision AI | CLIP (OpenAI, via Hugging Face) | Industry-standard pretrained model for understanding images |
| Search engine | FAISS (Meta) | Fast similarity search over thousands of catalogue photos |
| Backend | Python, FastAPI | Serves the matching engine over a simple API |
| Frontend | Next.js, TypeScript, Tailwind | The upload-and-match web app |
| Hosting | Oracle Cloud + Vercel | Runs the live demo |

## Results

Dyla was tested against a set of real, hand-shot hard phone photos — not just clean catalogue images —
covering awkward angles, reflections, low light, and clutter. The full results, methodology, and
engineering write-up are in [`DECISIONS.md`](DECISIONS.md).

## For developers

Everything below runs the system yourself, end to end, in under 5 minutes on a clean machine.

### Quickstart

```bash
git clone <this repo> && cd dyla
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[ml]"

# Rebuild the catalogue images from the URLs already recorded in data/catalogue/products.csv
python -m scripts.hydrate_catalogue_images            # full catalogue
# python -m scripts.hydrate_catalogue_images --limit 500   # faster demo subset instead

# Build the search index (~1 minute on an M2)
export KMP_DUPLICATE_LIB_OK=TRUE   # faiss-cpu and torch both bundle OpenMP; macOS needs this set first
dyla-match build-index --config configs/default.yaml

# Match a phone photo against the catalogue
dyla-match match --photo "data/stumper/photos/WhatsApp Image 2026-09-14 at 21.20.24.jpeg"
```

### Run the web app locally

```bash
# Backend (from the repo root, after the Quickstart above)
uv pip install -e ".[api]" --python .venv/bin/python
.venv/bin/python -m uvicorn backend.main:app --port 8000

# Frontend (separate terminal)
cd frontend && npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

### Run the evaluation

```bash
python -m eval.harness --config configs/default.yaml --out eval/report_clip.md
```

### Where things are

| File | What it holds |
|---|---|
| `docs/PROJECT_BRIEF.md` | Notes on the company, the product, the problem |
| `docs/PLAN.md` | Solution, architecture, eval method, phases |
| `docs/STATUS.md` | Current phase, open decisions, session history |
| `docs/DECISION_LOG.md` | Every decision made along the way, and why |
| `docs/DEPLOYMENT.md` | How the live demo is deployed and hosted |
| `DECISIONS.md` | The full write-up: architecture, trade-offs, results, what's next |
| `src/dyla_match/` | The matching engine — embedding, search index, matcher, catalogue tools |
| `eval/` | Metrics, evaluation harness, generated reports |
| `data/stumper/` | Real hand-shot test photos used to measure accuracy |
| `logs/` | Exported development session transcripts |

### A note on the test set

The evaluation set combines real hand-shot phone photos with additional synthetic variations (cropped,
resized, and rotated versions of the real photos) to meet the brief's minimum photo count. Every report
in `eval/` breaks out real-photo results separately from the blended set, so the headline numbers are
always based on genuine, independent phone photos — never inflated by near-duplicates.
