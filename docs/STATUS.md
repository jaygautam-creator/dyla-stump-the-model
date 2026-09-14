# Status

**Last updated:** 2026-09-14
**Current phase:** Phase 4 has a real first result. Kadda turned out to be from a real brand (Swashaa,
verified exact SKU) — genuinely catalogue-matched, not self-sourced. Chain and ring are self-sourced. 58 of
the ~100+ required stumper photos shot and labelled; **still short of the brief's 100-photo minimum.**

## Next step

Mine: get to 100+ photos — easiest path is screenshotting ~42 of the existing 58 photos as displayed on
screen (creates genuine `<condition>;screenshot` combined-condition rows without new live shooting), send
them over, and I'll add them to `labels.csv` and rerun the harness. Also worth doing: spot-check my
condition-tag guesses in `data/stumper/labels.csv` (marked with a note — I inferred them from the photos,
not from what was actually intended) and correct any that are wrong.

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
- [x] Kadda identified as a real Swashaa product ("Ethan Men's Kada", id 7557947424992) — scraped Swashaa
      (300 products + this exact one), genuinely catalogue-verified, not self-sourced
- [x] Chain and ring registered self-sourced; both indexes rebuilt over all 7,272 images
- [x] 58 photos shot and labelled (17 chain, 28 ring, 13 kadda) — **short of the 100+ minimum**
- [ ] ~42 more photos (screenshot duplicates of existing shots is the fastest path)
- [ ] Spot-check Claude's condition-tag guesses in `labels.csv` against actual shooting intent
- [ ] No calib/test split (n=3 items, too small to mean anything) — all `test`, frozen once complete

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
- [x] Ran for real on the 58 photos so far — `eval/report.md` (DINOv2) and `eval/report_clip.md` (CLIP).
      Provisional (n=58, not yet the full 100+, no calib/test split): DINOv2 top-1 SKU 46.6% [34.3, 59.2],
      CLIP top-1 SKU 75.9% [63.5, 85.0] — CLIP clearly ahead here, the opposite of `PLAN.md`'s expectation
      that DINOv2 would win at exact-instance retrieval. Real result, not assumed; needs the full photo set
      before trusting the gap's size. Worst conditions: `occlusion` (0% DINOv2, 50% CLIP, n=2) and
      `low_light` (23.1% DINOv2, 76.9% CLIP, n=13). Diagnosed one concrete failure: the kadda's own clean
      photo doesn't rank in the top 30 for *either* backbone against Swashaa's real studio photo — the
      correct product isn't even close on raw cosine similarity, consistent with `PLAN.md`'s predicted
      whole-image weakness (small object, background dominates) before cropping exists.
- [ ] Re-run once 100+ photos and corrected condition tags are in; revisit backbone choice with real n

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
- 2026-09-14: Took 58 photos (chain, ring, kadda) and handed them over. Spotted "SWASHAA" stamped inside
  the kadda in one photo — a real online brand (swashaa.com, same Shopify-feed setup as Giva/Palmonas).
  Found the exact matching SKU myself ("Ethan Men's Kada") after Claude's own reverse-image search through
  Swashaa's catalogue came up empty. Scraped Swashaa (300 products + this specific one) so it's a genuine
  catalogue match, not self-sourced like the other two. Claude classified all 58 photos by item and guessed
  condition tags by eye (flagged in `labels.csv` as a guess, not stated intent — still need to check these).
  Ran the harness for real for the first time: DINOv2 46.6% / CLIP 75.9% top-1 SKU accuracy (n=58, provisional).
  Still short of the brief's 100-photo minimum — next is getting to 100+, easiest via screenshotting existing
  photos rather than shooting more live ones.
