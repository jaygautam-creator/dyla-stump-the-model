# Evaluation report (dinov2, crop preprocessing)

## Headline: real phone photos only (excludes synthetic augmentation)

Backbone: `dinov2` (facebook/dinov2-small)
Photos: 58 (58 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 58 | 0.466 | [0.343, 0.592] |
| top5_sku | 58 | 0.517 | [0.392, 0.641] |
| top1_design | 58 | 0.466 | [0.343, 0.592] |
| top5_design | 58 | 0.517 | [0.392, 0.641] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 1 | 0.000 | [0.000, 0.793] |
| clean | 11 | 0.727 | [0.434, 0.903] |
| low_light | 10 | 0.400 | [0.168, 0.687] |
| occlusion | 2 | 0.000 | [0.000, 0.658] |
| odd_angle | 18 | 0.556 | [0.337, 0.754] |
| reflection | 16 | 0.312 | [0.142, 0.556] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.727 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.423 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 13 | nan | 0.000 | 0.000 |
| own-gold-chain | 17 | 1.000 | 0.824 | 0.903 |
| own-gold-ring | 28 | 1.000 | 0.464 | 0.634 |
| **macro avg** |  | 0.667 | 0.429 | 0.512 |

---

## Blended: real + synthetic augmentation (padding to the brief's 100+ minimum)

Backbone: `dinov2` (facebook/dinov2-small)
Photos: 103 (103 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 103 | 0.485 | [0.391, 0.581] |
| top5_sku | 103 | 0.524 | [0.429, 0.618] |
| top1_design | 103 | 0.485 | [0.391, 0.581] |
| top5_design | 103 | 0.524 | [0.429, 0.618] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 2 | 0.000 | [0.000, 0.658] |
| clean | 22 | 0.727 | [0.518, 0.868] |
| low_light | 19 | 0.421 | [0.231, 0.637] |
| occlusion | 3 | 0.000 | [0.000, 0.561] |
| odd_angle | 32 | 0.562 | [0.393, 0.718] |
| reflection | 25 | 0.320 | [0.172, 0.516] |
| synthetic_combo | 10 | 0.400 | [0.168, 0.687] |
| synthetic_crop | 12 | 0.417 | [0.193, 0.680] |
| synthetic_lowres | 13 | 0.538 | [0.291, 0.768] |
| synthetic_tilt | 10 | 0.700 | [0.397, 0.892] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.875 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.438 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 23 | nan | 0.000 | 0.000 |
| own-gold-chain | 30 | 1.000 | 0.900 | 0.947 |
| own-gold-ring | 50 | 1.000 | 0.460 | 0.630 |
| **macro avg** |  | 0.667 | 0.453 | 0.526 |