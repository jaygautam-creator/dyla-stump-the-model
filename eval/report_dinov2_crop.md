# Evaluation report (dinov2, crop preprocessing)

## Headline: real phone photos only (excludes synthetic augmentation)

Backbone: `dinov2` (facebook/dinov2-small)
Photos: 58 (58 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 58 | 0.328 | [0.221, 0.456] |
| top5_sku | 58 | 0.379 | [0.266, 0.508] |
| top1_design | 58 | 0.328 | [0.221, 0.456] |
| top5_design | 58 | 0.379 | [0.266, 0.508] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 1 | 0.000 | [0.000, 0.793] |
| clean | 11 | 0.273 | [0.097, 0.566] |
| low_light | 10 | 0.300 | [0.108, 0.603] |
| occlusion | 2 | 0.000 | [0.000, 0.658] |
| odd_angle | 18 | 0.500 | [0.290, 0.710] |
| reflection | 16 | 0.250 | [0.102, 0.495] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.364 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.462 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 13 | nan | 0.000 | 0.000 |
| own-gold-chain | 17 | 1.000 | 0.294 | 0.455 |
| own-gold-ring | 28 | 1.000 | 0.500 | 0.667 |
| **macro avg** |  | 0.667 | 0.265 | 0.374 |

---

## Blended: real + synthetic augmentation (padding to the brief's 100+ minimum)

Backbone: `dinov2` (facebook/dinov2-small)
Photos: 103 (103 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 103 | 0.320 | [0.238, 0.416] |
| top5_sku | 103 | 0.379 | [0.291, 0.475] |
| top1_design | 103 | 0.320 | [0.238, 0.416] |
| top5_design | 103 | 0.379 | [0.291, 0.475] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 2 | 0.000 | [0.000, 0.658] |
| clean | 22 | 0.273 | [0.132, 0.482] |
| low_light | 19 | 0.263 | [0.118, 0.488] |
| occlusion | 3 | 0.000 | [0.000, 0.561] |
| odd_angle | 32 | 0.531 | [0.364, 0.691] |
| reflection | 25 | 0.200 | [0.089, 0.391] |
| synthetic_combo | 10 | 0.000 | [0.000, 0.278] |
| synthetic_crop | 12 | 0.333 | [0.138, 0.609] |
| synthetic_lowres | 13 | 0.385 | [0.177, 0.645] |
| synthetic_tilt | 10 | 0.500 | [0.237, 0.763] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.375 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.438 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 23 | nan | 0.000 | 0.000 |
| own-gold-chain | 30 | 1.000 | 0.333 | 0.500 |
| own-gold-ring | 50 | 1.000 | 0.460 | 0.630 |
| **macro avg** |  | 0.667 | 0.264 | 0.377 |