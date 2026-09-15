# Evaluation report (CLIP + crop + verification re-rank)

## Headline: real phone photos only (excludes synthetic augmentation)

Backbone: `clip + verification re-rank (crop)` (openai/clip-vit-base-patch32, tight-crop second pass)
Photos: 58 (58 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 58 | 0.638 | [0.509, 0.749] |
| top5_sku | 58 | 0.759 | [0.635, 0.850] |
| top1_design | 58 | 0.638 | [0.509, 0.749] |
| top5_design | 58 | 0.759 | [0.635, 0.850] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 1 | 0.000 | [0.000, 0.793] |
| clean | 11 | 0.545 | [0.280, 0.787] |
| low_light | 10 | 0.900 | [0.596, 0.982] |
| occlusion | 2 | 0.500 | [0.095, 0.905] |
| odd_angle | 18 | 0.722 | [0.491, 0.875] |
| reflection | 16 | 0.500 | [0.280, 0.720] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.818 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.846 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 13 | nan | 0.000 | 0.000 |
| own-gold-chain | 17 | 0.722 | 0.765 | 0.743 |
| own-gold-ring | 28 | 0.686 | 0.857 | 0.762 |
| **macro avg** |  | 0.469 | 0.541 | 0.502 |

---

## Blended: real + synthetic augmentation

Backbone: `clip + verification re-rank (crop)` (openai/clip-vit-base-patch32, tight-crop second pass)
Photos: 103 (103 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 103 | 0.573 | [0.476, 0.664] |
| top5_sku | 103 | 0.689 | [0.595, 0.771] |
| top1_design | 103 | 0.573 | [0.476, 0.664] |
| top5_design | 103 | 0.689 | [0.595, 0.771] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 2 | 0.000 | [0.000, 0.658] |
| clean | 22 | 0.455 | [0.269, 0.653] |
| low_light | 19 | 0.789 | [0.567, 0.915] |
| occlusion | 3 | 0.667 | [0.208, 0.939] |
| odd_angle | 32 | 0.656 | [0.483, 0.796] |
| reflection | 25 | 0.440 | [0.267, 0.629] |
| synthetic_combo | 10 | 0.300 | [0.108, 0.603] |
| synthetic_crop | 12 | 0.500 | [0.254, 0.746] |
| synthetic_lowres | 13 | 0.692 | [0.424, 0.873] |
| synthetic_tilt | 10 | 0.400 | [0.168, 0.687] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.542 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.833 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 23 | nan | 0.000 | 0.000 |
| own-gold-chain | 30 | 0.739 | 0.567 | 0.642 |
| own-gold-ring | 50 | 0.677 | 0.840 | 0.750 |
| **macro avg** |  | 0.472 | 0.469 | 0.464 |