# DECISIONS

Thuli Studios (Dyla) take-home, Problem 2: visual jewellery matcher + hard-photo stumper harness.

## Catalogue

7,272 images, 1,010 products: 400 Giva + 607 Palmonas (public Shopify `/products.json` feeds,
robots.txt-checked) + 300 Swashaa (scraped after one stumper item turned out to be a real Swashaa SKU) +
3 self-sourced items (a gold chain, a gold ring, and that same Swashaa kada, registered before it was
identified as a real product). Jewellery because it's Dyla's sector. Near-duplicate listings are grouped
by `design_group` so top-5 accuracy isn't punished for a same-design colour variant.

## Architecture

Whole-image embedding (no fine-tuning — 1,010 products with a handful of views each would overfit
anything trained) → FAISS cosine search over image-level vectors, aggregated to product level by max
score → top-5. CLIP (`openai/clip-vit-base-patch32`), chosen over DINOv2 by direct measurement: 75.9%
vs 46.6% top-1 SKU accuracy on real photos.

## What was tried and rejected, with evidence

- **Crop-to-object preprocessing** — tried three times, fixing two real bugs along the way (one found
  by me, one by an independent audit, `docs/ANTIGRAVITY_AUDIT.md`): a background-noise bbox blowout,
  then an annular-jewellery bisection bug that cropped rings/bangles into unusable slivers. Even fully
  fixed, it still measures worse than the uncropped baseline (CLIP+crop 56.9% vs 75.9%). Rejected.
- **Equal-weight CLIP+DINOv2 ensemble** — weight fixed at 0.5/0.5 before looking at results. 55.2%
  top-1, worse than CLIP alone. Rejected.
- **Verification re-rank for the kada failure** — a wider candidate pool + a tighter second embedding
  pass. First measurement looked catastrophic (31.0%); the audit found a real double-crop bug behind
  it. Fixed, re-measured: 63.8% — closer to baseline but still below it, and the kada is still 0%.
  Rejected on the corrected number.
- **Calibrated refusal** — not built. Needs a not-in-catalogue negative class, and none exists at zero
  budget (all 3 available physical items had to become positives). Fabricating negatives would measure
  something that isn't real, so this is named as absent rather than faked.

**The pattern:** three ideas that should have helped by the original plan's own reasoning all measured
worse, twice each after fixing a real bug that made the first measurement look even worse than the
honest one. Plain whole-image CLIP, no preprocessing, no re-ranking, is still the best-measured
configuration — and that's a real finding about this catalogue's accuracy ceiling with off-the-shelf
embeddings, not a default reached by not trying.

## Evaluation methodology

Every stumper photo is a real phone photo of one of 3 items genuinely in the catalogue (no calib/test
split — 3 items is too small for one to mean anything; everything is `test`, frozen once the real 58
photos were shot). Top-1/top-5 accuracy at SKU and design-group level with Wilson 95% CIs, per-condition
breakdown, paired clean-vs-hard drop, per-item precision/recall/F1.

**Real vs synthetic, always reported separately.** The brief asks for 100+ photos; only 58 real ones
exist at zero budget. `scripts/augment_stumper.py` pads the set to 103 with tagged `synthetic_*`
crop/resize/rotate transforms of the real 58. A synthetic near-duplicate of a photo the matcher has
already seen isn't independent evidence the way a new real photo is — every report has a "real photos
only" headline and a separate "blended" section, and the real section is the number that counts.

## Results

**Headline (real 58 photos, shipped config): 75.9% top-1 SKU accuracy [63.5%, 85.0%].** Broken down by
item, that number hides something important:

| item | source | n | top-1 recall |
|---|---|---|---|
| gold chain | self-sourced | 17 | 100% |
| gold ring | self-sourced | 28 | 96.4% |
| **kada** | **genuine Swashaa SKU** | **13** | **0%** |

The one genuine external catalogue match never matches, in every configuration tried. A clean kada photo
scores 0.88-0.90 against the *self-sourced gold ring* — a different item — while the true SKU doesn't
even reach the top 5 (it exists in the embedding space, just consistently out-ranked).

**Why, checked directly, not assumed:** mean background colour of four photos —

| photo | mean background RGB |
|---|---|
| kada phone photo | [174, 171, 167] |
| self-sourced ring/chain reference photos | [179, 177, 171] / [172, 166, 160] |
| true Swashaa kada catalogue photo (studio) | [249, 249, 250] |

The self-sourced items' "catalogue" photo *is* a home phone photo, shot on the same table as every
query — their background matches by construction. The kada's real catalogue photo is a studio shot on
white, a genuinely different domain. The 100%/96.4% self-sourced numbers are partly background match,
not pure SKU discrimination; the kada's 0% is as much a domain gap as a plain-jewellery-similarity
problem. Nothing tried fixes either — a real fix needs to remove the background, not crop around it.

Worst condition: `reflection` (62.5%, n=16). Best: `low_light` (100%, n=10) — these shots are dim but
sharp and well-composed, which barely perturbs CLIP.

## Trade-offs and where it breaks

No fine-tuning, no object detector, no learned re-ranker — everything pretrained and explainable in one
sentence. The shipped matcher is deliberately the simplest thing tried, because everything smarter
measured worse here. No refusal capability (no negatives to build or test it against). Only 3 physical
items, one genuinely external — the 75.9% headline is really "100%/96.4% self-sourced, 0% real match,"
a materially different and less impressive claim than the aggregate suggests. No defense against a
genuinely out-of-catalogue item — it always returns 5 neighbours, however irrelevant.

## Next two weeks

1. Remove the background from the embedding (mask + composite onto neutral), not just crop tighter —
   targets the actual diagnosed cause, unlike the bounding-box crop tried three times here.
2. A real local-feature verification stage (keypoint/edge matching on the clasp or engraving, per the
   original design) rather than a second whole-crop embedding, which got closer to baseline but never
   beat it.
3. A handful of genuine not-in-catalogue negatives to make refusal real.
4. Re-shoot the self-sourced items' catalogue photos on a neutral background, so their accuracy isn't
   partly an artifact of matching the stumper photos' table.
5. More real kada photos, varying background, to separate "this item" from "this domain gap."
