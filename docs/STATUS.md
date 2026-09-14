# Status

**Last updated:** 2026-09-14
**Current phase:** Phase 1 and Phase 3 done. Phase 4's metrics module written and self-checked (no real data
yet). Phase 2 (stumper set) still needs the physical purchase/shoot, which only I can do — everything else
is blocked on it.

## Next step

Mine: buy the 6 items in `docs/SHOT_LIST.md` (~₹12,400), do the store visit for negatives, shoot and label.
Once photos exist: `harness.py` (wire labels.csv + matcher output into `eval/metrics.py`) and the first
`report.md` — measuring DINOv2 vs CLIP on the real stumper set rather than eyeballing self-retrieval.

## Decisions (settled — see `DECISION_LOG.md` for full reasoning)

| # | Decision | Choice |
|---|---|---|
| D1 | Brand and photo access | Mix: buy a handful of Giva/Palmonas pieces for controlled paired shots + a store visit (CaratLane/Tanishq/BlueStone) for more items and lookalike negatives |
| D2 | Time available | Full 12–15 h budget, no scope cut for now |
| D3 | Extension and approach | Refusal, with the two-stage retrieval pipeline in `PLAN.md` |
| D4 | Interface | CLI only for the core; small demo only if time remains |

## Checklist

### Phase 0: understand and plan
- [x] Read the brief, pick Problem 2
- [x] Research Thuli Studios / Dyla → `PROJECT_BRIEF.md`
- [x] Sector: jewellery
- [x] Plan: solution, going beyond the brief, refusal, architecture → `PLAN.md`
- [x] Project notes, log export script, repo
- [x] Settle D1–D4

### Phase 1: catalogue
- [x] Check source can be scraped (robots.txt, terms) — Giva & Palmonas confirmed: public `/products.json` feed
- [x] Giva scraped: 2,294 images (400 products)
- [x] Palmonas topped up: 4,056 images (607 products) — cleared the 5,000-image target
- [x] Design groups for near-duplicate listings — `groups.py`, text-based (strips colour/plating/size
      tokens from titles, groups by vendor+product_type+normalised title). 1,007 products → 999 design
      groups, 8 groups merge a true colour variant (checked by hand). `design_group` column added to
      `products.csv`.

### Phase 2: stumper set
- [x] Shot list: items, conditions, clean pairs — `docs/SHOT_LIST.md`
- [ ] Buy the 6 items, do the store visit for negatives
- [ ] 100+ positive photos, ~20 lookalike negatives
- [ ] WhatsApp-recompressed and screenshot variants
- [ ] `labels.csv` complete, calib/test split by item, frozen

### Phase 3: baseline matcher
- [x] Environment (uv), config, DINOv2 + CLIP embeddings, FAISS index, CLI, per-stage timing

### Phase 4: harness
- [x] Metrics module (`eval/metrics.py`): top-k accuracy, Wilson CI, FAR/FRR (+ curve), ECE — verified
      against hand-computed reference values, not run on real data yet
- [ ] Paired drop, `harness.py` wiring labels.csv + matcher output to these metrics, `report.md`

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
- 2026-09-14: Settled D1–D4 (mix of Giva/Palmonas purchase + store visit; full time budget; refusal; CLI).
  Verified Giva and Palmonas both expose a public Shopify `/products.json` feed; CaratLane/Tanishq/BlueStone
  allow crawling via sitemaps. Starting Phase 1 scraper.
- 2026-09-14: Confirmed the Palmonas topped-up scrape is intact (no live permission/blocking issue on either
  feed — checked 15+ pages of `/products.json` on both shops, all 200s). Catalogue stands at 6,350 images,
  1,007 products (400 Giva, 607 Palmonas), past the 5,000 target. Wrote `groups.py` to assign `design_group`
  per listing from the title (strips colour/plating/size words, groups by vendor+product_type+normalised
  title) — no embeddings pipeline exists yet to do this by image. 999 design groups, 8 correctly merge a
  colour variant; spot-checked by hand. Phase 1 catalogue work is done; next is planning the store visit.
- 2026-09-14: Planned Phase 2 in `docs/SHOT_LIST.md`. Picked 6 concrete catalogue items to buy (~₹12,400,
  ring/earrings/necklace × Giva/Palmonas) after I chose the 6-item budget tier over an 8-item one Claude also
  offered. Reworked D1's store-visit purpose: it's for lookalike negatives only (CaratLane/Tanishq/BlueStone
  aren't in the catalogue, so nothing there can be a positive) — corrected from the original "more items +
  negatives" framing. Wrote the per-item shot list (live hard-condition shots + WhatsApp/screenshot
  processed duplicates to hit combined-condition photos without extra staging) and a calib/test split by
  item. Nothing bought or shot yet — that's the next physical step.
- 2026-09-14: Built Phase 3 (baseline matcher) while Phase 2's physical steps are still pending — the plan
  already allows the two phases to overlap once the catalogue exists. `uv`-managed `.venv`; added torch,
  torchvision, faiss-cpu, transformers, pyyaml to the `ml` extra. Wrote `configs/default.yaml`,
  `embed.py` (DINOv2 + CLIP via `transformers`, L2-normalised), `index.py` (FAISS flat IP, image→product
  max-score aggregation), `matcher.py` (photo → top-5 + per-stage timing), `cli.py` (`build-index`, `match`).
  Two real bugs, both fixed: (1) faiss-cpu and torch each bundle their own OpenMP runtime, which aborts the
  process on macOS unless `KMP_DUPLICATE_LIB_OK=TRUE` is set before either is imported — documented in
  `cli.py`, not a silent workaround. (2) this environment's `transformers` (5.17.0) changed
  `CLIPModel.get_image_features` to return a `BaseModelOutputWithPooling` instead of a bare tensor — fixed
  by reading `.pooler_output`. Built both indexes over the full 6,350-image catalogue (DINOv2 ~69s, CLIP
  ~56s on the M2's MPS backend). Sanity check only so far: matching a catalogue image against its own index
  retrieves itself top-1 at score 1.0 for both backbones — real accuracy numbers need the stumper photos
  (Phase 4), not this.
- 2026-09-14: Wrote `eval/metrics.py` (top-k accuracy, Wilson CI, FAR/FRR + curve, ECE with reliability
  bins) while still waiting on the physical Phase 2 steps — pure functions, no dependency on real stumper
  data. Checked against hand-computed reference values (e.g. Wilson CI for n=100,k=80 against a worked-by-hand
  calculation, not a misremembered one — my first guess at the reference numbers was wrong and the check
  caught it, not the formula). `harness.py` (wiring labels.csv + matcher output into these) still needs real
  photos to be worth writing.
