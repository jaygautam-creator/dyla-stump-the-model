# Status

**Last updated:** 2026-09-14
**Current phase:** planning done, starting phase 1 once the open decisions below are settled.

## Next step

Settle D1–D4. Then check that the chosen brand's catalogue can be scraped (robots.txt, terms, product feed)
and set up the repo layout from `PLAN.md`.

## Open decisions

| # | Decision | Options | Leaning |
|---|---|---|---|
| D1 | Brand and photo access | A) store visit (CaratLane / Tanishq / BlueStone) · B) buy 5–10 inexpensive pieces (Giva / Palmonas / Salty; check whether they expose a public product feed) · C) pieces friends or family own from a brand with an online catalogue | Mix of B and A: owned pieces for controlled shots, store for more items and lookalikes |
| D2 | Time available | Full 12–15 h over 5–7 days, or cut scope | — |
| D3 | Extension and approach | Refusal as the one extension; two-stage retrieval as in PLAN.md | Refusal |
| D4 | Interface | CLI only · CLI + small Gradio demo | CLI first |

## Checklist

### Phase 0: understand and plan
- [x] Read the brief, pick Problem 2
- [x] Research Thuli Studios / Dyla → `PROJECT_BRIEF.md`
- [x] Sector: jewellery
- [x] Plan: solution, going beyond the brief, refusal, architecture → `PLAN.md`
- [x] Project notes, log export script, repo
- [ ] Settle D1–D4

### Phase 1: catalogue
- [ ] Check source can be scraped (robots.txt, terms)
- [ ] Scraper → 5,000+ images, `products.csv` with source URLs
- [ ] Design groups for near-duplicate listings

### Phase 2: stumper set
- [ ] Shot list: items, conditions, clean pairs
- [ ] 100+ positive photos, ~20 lookalike negatives
- [ ] WhatsApp-recompressed and screenshot variants
- [ ] `labels.csv` complete, calib/test split by item, frozen

### Phase 3: baseline matcher
- [ ] Environment (uv), config, DINOv2 + CLIP embeddings, FAISS index, CLI, per-stage timing

### Phase 4: harness
- [ ] Metrics (SKU/design top-1/5, Wilson CI, paired drop, FAR/FRR, ECE), `report.md`

### Phase 5: improvements, each measured
- [ ] Crop vs whole image
- [ ] Verification re-rank
- [ ] Calibrated refusal vs cosine threshold

### Phase 6: submission
- [ ] `DECISIONS.md` ≤ 2 pages
- [ ] README tested on a clean machine (< 5 min)
- [ ] Export all logs
- [ ] Share the private repo, email careers@thuli.studio

## Session history

- 2026-09-14: Read the brief, picked Problem 2, researched Dyla, chose jewellery, wrote the plan and project
  notes. No code yet; I wanted the problem and approach clear first.
