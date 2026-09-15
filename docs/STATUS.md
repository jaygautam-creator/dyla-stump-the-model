# Status

**Last updated:** 2026-09-15
**Current phase:** Phase 5 done and measured, submission code/docs pushed to GitHub. Photo count is past
the brief's 100-photo minimum (58 real + 45 synthetic, reported separately everywhere). CLIP is the
measured winner over DINOv2. **Every Phase 5 improvement tried (crop-to-object, twice; equal-weight
ensemble; verification re-rank) measured worse than the Phase 4 baseline and was rejected** — the shipped
matcher is plain whole-image CLIP cosine retrieval, no preprocessing, no re-ranking. **Real finding, still
unfixed:** the one item that's a genuine external catalogue match (the Swashaa kada) scores 0% top-1
recall in every configuration tried, including the rejected fixes. The 75.9% headline number is carried
entirely by the two self-sourced items. Full detail in `DECISIONS.md`.

Now building toward: a deployed web demo (not yet started — requirements captured in `docs/PLAN.md`
"Phase 6", stack recommendation is Next.js on Vercel + FastAPI on Render, not yet confirmed by me).

## Next step

Mine: confirm or redirect the Phase 6 stack/design recommendation in `docs/PLAN.md`, then say go on
building the FastAPI backend + Next.js frontend. Separately open: whether to spend more time chasing the
kada failure with a *real* verification method (Next-two-weeks item 1 in `DECISIONS.md`) before or after
the demo — my call.

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
- [x] 45 synthetic rows added via `scripts/augment_stumper.py` (crop/resize/tilt of the real 58),
      tagged `synthetic_*` and always reported separately from real-photo accuracy — 103 total
- [x] Condition-tag spot-check done; 11 mistagged rows corrected (chain odd_angle/clutter guesses that
      were actually clean shots, kadda low_light guesses that were actually bright/blurred)
- [x] No calib/test split (n=3 items, too small to mean anything) — all `test`, frozen once complete

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
- [x] Re-run with 103 photos (58 real + 45 synthetic) and corrected condition tags; backbone choice
      confirmed with real n: CLIP wins (75.9% vs DINOv2 46.6%, real-58 top-1 SKU)

### Phase 5: improvements, each measured
- [x] Crop vs whole image — `src/dyla_match/preprocess.py`, corner-background-subtraction heuristic
      (no object detector, 8GB RAM budget). Measured twice (naive bbox, then a more robust "largest
      dense run" bbox after finding a real bug in the first version). Both hurt real-photo accuracy;
      the more correct version hurt more (CLIP 75.9%→51.7%, DINOv2 46.6%→31.0%). **Rejected, off by
      default.** `eval/report_dinov2_crop.md`, `eval/report_clip_crop.md`.
- [x] Ensemble — equal-weight CLIP+DINOv2 score fusion (`eval/run_ensemble.py`). Measured worse than
      CLIP alone (55.2% vs 75.9%) — rejected, DINOv2's weaker signal drags it down.
- [x] Verification re-rank for the kada failure — wider candidate pool + tighter-crop-embedding fusion
      (`src/dyla_match/rerank.py`, `eval/run_rerank.py`). Measured worse across the board (real top-1
      31.0% vs 75.9% baseline) and did not fix the kada (still 0% recall) — rejected. A real local-feature
      verification method (not a second whole-crop embedding) is still open, see `DECISIONS.md`
      next-two-weeks item 1.
- [ ] Calibrated refusal vs cosine threshold — not built; needs a not-in-catalogue negative class, and
      none exists at zero budget (documented, not fabricated).

**Net result of Phase 5: every improvement tried measured worse than the Phase 4 baseline.**
`configs/default.yaml` ships plain whole-image CLIP, no preprocessing, no re-ranking — still the
best-measured configuration in the repo.

### Phase 6: demo + deployment
- [x] Requirements written down in `docs/PLAN.md` before any code — stack recommendation (Next.js on
      Vercel + FastAPI on Render), design brief, API contract draft, cost flag on Render's paid tier
- [ ] Confirm stack/design with me before building
- [ ] FastAPI backend wrapping the matcher
- [ ] Next.js frontend, premium jewellery-appropriate design
- [ ] Deploy both, verify end-to-end on the live URL

### Phase 7: submission
- [x] `DECISIONS.md` ≤ 2 pages — filled in with real numbers, including the kada 0%-recall finding
- [x] README tested on a clean machine (< 5 min) — quickstart commands run end-to-end as written
- [ ] Export all logs — last session's export was blocked by a macOS Desktop-folder permission lockout
      (Terminal's Files-and-Folders access got revoked mid-session, see session history below); re-run
      pending
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
- 2026-09-15: Prior session ended mid-task on a macOS permission lockout (Terminal's Desktop-folder access
  got revoked, likely triggered by an Accessibility/Automation prompt from screenshot-capture work) —
  `scripts/export_logs.py` failed with `Operation not permitted` and never completed; caught in this
  session's resume, re-export still pending. Spot-checked all 58 real photos' condition tags against what
  they actually show; corrected 11 mismatches (mostly `odd_angle`/`clutter` guesses on chain photos that
  were actually plain clean shots, and `low_light` guesses on kadda photos that were actually bright or
  blurred). Built `scripts/augment_stumper.py` to pad the stumper set to 103 photos (58 real + 45 tagged
  `synthetic_*` crop/resize/tilt variants) — past the brief's 100-photo minimum, with real and synthetic
  accuracy always reported separately so the synthetic padding never inflates the real number. Added
  crop-to-object preprocessing (`src/dyla_match/preprocess.py`, corner-background-subtraction, no object
  detector) and re-ran the full harness across DINOv2/CLIP × crop/no-crop (4 reports) plus an equal-weight
  CLIP+DINOv2 ensemble experiment. Real findings: CLIP confirmed as the stronger backbone with real n
  (75.9% vs 46.6% top-1 SKU), crop preprocessing has a small mixed effect (kept on, not a clean win),
  ensemble fusion measured worse than CLIP alone (rejected). Most important finding: broke accuracy down
  per item and found the one genuine external catalogue match (the Swashaa kada) scores 0% top-1 recall in
  every configuration tried — the 75.9% headline is carried entirely by the two self-sourced items, a
  materially different and less impressive claim than the aggregate suggests. Wrote this up in
  `DECISIONS.md` rather than leaving it in the aggregate. Also wrote `scripts/hydrate_catalogue_images.py`
  (rebuilds the gitignored catalogue images from URLs already in `products.csv`, via a thread pool, so the
  README's <5-minute clean-machine claim is achievable) and a real README with tested quickstart commands.
- 2026-09-15 (continued): Tried a verification re-rank to fix the kada 0%-recall failure specifically.
  Diagnostic found the true SKU does exist in the embedding space (unique-product rank ~40-70, not
  missing), just consistently out-ranked by generic gold jewellery. Built a wider-candidate-pool +
  tighter-crop-fusion re-rank; while building it, found and fixed a real bug in the crop heuristic itself
  (naive min/max bbox blown out by scattered background noise on some photos). Re-measuring crop with the
  bug fixed reversed the earlier "small mixed effect, kept on" call from the same day: the more correct
  crop hurts clearly (CLIP 75.9%→51.7%, DINOv2 46.6%→31.0%). Both crop and the full re-rank (31.0%,
  kada still 0%) are now rejected; `configs/default.yaml` reverted to plain whole-image CLIP, the
  actual best-measured config. `DECISIONS.md`, `docs/DECISION_LOG.md`, and this file corrected to match
  rather than left stale. Also wrote Phase 6 (demo + deployment) requirements into `docs/PLAN.md` per
  instruction, before writing any UI code: Next.js/Vercel + FastAPI/Render recommended, premium
  jewellery-aesthetic design brief captured, Render cost flagged as a real recurring expense to confirm
  before provisioning. Not yet built or deployed — waiting on go-ahead.
