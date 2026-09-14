# Evaluation report

Backbone: `dinov2` (facebook/dinov2-small)
Photos: 58 (58 positive, 0 negative)

## Overall (SKU and design level, positives only)

| metric | n | accuracy | 95% CI |
|---|---|---|---|
| top1_sku | 58 | 0.466 | [0.343, 0.592] |
| top5_sku | 58 | 0.500 | [0.375, 0.625] |
| top1_design | 58 | 0.466 | [0.343, 0.592] |
| top5_design | 58 | 0.500 | [0.375, 0.625] |

## Per-condition top-1 SKU accuracy

| condition | n | accuracy | 95% CI |
|---|---|---|---|
| clean | 4 | 0.750 | [0.301, 0.954] |
| clutter | 2 | 1.000 | [0.342, 1.000] |
| low_light | 13 | 0.231 | [0.082, 0.503] |
| motion_blur | 1 | 1.000 | [0.207, 1.000] |
| occlusion | 2 | 0.000 | [0.000, 0.658] |
| odd_angle | 22 | 0.591 | [0.387, 0.767] |
| reflection | 14 | 0.357 | [0.163, 0.612] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 0.875 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.385 |
