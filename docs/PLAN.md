# Plan

Drafted 2026-09-14. Some choices are still open (see `STATUS.md`). Any change goes into `DECISION_LOG.md`
with the reason.

## Phase 6: demo + deployment (added 2026-09-15, supersedes D4)

Written down before any UI code exists, per instruction — nothing here should be guessed later.

**Sequencing (my instruction, 2026-09-15):** model accuracy work first, this plan second, build/deploy
last — not started until told to.

**Recommended stack, revised 2026-09-15 after "we can't buy any plan"** (Claude's recommendation; final
call is mine) — zero recurring cost, no card required anywhere:
- **Backend:** FastAPI wrapping the matcher, deployed on **Hugging Face Spaces (Docker SDK, free CPU
  tier)**. Originally recommended Render, but Render's free web-service tier (~512MB RAM) can't hold
  CLIP+torch without OOM-crashing, and a paid tier is off the table. HF Spaces' free CPU tier gives 16GB
  RAM, no credit card, and takes a plain Dockerfile directly — `backend/Dockerfile` reused as-is via
  `scripts/deploy_hf_space.sh`. Trade-off versus a paid host: still sleeps after inactivity, so the
  first request after idle time is slow (model reload) — acceptable for a take-home demo, not for real
  production traffic.
  - Google Cloud Run's free tier was considered and rejected for this: technically capable, but Google
    requires a billing account on file even for free-tier usage, which fails the "no card" constraint
    even though it wouldn't actually charge anything within the free allowance.
  - Cloudflare Workers was considered and rejected: doesn't run PyTorch at all. Using it would mean
    re-architecting onto Cloudflare's own hosted CLIP model (different embedding space, would need
    re-embedding the whole catalogue and re-measuring every number in `DECISIONS.md` from scratch) —
    too large a change for what this is.
- **Frontend:** Next.js on **Vercel**, free Hobby tier, no card — unchanged from the original plan.
- **API contract:** `POST /match` with a multipart image upload → JSON `{results: [{vendor,
  product_id, title, score, image_url}], timings}`. Backend serves catalogue thumbnails directly (they're
  already resized to ≤512px) so the frontend never needs its own copy of the 180MB catalogue.

**Design brief for the frontend** (from instruction, 2026-09-15): modern, aesthetic, premium feel; light,
jewellery-appropriate palette (warm ivory/cream/blush neutrals, soft gold/champagne accents — not a
generic SaaS-blue dashboard); a bit of restrained modern elegance rather than maximalist. Core flow:
upload/drop a phone photo → loading state → top-5 results as photo cards with product image, title,
vendor, and confidence, ranked by score. Should read as a boutique product-recognition tool, not a
raw ML demo. Built in `frontend/`, verified building and serving locally.

**Open decisions still mine to make when we get here:** whether the frontend also shows the "not in
catalogue" / low-confidence case explicitly, whether to password-gate the deployed demo (it's a
take-home submission, not meant for public traffic), whether the free tier's cold-start latency is
acceptable to leave as-is or needs a "waking up" loading state in the frontend.

## What I'm aiming for

1. The core, working from a clean checkout.
2. One extension done properly: refusal.
3. At least two obvious approaches tried, measured, and replaced, with numbers.
4. Weaknesses I find myself and write up.
5. Jewellery-specific details that matter for a real retailer, not just a generic image-retrieval demo.
6. A system small enough to change live in the follow-up call.

## The matcher: two-stage retrieval

```
phone photo
  │
  ├─ 1. localise   open-vocabulary detector ("ring", "earring", "necklace", "bangle", "pendant")
  │                crop to the piece; fall back to the whole image if nothing is found
  │
  ├─ 2. embed      pretrained backbone, L2-normalised
  │                DINOv2 vs CLIP/SigLIP, picked by measurement
  │
  ├─ 3. search     FAISS inner-product index over every catalogue image (packshot, side, on-model)
  │                image hits aggregated to product level (max score), top-K ≈ 20
  │
  ├─ 4. verify     local feature matching between photo and each candidate
  │                (SuperPoint + LightGlue, or DINOv2 patch mutual nearest neighbours) + geometric check
  │                inlier count used to re-rank
  │
  └─ 5. decide     confidence = f(top-1 score, top-1/top-2 margin, inliers), fit on the calibration split
                   top-5 with probabilities, or NOT IN CATALOGUE below the threshold
```

Why each stage:

- **Localise.** Jewellery is small in a real photo. A whole-image embedding mostly encodes the hand, face or
  background.
- **Pretrained embeddings, no fine-tuning.** 5k images with only a few views per product would overfit, and I
  can't fine-tune honestly in the time budget.
- **FAISS flat.** At 5k vectors search is under a millisecond, so lookup time is really model time. I'll report
  timing per stage.
- **Verification.** Lookalike pieces score close to true matches on global similarity. An exact match shares local
  structure: stone layout, links, engraving.
- **Calibration.** A confidence of 0.8 should be right about 80% of the time. I'll check with a reliability plot.

## Going beyond the brief

1. **Paired photos.** Every item I shoot gets a clean phone photo plus hard ones. The drop for each condition is
   measured against the same item's clean phone photo, which separates the condition from the general
   phone-vs-studio gap. Using catalogue images as the "clean" baseline would be leakage.
2. **SKU vs design accuracy.** Jewellery sites list the same design several times (14K/18K, yellow/rose gold, sizes)
   and no photo can tell those apart. I'll group near-duplicate listings and report accuracy at both levels.
3. **Confidence intervals.** Around 15 photos per condition gives roughly ±20 points. Wilson intervals on every
   per-condition number.
4. **Confounding.** Many photos have more than one condition. The paired design helps; I'll note where it doesn't.
5. **Conditions that aren't in the brief but happen in real jewellery shopping:**
   - WhatsApp recompression: photos arrive downscaled and recompressed.
   - Screenshots of a phone or laptop screen (Instagram posts, product pages).
   - Worn (ear, neck, wrist) vs held in a hand.
6. **Latency per stage** (detector, embedding, search, verification), p50 and p95 on the M2 CPU.

## Extension: dropped, not replaced yet

Refusal was the original plan (see `DECISION_LOG.md`, 2026-09-14 "Refusal (the extension)" and the later
entry that supersedes it). It needed ~20 lookalike pieces genuinely outside the catalogue. Once the stumper
set became 3 zero-cost home pieces (ring, chain, kadda) added *as* catalogue items, there was nothing left
at zero cost to serve as negatives — the home pieces became positives instead. Rather than half-build
refusal with no real negatives to test it against, it's dropped. This submission covers the brief's core
(matcher + stumper) without a "take it further" piece, named openly rather than gestured at.

A zero-cost replacement extension (e.g. scaling the catalogue further, multi-item detection, or automating
hard-case generation instead of only hand-shooting them) is still open — decide once the core is running on
real numbers, not before.

## Alternatives and why not (for now)

| Alternative | Decision | Reason |
|---|---|---|
| Fine-tune or metric learning | Next two weeks | Few views per SKU, overfit risk, time |
| CLIP/SigLIP alone | Baseline | Good at "gold necklace", weak at "this exact necklace" |
| Whole-image embedding | Baseline, expected to be replaced by cropping | Small object, background dominates |
| Cosine threshold for refusal | Baseline, expected to be replaced | Lookalikes |
| 100k scale, multi-item, automated stumper | Skipped | One extension done properly |

## Repo layout (target)

```
dyla/
├── README.md
├── DECISIONS.md
├── pyproject.toml            # uv, pinned deps
├── configs/default.yaml      # backbone, detector, K, verifier, threshold
├── src/dyla_match/
│   ├── catalogue/
│   │   ├── scrape.py         # polite scraper → images + products.csv with source URLs
│   │   ├── groups.py         # near-duplicate listings → design_group
│   │   └── own_items.py      # register a zero-cost self-sourced item (see below) as a catalogue entry
│   ├── localise.py           # detector + crop
│   ├── embed.py              # dinov2 / clip / siglip
│   ├── index.py              # FAISS build / add / search, product-level aggregation
│   ├── matcher.py            # photo → top-5 + score, per-stage timing (no refusal — dropped, see PLAN)
│   └── cli.py                # match, build-index, eval
├── eval/
│   ├── harness.py
│   ├── metrics.py            # top-1/5 (SKU + design), Wilson CI, FAR/FRR, ECE
│   └── report.md             # generated results, including rejected approaches
├── data/
│   ├── catalogue/
│   ├── stumper/{photos/, labels.csv}
│   └── index/
├── scripts/export_logs.py
├── logs/
└── docs/
```

### `data/stumper/labels.csv`

| column | meaning |
|---|---|
| `photo_id` | unique id |
| `file` | path under `data/stumper/photos/` |
| `sku_id` | catalogue product id, empty for negatives |
| `design_group` | from `groups.py`, empty for negatives |
| `in_catalogue` | `true` / `false` |
| `conditions` | `;`-separated: `clean, low_light, odd_angle, occlusion, clutter, motion_blur, reflection, hand_wrist, worn, whatsapp, screenshot` |
| `pair_id` | links hard photos to the same item's clean photo |
| `split` | `calib` or `test`, split by item so the same piece never appears in both |
| `notes` | free text |

### Evaluation

- Top-1 and top-5 at SKU and design level; per-condition accuracy with Wilson 95% CI; paired drop vs the clean
  photo; FAR/FRR at the chosen operating point plus the curve; ECE and reliability plot; latency p50/p95 per stage.
- Calibration and test split by item. Test photos frozen before any improvement work.
- Every experiment in `eval/report.md` records its config and numbers, including the ones I reject.

### Hardware

M2, 8 GB RAM. Small backbones (ViT-S/B). Catalogue images resized to around 512 px on the long side. Note whether
numbers come from CPU or MPS.

## Phases (about 15 hours)

| Phase | Work | Est. |
|---|---|---|
| 0 | Read the brief, research the company, plan | done |
| 1 | Pick brand and catalogue source, check it can be scraped, scrape 5k+ images, design groups | 2 h |
| 2 | Shoot and label the stumper set (100+ positives, ~20 lookalike negatives, clean pairs), then freeze it | 3 h |
| 3 | Baseline matcher: whole-image DINOv2 vs CLIP, FAISS, CLI, timing | 2 h |
| 4 | Harness, metrics, first report | 2 h |
| 5 | Improvements one at a time, each measured: crop, verification, calibrated refusal | 3 h |
| 6 | DECISIONS.md, clean-machine README test, logs, submit | 2–3 h |

Phases 2 and 3 can overlap once the catalogue exists.
