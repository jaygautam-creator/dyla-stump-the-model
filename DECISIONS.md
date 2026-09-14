# DECISIONS

> Draft outline (max two pages). Filled in from `docs/DECISION_LOG.md`
> and `eval/report.md` once results exist.

## Catalogue: what and why
<!-- Brand/source, size, why jewellery (Dyla's domain), SKU vs design groups. -->

## Architecture chosen
<!-- Two-stage retrieval: localise → embed → FAISS → verify → calibrated decide. One line of why per stage. -->

## What I rejected (with evidence)
<!-- Whole-image embedding vs crop (numbers). CLIP vs DINOv2 (numbers). Cosine threshold refusal vs calibrated verification (FAR/FRR). -->

## Evaluation methodology and why
<!-- Paired clean/hard design, split by item, frozen test set, SKU vs design accuracy, Wilson CIs, confounding. -->

## Results
<!-- Clean vs hard gap; per-condition table; which conditions hurt most and why; refusal FAR/FRR; latency per stage. -->

## Trade-offs under the time limit

## Where it breaks
<!-- Named weaknesses, found by us, with evidence. -->

## Next two weeks
