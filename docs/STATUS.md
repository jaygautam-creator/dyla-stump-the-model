# Status

**Last updated:** 2026-09-14
**Current phase:** Phase 1, 3, and 4's harness done. Phase 2 (stumper set) redefined: no purchase, no store
visit, no refusal extension — using 3 home items instead (see `docs/SHOT_LIST.md`, rewritten). Tooling for
it is ready (`own_items.py`); the shoot itself is still mine to do.

## Next step

Mine: take one clean reference photo of each of 3 home items (gold ring, gold chain, gold kadda), register
each with `python -m dyla_match.catalogue.own_items`, rebuild both indexes, then shoot ~34 hard-condition
photos per item (~102 total) per `docs/SHOT_LIST.md` and log into `data/stumper/labels.csv` as I go. Once
that exists: run `harness.py` for real and write the first `report.md`.

## Decisions (settled — see `DECISION_LOG.md` for full reasoning)

| # | Decision | Choice |
|---|---|---|
| D1 | Brand and photo access | Superseded 2026-09-14 — zero-budget: 3 home items self-added as catalogue entries, no purchase, no store visit |
| D2 | Time available | Full 12–15 h budget, no scope cut for now |
| D3 | Extension and approach | Refusal — dropped 2026-09-14 (no zero-cost negatives once D1 changed); two-stage retrieval pipeline in `PLAN.md` stands |
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
- [x] Shot list rewritten for 3 zero-cost home items — `docs/SHOT_LIST.md`
- [x] `own_items.py` built and tested — registers a self-sourced item as a catalogue entry
- [ ] Clean reference photo + registration for each of the 3 items, then rebuild both indexes
- [ ] ~102 positive photos (no negatives — refusal dropped)
- [ ] WhatsApp-recompressed and screenshot variants
- [ ] `labels.csv` complete (no calib/test split — n=3 is too small to mean anything), frozen

### Phase 3: baseline matcher
- [x] Environment (uv), config, DINOv2 + CLIP embeddings, FAISS index, CLI, per-stage timing

### Phase 4: harness
- [x] Metrics module (`eval/metrics.py`): top-k accuracy, Wilson CI, FAR/FRR (+ curve), ECE — verified
      against hand-computed reference values, not run on real data yet
- [x] `harness.py`: labels.csv -> matcher -> metrics -> report.md, incl. per-condition accuracy and
      paired drop. Wiring verified with catalogue images standing in for photos (never written to
      `data/stumper/`) — this proves the pipeline runs, not that the matcher works on real hard photos.
      ECE deliberately left out until `calibrate.py` (Phase 5) exists — reporting raw cosine score as a
      calibrated probability would be measuring something that isn't there yet.
- [ ] Run for real once Phase 2's photos exist; `eval/report.md` generated from that, not faked

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
  caught it, not the formula).
- 2026-09-14: Wrote `eval/harness.py` (labels.csv -> matcher -> metrics -> report.md), still ahead of Phase
  2's real photos. Verified the wiring using real catalogue images relabelled as if they were photos —
  deliberately not written into `data/stumper/`, to keep that path clean for the real frozen test set.
  Confirmed self-consistent: matcher trivially self-retrieves catalogue images at 100% top-1, report.md
  renders correctly. Left ECE out for now — no calibrated confidence exists until Phase 5's `calibrate.py`,
  and reporting raw cosine score as if it were a probability would be measuring something that isn't real.
  Everything left in Phase 4/5 needs actual stumper photos to be worth building further; that's still the
  next step, mine to do.
- 2026-09-14: Overruled my own D1/D3 after pushing back twice on the ₹12,400 purchase — no budget for it.
  Real zero-cost pieces exist at home (gold ring, chain, kadda) but with no receipt or known brand, so they
  can't be matched against a scraped catalogue. Rather than fake the "genuinely in your catalogue"
  requirement (using catalogue images or other people's photos as stand-ins — considered and rejected: it's
  detectable, defeats the point of the exercise, and is exactly what the brief's grading criteria call out),
  the fix is to add these 3 items as catalogue entries themselves (self-sourced, disclosed as such, not
  passed off as scraped). Built and tested `own_items.py` for this. Refusal extension dropped — it needed
  ~20 genuine negatives and there's nothing left at zero cost to serve as one. `docs/SHOT_LIST.md` and
  `docs/PLAN.md` rewritten accordingly. Submission now covers the brief's core only, no "take it further"
  piece — named openly rather than gestured at.
