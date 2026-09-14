# Evaluation report

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
| clean | 4 | 0.750 | [0.301, 0.954] |
| clutter | 2 | 1.000 | [0.342, 1.000] |
| low_light | 13 | 0.769 | [0.497, 0.918] |
| motion_blur | 1 | 1.000 | [0.207, 1.000] |
| occlusion | 2 | 0.500 | [0.095, 0.905] |
| odd_angle | 22 | 0.818 | [0.615, 0.927] |
| reflection | 14 | 0.643 | [0.388, 0.837] |

## Paired drop (hard vs this item's own clean photo)

| pair_id | clean hit | hard hit rate |
|---|---|---|
| chain_pair | True | 1.000 |
| kadda_pair | False | 0.000 |
| ring_pair | True | 0.962 |
