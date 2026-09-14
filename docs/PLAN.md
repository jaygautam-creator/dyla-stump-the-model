# Plan

Drafted 2026-09-14. Some choices are still open (see `STATUS.md`). Any change goes into `DECISION_LOG.md`
with the reason.

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

## Refusal (the extension)

- **Start with the obvious version:** refuse when the top-1 cosine score is below a threshold. My expectation is
  that lookalike pieces score as high as real matches and no threshold separates them. I'll show the score
  distributions and ROC to check that.
- **Replacement:** verification inliers + margin + score, calibrated to a probability.
- **Negatives:** about 20 lookalike pieces that aren't in the catalogue, not random objects.
- **Protocol:** threshold and calibration fit on the calibration split only; false accept and false reject rates
  reported on the held-out test split, with the full trade-off curve.
- **Showing evidence:** draw the matched keypoints between the photo and the catalogue image.
- **Why it matters for a jewellery retailer:** a confident wrong "yes, we have this" on WhatsApp costs a sale and
  trust.
- **Known risk:** polished gold and stones move their highlights with the angle, so keypoints are unstable and
  verification may reject true matches. I'll measure how often.

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
│   │   └── groups.py         # near-duplicate listings → design_group
│   ├── localise.py           # detector + crop
│   ├── embed.py              # dinov2 / clip / siglip
│   ├── index.py              # FAISS build / add / search, product-level aggregation
│   ├── verify.py             # local matching + geometric check
│   ├── calibrate.py          # confidence model and refusal threshold
│   ├── matcher.py            # photo → top-5 + confidence | NOT_IN_CATALOGUE, per-stage timing
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
