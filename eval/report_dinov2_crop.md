# Evaluation report (dinov2, crop preprocessing)

## Headline: real phone photos only (excludes synthetic augmentation)

Backbone: `dinov2` (facebook/dinov2-small)
Photos: 58 (58 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 58 | 0.310 | [0.206, 0.438] |
| top5_sku | 58 | 0.379 | [0.266, 0.508] |
| top1_design | 58 | 0.310 | [0.206, 0.438] |
| top5_design | 58 | 0.379 | [0.266, 0.508] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 1 | 0.000 | [0.000, 0.793] |
| clean | 11 | 0.273 | [0.097, 0.566] |
| low_light | 10 | 0.300 | [0.108, 0.603] |
| occlusion | 2 | 0.000 | [0.000, 0.658] |
| odd_angle | 18 | 0.444 | [0.246, 0.663] |
| reflection | 16 | 0.250 | [0.102, 0.495] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.545 |
| kadda_pair | False | 0.000 |
| ring_pair | False | 0.346 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 13 | nan | 0.000 | 0.000 |
| own-gold-chain | 17 | 0.889 | 0.471 | 0.615 |
| own-gold-ring | 28 | 1.000 | 0.357 | 0.526 |
| **macro avg** |  | 0.630 | 0.276 | 0.381 |

---

## Blended: real + synthetic augmentation (padding to the brief's 100+ minimum)

Backbone: `dinov2` (facebook/dinov2-small)
Photos: 103 (103 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 103 | 0.252 | [0.178, 0.344] |
| top5_sku | 103 | 0.301 | [0.221, 0.395] |
| top1_design | 103 | 0.252 | [0.178, 0.344] |
| top5_design | 103 | 0.301 | [0.221, 0.395] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| blur | 2 | 0.000 | [0.000, 0.658] |
| clean | 22 | 0.227 | [0.101, 0.434] |
| low_light | 19 | 0.211 | [0.085, 0.433] |
| occlusion | 3 | 0.000 | [0.000, 0.561] |
| odd_angle | 32 | 0.406 | [0.255, 0.577] |
| reflection | 25 | 0.160 | [0.064, 0.347] |
| synthetic_combo | 10 | 0.000 | [0.000, 0.278] |
| synthetic_crop | 12 | 0.167 | [0.047, 0.448] |
| synthetic_lowres | 13 | 0.231 | [0.082, 0.503] |
| synthetic_tilt | 10 | 0.300 | [0.108, 0.603] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.292 |
| kadda_pair | False | 0.000 |
| ring_pair | False | 0.333 |

## FAR/FRR curve / ROC-AUC

Not computed: every photo in this stumper set is genuinely in the catalogue (the refusal extension was dropped for D1/D3 — no zero-cost not-in-catalogue negatives exist). FAR/FRR and ROC-AUC need a negative class; fabricating one here would measure something that isn't real. The precision/recall/F1 below is the honest substitute: a closed-set multi-class identification metric computed only from the positives we actually have.

## Per-item precision / recall / F1 (closed-set top-1 SKU identification)

| sku_id | n | precision | recall | f1 |
|---|---|---|---|---|
| 7557947424992 | 23 | nan | 0.000 | 0.000 |
| own-gold-chain | 30 | 0.750 | 0.300 | 0.429 |
| own-gold-ring | 50 | 1.000 | 0.340 | 0.507 |
| **macro avg** |  | 0.583 | 0.213 | 0.312 |