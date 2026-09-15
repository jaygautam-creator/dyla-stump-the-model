# Evaluation report (clip)

## Headline: real phone photos only (excludes synthetic augmentation)

Backbone: `clip` (openai/clip-vit-base-patch32)
Photos: 58 (58 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 58 | 0.759 | [0.635, 0.850] |
| top5_sku | 58 | 0.776 | [0.653, 0.864] |
| top1_design | 58 | 0.759 | [0.635, 0.850] |
| top5_design | 58 | 0.776 | [0.653, 0.864] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 1 | 0.000 | [0.000, 0.793] |
| clean | 11 | 0.727 | [0.434, 0.903] |
| low_light | 10 | 1.000 | [0.722, 1.000] |
| occlusion | 2 | 0.500 | [0.095, 0.905] |
| odd_angle | 18 | 0.833 | [0.608, 0.942] |
| reflection | 16 | 0.625 | [0.386, 0.815] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 1.000 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.962 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 13 | nan | 0.000 | 0.000 |
| own-gold-chain | 17 | 1.000 | 1.000 | 1.000 |
| own-gold-ring | 28 | 0.711 | 0.964 | 0.818 |
| **macro avg** |  | 0.570 | 0.655 | 0.606 |

---

## Blended: real + synthetic augmentation (padding to the brief's 100+ minimum)

Backbone: `clip` (openai/clip-vit-base-patch32)
Photos: 103 (103 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 103 | 0.718 | [0.625, 0.796] |
| top5_sku | 103 | 0.777 | [0.687, 0.846] |
| top1_design | 103 | 0.718 | [0.625, 0.796] |
| top5_design | 103 | 0.777 | [0.687, 0.846] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 2 | 0.000 | [0.000, 0.658] |
| clean | 22 | 0.727 | [0.518, 0.868] |
| low_light | 19 | 0.947 | [0.754, 0.991] |
| occlusion | 3 | 0.333 | [0.061, 0.792] |
| odd_angle | 32 | 0.781 | [0.612, 0.890] |
| reflection | 25 | 0.560 | [0.371, 0.733] |
| synthetic_combo | 10 | 0.600 | [0.313, 0.832] |
| synthetic_crop | 12 | 0.750 | [0.468, 0.911] |
| synthetic_lowres | 13 | 0.769 | [0.497, 0.918] |
| synthetic_tilt | 10 | 0.500 | [0.237, 0.763] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.958 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.896 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 23 | nan | 0.000 | 0.000 |
| own-gold-chain | 30 | 1.000 | 0.967 | 0.983 |
| own-gold-ring | 50 | 0.726 | 0.900 | 0.804 |
| **macro avg** |  | 0.575 | 0.622 | 0.596 |