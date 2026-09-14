# Phase 2: purchase list, store visit, and shot list

Drafted 2026-09-14, after Phase 1 (catalogue: 6,350 images, 1,007 products, design groups). Any change
goes into `DECISION_LOG.md`. This plans the work; it doesn't execute it — buying, visiting the store, and
shooting are physical steps for me to do.

## Purchase list — 6 owned items (~₹12,400)

Two per category, one Giva + one Palmonas, so the positive set covers both vendors and both a distinctive
and a plain/generic design per category (a plain solitaire is the harder retrieval case — closer to
lookalikes than an ornate piece is).

| # | Vendor | Item | Price | Product URL |
|---|---|---|---|---|
| 1 | Giva | Silver Aurora Marquis Ring | ₹1,599 | giva.co/products/silver-aurora-marquis-ring |
| 2 | Palmonas | Minimal Solitaire 925 Sterling Silver Ring | ₹2,892 | palmonas.com/products/minimal-solitaire-925-sterling-silver-ring-93992 |
| 3 | Giva | Silver Multi Twinkle Earrings | ₹1,199 | giva.co/products/silver-multi-twinkle-earrings |
| 4 | Palmonas | Dewdrop Bezel 925 Sterling Silver Studs | ₹1,799 | palmonas.com/products/dewdrop-bezel-925-sterling-silver-studs-97059 |
| 5 | Giva | Silver Branchful Necklace | ₹1,999 | giva.co/products/silver-branchful-necklace |
| 6 | Palmonas | Sculptural Knot 925 Sterling Silver Necklace | ₹2,889 | palmonas.com/products/sculptural-knot-925-sterling-silver-necklace-56027 |

Total ≈ ₹12,377 (a bit over the ~₹11k estimate — solitaire/knot designs ran a little higher than the
category median). Each of these has a `product_id` already in `data/catalogue/products.csv`, so `sku_id`
and `design_group` for the labelled photos come straight from there.

## Store visit — lookalike negatives, not more positives

D1 originally framed the store visit as "more items + negatives," but on reflection it should be **negatives
only**: CaratLane/Tanishq/BlueStone are different retailers, not in the Giva/Palmonas catalogue, so anything
photographed there is by definition not-in-catalogue — exactly what a lookalike negative needs to be. Trying
to also use it for positives would mean owning nothing to re-shoot under hard conditions later.

- Target: ~20 negative photos from ~12–15 pieces, one visit.
- Mirror the purchased categories — rings, stud/drop earrings, pendant necklaces — so negatives are
  genuine style lookalikes (plausible "do you have this?" candidates), not random jewellery.
- Per piece: 1 clean photo, plus a second under whatever condition the store setting gives for free
  (glass-case reflection, display lighting, odd angle reaching around other stock) — no need to stage more,
  the environment does it.
- Ask staff before photographing (per D1's revisit clause: if refused, fall back to a different online-only
  brand's catalogue images as the negative source instead).
- Labels: `sku_id` and `design_group` empty, `in_catalogue = false`.

## Shot list per owned item (~16–18 photos/item → 100+ total)

Condition tags from `docs/PLAN.md`'s `labels.csv` schema: `clean, low_light, odd_angle, occlusion, clutter,
motion_blur, reflection, hand_wrist, worn, whatsapp, screenshot`.

`hand_wrist` applies to the two rings; `worn` applies to earrings and necklaces (on ear / on neck). Per item:

1. **Live shots** (physically staged, ~9 per item): `clean`, `low_light`, `odd_angle`, `occlusion`,
   `clutter`, `motion_blur`, `reflection`, plus `hand_wrist` (rings) or `worn` (earrings/necklaces), plus one
   repeat of a harder condition with a different instance (e.g. a second `occlusion` shot — cloth instead of
   a finger — or a second `odd_angle`).
2. **Processed duplicates** (no new staging, ~7–9 per item): send a handful of the live photos to myself on
   WhatsApp and re-save (`whatsapp` condition, combined with whatever the source photo already had, e.g.
   `clean;whatsapp` or `occlusion;whatsapp`), and screenshot a handful as displayed on-screen (`screenshot`,
   same combination logic). This is the cheapest way to get combined-condition photos and directly serves
   the "confounding" point in `PLAN.md` — most real hard photos aren't single-condition.

This lands each item around 16–18 labelled photos, 6 items ≈ 100–108 total, without needing more purchases
or more live staging than the ~9 base shots.

## Calibration / test split (by item, frozen before improvement work)

Small n — flag this as a stumper-set weakness in `DECISIONS.md`, not something to paper over.

- **Positives:** 2 items → `calib` (one ring, one necklace — pick the plainer design of each pair so
  calibration isn't fit on the easiest cases), 4 items → `test`.
- **Negatives:** roughly 30/70 by item — ~4 items' worth → `calib`, ~8–11 items' worth → `test`.

## Open items before shooting

- Exact CaratLane/Tanishq/BlueStone branch and date — mine to schedule.
- Confirm staff will allow photography before relying on the store visit; if not, fall back per D1.
- Once purchases arrive: shoot in the order clean → live hard conditions → process whatsapp/screenshot
  duplicates, and log each item's photos into `data/stumper/labels.csv` as they're taken, not in one batch
  at the end.
