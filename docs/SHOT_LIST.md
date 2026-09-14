# Phase 2: shot list (zero-cost, 3 home items)

Rewritten 2026-09-14 — supersedes the earlier purchase-list version. See `DECISION_LOG.md`, "D1
superseded — zero-budget stumper set, refusal extension dropped."

## The 3 items

Gold ring, gold chain, gold kadda — already owned, no receipt, no known brand. Since they can't be
verified against a scraped catalogue, they're added *as* catalogue items themselves (self-sourced, not
scraped — disclosed as such in `DECISIONS.md`). The Giva/Palmonas scrape (6,350 images) is untouched and
still meets the "5,000+ scraped images" requirement on its own.

## Step 1 — one clean reference photo per item

For each of the 3 items: a plain background, good even light, the item laid flat or on a neutral surface,
in focus, filling most of the frame. This is that item's entire catalogue entry — there's no second angle
or on-model shot the way scraped products have, so get this one right.

Register each with:

```
python -m dyla_match.catalogue.own_items --title "Gold Ring" --category ring --photo path/to/clean_ring.jpg
python -m dyla_match.catalogue.own_items --title "Gold Chain" --category chain --photo path/to/clean_chain.jpg
python -m dyla_match.catalogue.own_items --title "Gold Kadda" --category bracelet --photo path/to/clean_kadda.jpg
```

This appends each to `data/catalogue/products.csv` with `vendor=own`, resizes and stores the image
alongside the scraped ones, and assigns it its own `design_group` (trivially itself — no variants to merge).
Rebuild both FAISS indexes afterwards (`dyla-match build-index`) so the 3 new items are searchable.

## Step 2 — stumper photos: ~34 per item, 100+ total

Same condition tags as before: `clean, low_light, odd_angle, occlusion, clutter, motion_blur, reflection,
hand_wrist, worn, whatsapp, screenshot`. `hand_wrist` fits the ring; `worn` fits the chain (neck) and kadda
(wrist).

Per item, since there's no second item in the category to split load with:

1. **Live shots** (~10): `clean` (can reuse the Step 1 photo, or take a second one — either is fine, it's
   just another labelled photo now, not the catalogue entry), `low_light`, `odd_angle` ×2 (two different
   angles), `occlusion` ×2 (finger, then cloth), `clutter`, `motion_blur`, `reflection`, plus `hand_wrist`
   or `worn`.
2. **Processed duplicates** (~24): WhatsApp a good chunk of the live shots to yourself and re-save
   (`whatsapp`, combined with the source condition, e.g. `occlusion;whatsapp`), and screenshot the rest as
   displayed on-screen (`screenshot`, same combination logic). This is most of the volume here — 3 items
   can't carry 100+ live-staged shots without becoming repetitive, but combined-condition photos from
   processing are realistic (a real hard photo often already has more than one condition) and cheap to
   produce.

~34/item × 3 = ~102 total. Log each into `data/stumper/labels.csv` as you go.

## No negatives, no refusal

Dropped — see `DECISION_LOG.md`. There's nothing left at zero cost to serve as genuine not-in-catalogue
items once the 3 home pieces became positives. `in_catalogue` is `true` for every row; the refusal-specific
columns/metrics (FAR/FRR) don't get real numbers this round.

## Calibration / test split

Only 3 items — too few to split by item and still calibrate anything meaningful. Recommendation: **no
calib/test split this round**, all 3 items go to `test`, and this is named as a real limitation in
`DECISIONS.md` rather than forcing a split that wouldn't mean anything with n=3. (No calibration work is
needed anyway now that refusal — the thing that used the calibration split — is dropped.)
