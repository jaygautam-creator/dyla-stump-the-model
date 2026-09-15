# Evaluation report (clip, crop preprocessing)

## Headline: real phone photos only (excludes synthetic augmentation)

Backbone: `clip` (openai/clip-vit-base-patch32)
Photos: 58 (58 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 58 | 0.569 | [0.441, 0.688] |
| top5_sku | 58 | 0.603 | [0.475, 0.719] |
| top1_design | 58 | 0.569 | [0.441, 0.688] |
| top5_design | 58 | 0.603 | [0.475, 0.719] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 1 | 0.000 | [0.000, 0.793] |
| clean | 11 | 0.364 | [0.152, 0.646] |
| low_light | 10 | 0.800 | [0.490, 0.943] |
| occlusion | 2 | 0.500 | [0.095, 0.905] |
| odd_angle | 18 | 0.722 | [0.491, 0.875] |
| reflection | 16 | 0.438 | [0.231, 0.668] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.545 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.885 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 13 | nan | 0.000 | 0.000 |
| own-gold-chain | 17 | 0.800 | 0.471 | 0.593 |
| own-gold-ring | 28 | 0.926 | 0.893 | 0.909 |
| **macro avg** |  | 0.575 | 0.454 | 0.501 |

---

## Blended: real + synthetic augmentation (padding to the brief's 100+ minimum)

Backbone: `clip` (openai/clip-vit-base-patch32)
Photos: 103 (103 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 103 | 0.485 | [0.391, 0.581] |
| top5_sku | 103 | 0.583 | [0.486, 0.673] |
| top1_design | 103 | 0.485 | [0.391, 0.581] |
| top5_design | 103 | 0.583 | [0.486, 0.673] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 2 | 0.000 | [0.000, 0.658] |
| clean | 22 | 0.318 | [0.164, 0.527] |
| low_light | 19 | 0.579 | [0.363, 0.769] |
| occlusion | 3 | 0.333 | [0.061, 0.792] |
| odd_angle | 32 | 0.656 | [0.483, 0.796] |
| reflection | 25 | 0.400 | [0.234, 0.593] |
| synthetic_combo | 10 | 0.100 | [0.018, 0.404] |
| synthetic_crop | 12 | 0.417 | [0.193, 0.680] |
| synthetic_lowres | 13 | 0.538 | [0.291, 0.768] |
| synthetic_tilt | 10 | 0.400 | [0.168, 0.687] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.333 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.792 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 23 | nan | 0.000 | 0.000 |
| own-gold-chain | 30 | 0.833 | 0.333 | 0.476 |
| own-gold-ring | 50 | 0.930 | 0.800 | 0.860 |
| **macro avg** |  | 0.588 | 0.378 | 0.445 |