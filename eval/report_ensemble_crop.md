# Evaluation report (dinov2 + clip ensemble, crop preprocessing, equal weight)

## Headline: real phone photos only (excludes synthetic augmentation)

Backbone: `dinov2+clip ensemble (crop, equal-weight)` (facebook/dinov2-small + openai/clip-vit-base-patch32)
Photos: 58 (58 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 58 | 0.552 | [0.425, 0.673] |
| top5_sku | 58 | 0.690 | [0.562, 0.794] |
| top1_design | 58 | 0.552 | [0.425, 0.673] |
| top5_design | 58 | 0.690 | [0.562, 0.794] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 1 | 0.000 | [0.000, 0.793] |
| clean | 11 | 0.727 | [0.434, 0.903] |
| low_light | 10 | 0.500 | [0.237, 0.763] |
| occlusion | 2 | 0.500 | [0.095, 0.905] |
| odd_angle | 18 | 0.556 | [0.337, 0.754] |
| reflection | 16 | 0.500 | [0.280, 0.720] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 1.000 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.500 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 13 | nan | 0.000 | 0.000 |
| own-gold-chain | 17 | 1.000 | 1.000 | 1.000 |
| own-gold-ring | 28 | 1.000 | 0.536 | 0.698 |
| **macro avg** |  | 0.667 | 0.512 | 0.566 |

---

## Blended: real + synthetic augmentation

Backbone: `dinov2+clip ensemble (crop, equal-weight)` (facebook/dinov2-small + openai/clip-vit-base-patch32)
Photos: 103 (103 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 103 | 0.544 | [0.448, 0.637] |
| top5_sku | 103 | 0.699 | [0.605, 0.779] |
| top1_design | 103 | 0.544 | [0.448, 0.637] |
| top5_design | 103 | 0.699 | [0.605, 0.779] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 2 | 0.000 | [0.000, 0.658] |
| clean | 22 | 0.727 | [0.518, 0.868] |
| low_light | 19 | 0.526 | [0.317, 0.727] |
| occlusion | 3 | 0.333 | [0.061, 0.792] |
| odd_angle | 32 | 0.562 | [0.393, 0.718] |
| reflection | 25 | 0.440 | [0.267, 0.629] |
| synthetic_combo | 10 | 0.500 | [0.237, 0.763] |
| synthetic_crop | 12 | 0.417 | [0.193, 0.680] |
| synthetic_lowres | 13 | 0.538 | [0.291, 0.768] |
| synthetic_tilt | 10 | 0.700 | [0.397, 0.892] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 1.000 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.500 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 23 | nan | 0.000 | 0.000 |
| own-gold-chain | 30 | 1.000 | 1.000 | 1.000 |
| own-gold-ring | 50 | 1.000 | 0.520 | 0.684 |
| **macro avg** |  | 0.667 | 0.507 | 0.561 |