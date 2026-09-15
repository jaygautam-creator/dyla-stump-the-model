# Evaluation report (CLIP + crop + verification re-rank)

## Headline: real phone photos only (excludes synthetic augmentation)

Backbone: `clip + verification re-rank (crop)` (openai/clip-vit-base-patch32, tight-crop second pass)
Photos: 58 (58 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 58 | 0.310 | [0.206, 0.438] |
| top5_sku | 58 | 0.586 | [0.458, 0.704] |
| top1_design | 58 | 0.310 | [0.206, 0.438] |
| top5_design | 58 | 0.586 | [0.458, 0.704] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 1 | 0.000 | [0.000, 0.793] |
| clean | 11 | 0.364 | [0.152, 0.646] |
| low_light | 10 | 0.300 | [0.108, 0.603] |
| occlusion | 2 | 0.500 | [0.095, 0.905] |
| odd_angle | 18 | 0.389 | [0.203, 0.614] |
| reflection | 16 | 0.188 | [0.066, 0.430] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.364 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.385 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 13 | nan | 0.000 | 0.000 |
| own-gold-chain | 17 | 0.857 | 0.353 | 0.500 |
| own-gold-ring | 28 | 0.800 | 0.429 | 0.558 |
| **macro avg** |  | 0.552 | 0.261 | 0.353 |

---

## Blended: real + synthetic augmentation

Backbone: `clip + verification re-rank (crop)` (openai/clip-vit-base-patch32, tight-crop second pass)
Photos: 103 (103 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 103 | 0.272 | [0.195, 0.365] |
| top5_sku | 103 | 0.485 | [0.391, 0.581] |
| top1_design | 103 | 0.272 | [0.195, 0.365] |
| top5_design | 103 | 0.485 | [0.391, 0.581] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 2 | 0.000 | [0.000, 0.658] |
| clean | 22 | 0.273 | [0.132, 0.482] |
| low_light | 19 | 0.263 | [0.118, 0.488] |
| occlusion | 3 | 0.333 | [0.061, 0.792] |
| odd_angle | 32 | 0.375 | [0.229, 0.547] |
| reflection | 25 | 0.160 | [0.064, 0.347] |
| synthetic_combo | 10 | 0.100 | [0.018, 0.404] |
| synthetic_crop | 12 | 0.167 | [0.047, 0.448] |
| synthetic_lowres | 13 | 0.385 | [0.177, 0.645] |
| synthetic_tilt | 10 | 0.200 | [0.057, 0.510] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.250 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.375 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 23 | nan | 0.000 | 0.000 |
| own-gold-chain | 30 | 0.800 | 0.267 | 0.400 |
| own-gold-ring | 50 | 0.769 | 0.400 | 0.526 |
| **macro avg** |  | 0.523 | 0.222 | 0.309 |