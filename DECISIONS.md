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
- **Crop-to-object preprocessing** — tried three times, twice fixing a real bug found along the way
  (once by me, once by an independent audit — `docs/ANTIGRAVITY_AUDIT.md`, 2026-09-15). v1 (naive
  min/max bounding box) measured as a small, roughly neutral effect, but was blowing the bbox out to
  nearly the full frame on photos with scattered background noise. v2 ("largest contiguous dense
  region") fixed that, but measured *worse*: CLIP+crop 75.9% → 51.7%, DINOv2+crop 46.6% → 31.0%. The
  audit found why: "largest single run" bisects annular jewellery (rings, bangles) whose density
  profile dips at the hollow centre, discarding one whole side (confirmed directly: a bangle catalogue
  image cropped to a 56×269-pixel sliver, keeping one rim and losing the rest). v3 (union extent of
  every run above threshold, not just the largest) fixed that specific bisection and recovered some
  ground — CLIP+crop 51.7% → 56.9%, DINOv2+crop 31.0% → 32.8% — but **still measures worse than plain
  whole-image embedding on both backbones**. Rejected after three honestly-measured, bug-fixed attempts;
  `configs/default.yaml` uses the plain, uncropped whole-image embedding.
- **Equal-weight CLIP+DINOv2 ensemble** — tried a straightforward score-level fusion (average of the
  two backbones' cosine scores, weight fixed at 0.5/0.5 *before* looking at results, not searched
  against stumper accuracy). Real result: 55.2% top-1, worse than CLIP alone (75.9%) — DINOv2's much
  weaker signal drags the average down (`eval/report_ensemble_crop.md`). Rejected.
- **Verification re-rank for the kada failure** — built a wider-candidate-pool + tighter-crop-fusion
  re-rank (`src/dyla_match/rerank.py`). First measurement: real top-1 SKU **dropped from 75.9% to
  31.0%**, which read as "the tight-crop signal is just too noisy." The same external audit found the
  real cause: the embedder passed into `verify_rerank` still had its own crop preprocessing switched on
  (loaded from `configs/clip_crop.yaml`), so every tight crop this function built was being **cropped a
  second time** inside `embedder.embed()` — a crop-of-a-crop, compounding into the degenerate slivers
  that made the "noisy signal" theory look right without being the real explanation. Fixed (the function
  now disables the embedder's own crop flag while it runs its own explicit crop) and re-measured: real
  top-1 recovers to **63.8%** — much closer to baseline, but still below it, and the kada still scores
  0% recall either way. Rejected on the corrected number, not the buggy one; kept in the repo as a
  documented experiment, not wired into the default config.
- **Calibrated cosine-threshold refusal** — not built. It needs a not-in-catalogue negative class, and
  none exists at zero budget (the only 3 physical items available all had to become catalogue
  entries to be genuine positives — see `docs/DECISION_LOG.md`, 2026-09-14). Fabricating negatives to
  report a refusal number would measure something that isn't real, so the FAR/FRR section of every
  report says this plainly instead.

**Pattern worth naming on its own:** three separate ideas that all "should" have helped, per PLAN.md's
own reasoning (crop, twice; ensemble; verification re-rank) all measured *worse* than the plain Phase 4
baseline. The whole-image CLIP embedding, no preprocessing, no re-ranking, is still the best-measured
configuration in this repo. That is itself a finding — this catalogue/photo set's accuracy ceiling with
pretrained, off-the-shelf, un-fine-tuned embeddings looks close to whatever whole-image CLIP already gets.

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

**Headline (real 58 photos, plain whole-image CLIP, the shipped config): 75.9% top-1 SKU accuracy
[63.5%, 85.0%].** That number hides something important:

| item | source | n (real) | top-1 recall |
|---|---|---|---|
| gold chain | self-sourced | 17 | 100% |
| gold ring | self-sourced | 28 | 96.4% |
| **kada** | **genuine Swashaa SKU** | **13** | **0%** |

**The one item that's a genuine catalogue match never matches, in any configuration tried** (DINOv2,
CLIP, with or without crop, the ensemble, or the verification re-rank — all 0% on the kada, see "What I
rejected"). A representative failure: a clean phone photo of the kada scores 0.88-0.90 cosine against
the *self-sourced gold ring* — a completely different item — and the true Swashaa SKU doesn't appear in
the top 5 at all (it exists in the embedding space, at roughly unique-product rank 40-70, just
consistently out-ranked).

**Corrected diagnosis (2026-09-15, via `docs/ANTIGRAVITY_AUDIT.md`):** the original write-up here
attributed this purely to "plain, featureless gold jewellery looking alike." That's real but incomplete
— the bigger, verified factor is a **background/domain confound that specifically favours the two
self-sourced items over the kada**. Checked directly (mean corner RGB, four photos):

| photo | mean background RGB |
|---|---|
| kada phone photo | [174, 171, 167] |
| **self-sourced gold ring reference photo** | **[179, 177, 171]** |
| **self-sourced gold chain reference photo** | **[172, 166, 160]** |
| true Swashaa kada catalogue photo (studio) | [249, 249, 250] |

The self-sourced items' catalogue "ground truth" photo *is* a home phone photo, shot on the same table
as every stumper photo — so their background matches every query almost by construction. The kada's
real catalogue photo is a studio packshot on white, a different domain entirely. A whole-image embedding
that's meant to encode "this specific piece" is partly encoding "this specific tabletop," and only the
kada is forced to cross that phone-to-studio gap. So the 100%/96.4% self-sourced numbers are inflated by
background match, not solely genuine SKU-level discrimination — and the kada's 0% is at least as much a
domain-gap problem as a plain-jewellery-similarity problem. Nothing tried in Phase 5 fixes either factor
(see "What I rejected"); a real fix needs to remove the background from the embedding, not just crop
tighter around the object (which, per "What I rejected," made things worse three separate times).

**Worst conditions** (real photos, CLIP, default config): `blur` (0%, n=1 — too small to trust alone),
`occlusion` (50%, n=2), `reflection` (62.5%, n=16). `low_light` is actually the *best* condition
(100%, n=10) — counter to the naive expectation that dim photos are harder; on inspection these
low-light shots are still sharp and well-composed, just dim, which barely perturbs CLIP's embedding.

**Crop-to-object preprocessing and verification re-rank were both tried and both rejected** (see "What I
rejected" above) — the plain whole-image CLIP embedding, no preprocessing, remains the best-measured
configuration and is what `configs/default.yaml` ships.

## Trade-offs under the time limit

- No fine-tuning, no learned re-ranker, no object detector — all pretrained, off-the-shelf, explainable
  in one sentence each. The shipped matcher is deliberately the simplest thing tried: plain whole-image
  cosine retrieval, because every attempt to add something smarter (crop, ensemble, re-rank) measured
  worse on this specific catalogue/photo set.
- No refusal/false-accept-rate result at all, for the reason above.
- Only 3 physical items, only one of which is a genuine external catalogue match. The 75.9% headline
  number is really "100%/96.4% on two self-sourced items I embedded myself, 0% on the one real
  catalogue match" — a much less impressive claim than the aggregate suggests, named openly here
  rather than left in the aggregate.

## Where it breaks

- **Background/domain match, not just plain jewellery, drives the biggest accuracy gap** — the
  self-sourced items' catalogue photos share a background with every query photo (same table); the
  kada's real catalogue photo doesn't (studio white). See "Results" for the measured RGB comparison.
  This means the headline number is not a fair, apples-to-apples measure of SKU-level accuracy.
- A background-subtraction-heuristic crop (tried three times, two real bugs found and fixed along the
  way — one by me, one by an independent audit) and a whole-crop-embedding verification pass both made
  accuracy worse, not better, even after the fixes — see "What I rejected." A real fix needs to remove
  the background, not just crop around the object.
- No defense against a genuinely out-of-catalogue item: it will always return its 5 nearest neighbours
  with no refusal option, however irrelevant they are.

## Next two weeks

1. **Remove the background from the embedding, not just crop tighter around the object** — the
   corrected diagnosis above points at background/domain match, not only object-level detail, so a real
   foreground-mask-and-composite-onto-neutral-background step (not the bounding-box crop tried three
   times here) is the more targeted fix, worth trying before another verification/re-rank attempt.
2. A real local-feature verification stage for the top-K candidates (e.g. keypoint/edge matching via
   SuperPoint+LightGlue, per `docs/PLAN.md`'s original design, or DINOv2 patch mutual-nearest-neighbours)
   on the clasp, stone setting, or engraving — the tight-crop-embedding-fusion tried here got closer to
   baseline once its own bug was fixed (63.8% vs 75.9%) but never beat it; a real verification signal
   might.
3. A handful of genuine not-in-catalogue negatives (even 10-15 zero-cost household items from other
   categories) to make the refusal FAR/FRR curve real instead of absent.
4. Re-shoot the self-sourced items' catalogue reference photos on a neutral/white background instead of
   the same home table the stumper photos use — as currently set up, their high accuracy is partly an
   artifact of matching backgrounds, not a fair comparison to how the kada is evaluated.
5. More real stumper photos of the kada specifically, varying angle/distance/background, to check
   whether 0% recall is a property of the item+domain-gap (plausible, per above) or of this particular
   batch of 13 photos.
