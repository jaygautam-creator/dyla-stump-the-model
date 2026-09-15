# DECISIONS

Thuli Studios (Dyla) take-home, Problem 2: visual jewellery matcher + hard-photo stumper harness.

## Catalogue: what and why

7,272 images across 1,010 catalogue entries: 400 Giva products + 607 Palmonas products (both scraped
via their public Shopify `/products.json` feed, robots.txt-checked first) + 300 Swashaa products
(scraped specifically because one stumper item turned out to be a real Swashaa SKU) + 3 self-sourced
items (a gold chain, a gold ring, and that Swashaa kada, before it was identified as a real product).
Jewellery because it's Dyla's sector. Near-duplicate listings (same product, different colour/plating)
are grouped by `design_group` so top-5 accuracy isn't punished for a same-design colour variant.

## Architecture chosen

Whole-image embedding (no fine-tuning: 1,010 products with a handful of views each would overfit
anything trained) → FAISS flat cosine search over image-level vectors, aggregated to product level by
max score → top-5. Crop-to-object preprocessing added in Phase 5 (below). No verification re-rank and
no calibrated refusal — see "What I rejected" and "Where it breaks."

## What I rejected (with evidence)

- **DINOv2 as the default backbone** — the plan expected DINOv2 to win at exact-instance retrieval
  ("this necklace" vs "a necklace"). Measured the opposite: CLIP 75.9% top-1 SKU vs DINOv2 46.6%
  on the 58 real photos (`eval/report.md` vs `eval/report_clip.md`). CLIP is the default as a result.
- **Equal-weight CLIP+DINOv2 ensemble** — tried a straightforward score-level fusion (average of the
  two backbones' cosine scores, weight fixed at 0.5/0.5 *before* looking at results, not searched
  against stumper accuracy). Real result: 55.2% top-1, worse than CLIP alone (75.9%) — DINOv2's much
  weaker signal drags the average down (`eval/report_ensemble_crop.md`). Rejected.
- **Calibrated cosine-threshold refusal** — not built. It needs a not-in-catalogue negative class, and
  none exists at zero budget (the only 3 physical items available all had to become catalogue
  entries to be genuine positives — see `docs/DECISION_LOG.md`, 2026-09-14). Fabricating negatives to
  report a refusal number would measure something that isn't real, so the FAR/FRR section of every
  report says this plainly instead.

## Evaluation methodology and why

Every stumper photo is a real phone photo of one of 3 items genuinely in the catalogue (no calib/test
split — 3 items is too small for one to mean anything, so everything is `test`, frozen once the real
58 photos were shot and labelled). Top-1/top-5 accuracy at SKU and design-group level, Wilson 95% CIs
(better-behaved than Wald at n≈15-60 per condition), per-condition breakdown, paired clean-vs-hard drop
per item, and per-item precision/recall/F1 as a closed-set identification metric.

**Real vs synthetic, reported separately, always.** The brief asks for 100+ hard photos; only 58 real
ones exist at zero budget. `scripts/augment_stumper.py` pads the set to 103 with crop/resize/rotate
transforms of the real 58, each tagged `synthetic_*`. A synthetic near-duplicate of a photo the matcher
has already "seen" (same lighting, background, physical instance) is not independent evidence of
accuracy the way a new real photo is. Every report in `eval/` has a "real phone photos only" headline
section and a separate "blended" section — the real section is the number to trust; synthetic exists
only to satisfy the photo-count minimum, and is never blended into a claim silently.

## Results

**Headline (real 58 photos, CLIP + crop): 75.9% top-1 SKU accuracy [63.5%, 85.0%].** That number hides
something important:

| item | source | n (real) | top-1 recall |
|---|---|---|---|
| gold chain | self-sourced | 17 | 100% |
| gold ring | self-sourced | 28 | 96.4% |
| **kada** | **genuine Swashaa SKU** | **13** | **0%** |

**The one item that's a genuine catalogue match never matches, in any configuration tried** (DINOv2,
CLIP, either with or without crop, or the ensemble — all 0% on the kada). A representative failure: a
clean phone photo of the kada scores 0.90 cosine against the *self-sourced gold ring* — a completely
different item — and the true Swashaa SKU doesn't appear in the top 5 at all. Plain, featureless gold
jewellery (a band, a bangle) looks nearly identical to both backbones at this level of visual detail;
the model is retrieving "a plain gold ring-shaped object," not this specific SKU. This is exactly the
whole-image weakness `docs/PLAN.md` predicted before any stumper photo was ever taken, and Phase 5's
crop-to-object step (see below) did not fix it.

**Worst conditions** (real photos, CLIP+crop): `blur` (0%, n=1 — too small to trust alone),
`occlusion` (50%, n=2), `reflection` (62.5%, n=16). `low_light` is actually the *best* condition
(100%, n=10) — counter to the naive expectation that dim photos are harder; on inspection these
low-light shots are still sharp and well-composed, just dim, which barely perturbs CLIP's embedding.

**Crop-to-object preprocessing** (`src/dyla_match/preprocess.py`, corner-based background subtraction,
no object detector — 8GB RAM budget): a small, mixed effect on real photos. It doesn't move the
aggregate top-1 number for either backbone, but the per-item breakdown shows it trading accuracy
between items (DINOv2: chain recall 88.2%→82.4%, ring recall 42.9%→46.4%) rather than a clean win. Kept
on by default anyway since it's free and slightly positive on the blended (103-photo) set, but it is
**not** the fix for the kada failure above.

## Trade-offs under the time limit

- No fine-tuning, no learned re-ranker, no object detector — all pretrained, off-the-shelf, explainable
  in one sentence each.
- Crop-to-object is a corner-background-subtraction heuristic, not a real detector. It fails silently
  (falls back to the whole image) whenever a photo's background isn't a clean, isolated surface.
- No refusal/false-accept-rate result at all, for the reason above.
- Only 3 physical items, only one of which is a genuine external catalogue match. The 75.9% headline
  number is really "100%/96.4% on two self-sourced items I embedded myself, 0% on the one real
  catalogue match" — a much less impressive claim than the aggregate suggests, named openly here
  rather than left in the aggregate.

## Where it breaks

- **Plain, low-detail jewellery is the matcher's real weak spot**, not lighting/angle/occlusion as
  originally hypothesized. A featureless gold band/bangle is retrieval-confusable with any other
  featureless gold band/bangle in the catalogue, regardless of backbone.
- Crop-to-object is a heuristic that can crop wrongly or not at all on busy backgrounds — never
  validated against catalogue images with a non-plain (lifestyle) background.
- No defense against a genuinely out-of-catalogue item: it will always return its 5 nearest neighbours
  with no refusal option, however irrelevant they are.

## Next two weeks

1. A learned or template-matched verification re-rank stage for the top-K candidates (e.g. local
   keypoint/edge matching on the clasp, stone setting, or engraving) — the actual fix for the
   plain-jewellery confusion above, which whole-image cosine similarity structurally cannot solve.
2. A handful of genuine not-in-catalogue negatives (even 10-15 zero-cost household items from other
   categories) to make the refusal FAR/FRR curve real instead of absent.
3. Replace the corner-background-subtraction crop with a small pretrained detector/segmenter once
   there's budget for the extra dependency, and re-measure against this heuristic's baseline.
4. More real stumper photos of the kada specifically, varying angle/distance, to check whether 0%
   recall is a property of the item (plausible, per above) or of this particular batch of 13 photos.
