# Decision log

Every decision, in order, with the reasoning. This feeds `DECISIONS.md` at the end. Where an idea came from
Claude and I accepted or changed it, I note that.

Format:
```
## YYYY-MM-DD: title
- Source: mine | suggested by Claude, accepted | suggested by Claude, changed | overruled Claude
- Options:
- Choice:
- Why / evidence:
- Revisit if:
```

---

## 2026-09-14: Problem 2
- Source: mine
- Options: P1 Ticket Stampede (backend), P2 Stump the Model (ML/CV), P3 Analyst and Auditor (agents)
- Choice: Problem 2
- Why: ML and computer vision is where I want to be evaluated.

## 2026-09-14: Understand before building
- Source: mine
- Choice: No code until the company, the problem, the approach, what goes beyond the brief, and the reasons are
  written down.
- Why: I have to explain and change every part of this in the follow-up call. Building first and understanding
  later would show.

## 2026-09-14: Jewellery as the category
- Source: mine. Claude's first suggestion was footwear, eyewear or watches based on what I could photograph; I
  asked it to research the company first, and that pointed to jewellery.
- Choice: Jewellery
- Why: Dyla is AI for Indian jewellery retail. The brief's hard conditions (reflections, hand or wrist in frame,
  small objects) are everyday conditions for jewellery.

## 2026-09-14: Plan beyond the core requirements
- Source: mine
- Choice: Plan what goes beyond the brief (PLAN.md) at the same time as the core, instead of adding it at the end.
- Why: The brief says a submission that only meets the requirements is a no.

## 2026-09-14: Refusal as the extension
- Source: suggested by Claude, accepted
- Options: refusal · 100k scale · multi-item · incremental add · automated stumper
- Why: Hardest of the five by the brief's own description, and the most relevant to a retailer: a wrong
  "we have this" loses trust.

## 2026-09-14: Brand and photo access (D1)
- Source: mine
- Options: buy Giva/Palmonas pieces · store visit (CaratLane/Tanishq/BlueStone) · mix of both · family/friends' pieces
- Choice: Mix of both — buy a handful of Giva or Palmonas pieces for fully controlled paired shots, plus a
  store visit for more items and for lookalike negatives.
- Why / evidence: Checked robots.txt and product feeds before deciding. Giva and Palmonas are both Shopify
  storefronts with a public `/products.json` feed (verified: returns full title, images, variants) — easiest
  catalogue to build cleanly. CaratLane, Tanishq and BlueStone all publish product/image sitemaps and allow
  crawling product pages (checked robots.txt), so a store visit adds reach without blocking the scrape.
- Revisit if: store visit isn't possible (staff refuse photography) — fall back to owned pieces only, and
  source lookalike negatives from a different online-only brand instead.

## 2026-09-14: Scraper bug caught on first real run
- Source: mine, found while running the Giva scrape
- What happened: `scrape.py` opened `products.csv` in append mode without creating its parent directory
  first (only `download_and_resize` created `images/`, lazily, per file). The script fetched the entire
  5,657-product listing (23 paginated requests, ~25s) and only then crashed with `FileNotFoundError` on
  the first CSV write, throwing away that work.
- Fix: create `out_dir` up front in `main()`, before opening the CSV.
- Why it matters: this is the kind of bug a quick 3-product smoke test doesn't catch (the smoke test ran
  first and passed, because logic executed in file order happened to work then too, actually — recheck:
  the smoke test DID create `data/catalogue/images/` and the CSV successfully; the bug only appeared on
  the real run after `rm -rf data/catalogue`, which removed the directory the smoke test had implicitly
  created). Lesson: re-verify after clearing state, don't assume a passing smoke test covers a fresh run.
- Revisit if: n/a — fixed and re-run cleanly (2,294 images, 0 errors, exit code 0).

## 2026-09-14: Time budget (D2) and interface (D4)
- Source: mine, accepting Claude's recommendation on D4
- D2 choice: full 12-15 hour budget across the week, no scope cut for now.
- D4 choice: CLI only for the core; revisit a small demo only if time remains at the end.

## 2026-09-14: Design grouping method — text, not embeddings
- Source: suggested by Claude, accepted
- Options: text-based normalisation of the title (strip colour/plating/size words, group by
  vendor+product_type+normalised title) · defer grouping until the embedding pipeline (Phase 3) exists and
  cluster by image similarity instead.
- Choice: text-based now, in `groups.py`.
- Why: the embedding pipeline doesn't exist yet (Phase 3), and the catalogue titles are structured enough
  (colour/plating/size are named tokens, not free text) to group reliably without it. Verified: grouping
  with vs without the product_type constraint gave the identical 8 multi-SKU groups, and all 8 were checked
  by hand to be true colour variants of the same design (not different designs).
- Revisit if: a future catalogue's titles aren't as structured, or once embeddings exist — re-grouping by
  image similarity would catch variants that don't share a title (different SKU naming) and could replace
  the text heuristic. Not needed for the current 1,007-product catalogue.

## 2026-09-14: Phase 2 purchase budget (6 items, not 8)
- Source: mine, choosing between two options Claude offered
- Options: 8 items ~₹15,800 (adds bracelet + anklet coverage) · 6 items ~₹11,000 (recommended: ring/earrings/
  necklace × Giva/Palmonas, hit 100+ photos via WhatsApp/screenshot processed duplicates instead of more
  items) · a different number/budget.
- Choice: 6 items. Actual total came to ~₹12,377 once specific pieces were picked (a couple of designs
  priced above their category median).
- Why: lower spend, and 100+ labelled photos is still reachable without buying more — processing existing
  live shots through WhatsApp/screenshot gives extra combined-condition rows for free.
- Trade-off accepted: no bracelet or anklet in the owned positive set — category coverage is rings, earrings,
  necklaces only. Named as a stumper-set limitation, to go in `DECISIONS.md`.

## 2026-09-14: Store visit is for negatives only, not more positives
- Source: suggested by Claude (correction to D1), accepted
- What changed: D1 originally described the store visit as "more items + negatives." On planning the actual
  shot list, that doesn't hold up: CaratLane/Tanishq/BlueStone pieces aren't in the Giva/Palmonas catalogue,
  so anything photographed there is by definition not-in-catalogue — a negative, never a positive.
- Choice: store visit produces ~20 lookalike-negative photos only, from ~12–15 pieces mirroring the
  purchased categories (rings, earrings, necklaces).
- Revisit if: staff refuse photography — fall back to a different online-only brand's catalogue images as
  the negative source (already noted as D1's fallback).

## 2026-09-14: D1 superseded — zero-budget stumper set, refusal extension dropped
- Source: mine, overruling my own earlier D1 (buy + store visit) after I pushed back twice on cost;
  Claude's proposed alternatives (buy fewer items, buy-and-return, borrow) were all declined.
- What changed: no purchase at all. 3 home pieces (gold ring, gold chain, gold kadda) — no receipts, no
  known brand, no way to verify them against a scraped catalogue — become the entire stumper set instead.
- Choice: add these 3 pieces as new catalogue entries themselves, self-sourced rather than scraped (one
  clean reference photo each, taken by me, standing in for what a scraped studio photo would be). The
  6,350-image Giva/Palmonas scrape is untouched and still satisfies the "5,000+ scraped images" requirement
  on its own; these 3 items sit on top of it as additional, undeniably-genuine SKUs. Disclosed as self-sourced
  in `DECISIONS.md`, not passed off as scraped.
- Refusal extension (the earlier D3) is dropped: it needs ~20 items genuinely not in the catalogue, and
  there's nothing left at zero cost to serve as negatives (the 3 home pieces are now positives). Falling
  back to the brief's core (matcher + stumper, no "take it further") rather than a half-built refusal with
  no negatives to test it against.
- Trade-off accepted, named openly: only 3 positive items (vs. the original 6), no category diversity beyond
  ring/chain/kadda, no refusal/false-accept-rate result. Whether to pick a different, zero-cost "take it
  further" extension (e.g. scaling the catalogue further, or automating hard-case generation) is still open —
  my call to make once the core is running on real numbers.
- Revisit if: a zero-cost source of genuine negatives turns up later (e.g. more home jewellery not used as
  positives) — refusal could still be added back.

## 2026-09-14: Kadda is a real Swashaa product, not self-sourced
- Source: mine — noticed "SWASHAA" stamped inside the kadda and gave Claude the exact product URL after
  its own attempt to find the SKU by eyeballing ~100 Swashaa product photos came up empty.
- Choice: scraped Swashaa (swashaa.com, same public Shopify `/products.json` setup as Giva/Palmonas) — 300
  products for general catalogue depth plus this one specific product by URL handle, since it happened to
  sit near the end of Swashaa's 1,816-product listing and a small `--limit-products` cap wouldn't reach it.
- Why it matters: the kadda is now a genuinely catalogue-verified positive, not a self-sourced item like
  the chain and ring — a stronger result than planned, and worth calling out in `DECISIONS.md` as something
  that improved past the original zero-budget fallback.
- Bug caught while doing this: `scrape.py` appended new rows without the `design_group` column that
  `groups.py` had already added to `products.csv`, silently corrupting row shape (12 fields instead of 13)
  for all newly-scraped rows. Fixed by making the writer detect and match the existing file's header;
  cleaned up and re-scraped. Also added a retry to `download_and_resize` after a `ReadTimeout` crashed the
  first Swashaa scrape partway through.

## 2026-09-14: First real evaluation — CLIP beats DINOv2 here, against the plan's expectation
- Source: measured, not assumed
- What happened: ran `harness.py` for real on the 58 photos shot so far (not yet the full 100+, no
  calib/test split yet). DINOv2 top-1 SKU accuracy 46.6% [34.3, 59.2] vs CLIP 75.9% [63.5, 85.0]. `PLAN.md`
  expected the opposite — DINOv2 favoured for exact-instance retrieval, CLIP expected weaker at "this exact
  necklace" vs "a gold necklace" in general.
- Caveat, stated plainly: n=58 across only 3 items, no calibration split — wide CIs, could easily be
  idiosyncratic to these specific 3 items rather than a general result. Not treating this as settled;
  re-measuring once the photo set reaches 100+ before it goes in `DECISIONS.md` as a real finding.
- Diagnosed one concrete failure along the way: the kadda's own "clean" phone photo doesn't rank in the
  top 30 of either backbone against Swashaa's real studio photo of the same product — consistent with
  `PLAN.md`'s predicted whole-image weakness (small object, background dominates) ahead of any cropping.

## 2026-09-15: Condition-tag spot-check corrections
- Source: mine (asked Claude to spot-check its own visual-read guesses from 2026-09-14)
- Options: trust the guessed tags as-is, or re-inspect every photo against what it actually shows
- Choice: re-inspected all 58 real photos; corrected 11 mismatches (`chain_01/03/05/07/08/11/16`,
  `kadda_01/02/03/04`) — mostly `odd_angle`/`clutter` guesses on chain photos that were actually plain
  clean shots, and `low_light` guesses on kadda photos that were actually bright or out of focus
- Why / evidence: per-photo visual re-inspection, documented in the conversation this decision came from
- Revisit if: any other condition tags turn out wrong on closer inspection later

## 2026-09-15: Pad the stumper set with tagged synthetic augmentation, reported separately
- Source: mine ("duplicate them, resize them, crop them, tilt them" — explicit instruction) ; Claude
  proposed reporting synthetic and real accuracy separately rather than blending them silently, and
  applied that by default without asking further
- Options: (a) merge synthetic rows into the test set indistinguishably from real photos, (b) tag them
  and report real-vs-synthetic accuracy separately in every report
- Choice: (b). `scripts/augment_stumper.py` adds 45 crop/resize/rotate variants of the real 58 photos,
  tagged `synthetic_*`, bringing the set to 103 (past the brief's 100-photo minimum)
- Why / evidence: a synthetic near-duplicate of a photo the matcher has already seen (same lighting,
  background, physical instance) is not independent evidence the way a new real photo is — blending it
  into the headline number without saying so would overstate accuracy. `eval/harness.py`'s `run_real_eval`
  writes a "real phone photos only" section and a separate "blended" section in every report.
- Revisit if: more real phone photos become available and the synthetic padding is no longer needed to
  clear the 100-photo minimum

## 2026-09-15: CLIP + crop-to-object preprocessing as the default config; DINOv2+CLIP ensemble rejected
- Source: suggested by Claude (Phase 5 items from `docs/PLAN.md`), accepted
- Options: DINOv2 vs CLIP as default backbone; whole image vs crop-to-object preprocessing; single
  backbone vs equal-weight ensemble of both
- Choice: CLIP, with crop-to-object preprocessing on. Ensemble rejected.
- Why / evidence: CLIP confirmed the stronger backbone on the full real-58 photo set (75.9% vs 46.6%
  top-1 SKU, `eval/report_clip.md` vs `eval/report.md`). Crop-to-object (`src/dyla_match/preprocess.py`,
  corner-background-subtraction, no object detector — 8GB budget) has a small, mixed effect: doesn't move
  the aggregate number for either backbone but trades accuracy between items (e.g. DINOv2 chain recall
  88.2%→82.4%, ring recall 42.9%→46.4%); kept on since it's free and slightly positive on the blended set.
  Equal-weight CLIP+DINOv2 score fusion (weight fixed a priori, not tuned against stumper accuracy) scored
  55.2% real top-1 — worse than CLIP alone — because DINOv2's much weaker signal drags the average down.
- Revisit if: a real object detector or a proper verification re-rank stage gets built (Phase 5
  next-two-weeks item), which could change whether crop/ensemble still look this way.

## 2026-09-15: Named finding — the one genuine catalogue item (the kada) scores 0% top-1 recall
- Source: mine (asked Claude to push for "very very good" accuracy); Claude found and reported this
  rather than only reporting the aggregate number
- What happened: broke the 75.9% headline top-1 SKU accuracy down per item. The self-sourced gold chain
  (100%) and gold ring (96.4%) carry the whole number; the Swashaa kada — the only item that's a genuine
  external catalogue match, not self-sourced — scores 0% top-1 recall in every backbone/preprocessing
  combination tried, including the crop and ensemble variants. A representative failure: a clean kada
  photo scores 0.90 cosine against the *self-sourced gold ring*, a different item entirely, and the true
  Swashaa SKU doesn't appear in the top 5 at all.
- Why it matters: this is exactly the whole-image weakness `docs/PLAN.md` predicted before any stumper
  photo was taken (small, low-detail object, background dominates) — now confirmed as the matcher's real
  failure mode, not lighting/angle/occlusion as originally hypothesized. Named openly in `DECISIONS.md`
  rather than left inside the aggregate, per the "measure don't assume, name weaknesses openly" rule.
- Revisit if: a verification re-rank stage or more kada photos change this — currently open as
  next-two-weeks item 1 and 4 in `DECISIONS.md`.

## 2026-09-15: D4 (interface) superseded — full web demo + deployment now wanted
- Source: mine — explicit instruction to build a deployed web demo before final submission
- Previous choice (D4, 2026-09-14): CLI only for the core, small demo only if time remained
- New choice: build a full web demo (upload a photo, see top-5 matches) with a premium,
  jewellery-appropriate look, and deploy it publicly (platform TBD between Vercel/Render/Cloudflare —
  Claude to recommend, I decide). Requirements captured in `docs/PLAN.md` "Phase 6: demo + deployment"
  before any UI code is written, so nothing here is guessed at build time.
- Sequencing, my instruction: model accuracy work first (kada verification re-rank), demo requirements
  written down second, UI build and deploy last — in that order, not started until I say so for the
  later steps.
- Revisit if: the deployment cost/complexity turns out not worth it for a take-home submission — this
  is additional scope beyond the brief's minimum ask, done because I asked for it, not because the
  brief requires it.

## 2026-09-15: Verification re-rank tried for the kada failure — measured worse, rejected
- Source: mine ("try the kada verification re-rank fix")
- What was built: `src/dyla_match/rerank.py` — widen the first-stage candidate pool (unique products up
  to 75, informed by a diagnostic showing the kada's true SKU at unique-product rank 43 in one photo,
  disclosed as such), then re-embed a tighter crop of the query and each candidate's best image, fusing
  that second score with the original at a fixed a-priori 0.5/0.5 weight. Also fixed a real bug in
  `object_crop` along the way: a naive min/max bounding box over foreground pixels was blown out to
  nearly the full frame by scattered background noise (shadows/specks) on some photos; replaced with a
  1-D "largest contiguous dense run" per axis, which is what made the tighter query crop actually tight.
- Measured once against the full frozen stumper set (`eval/report_rerank.md`), not iterated further
  against the result: **top-1 SKU accuracy on real photos dropped from 75.9% (CLIP+crop) to 31.0%.** The
  kada still scores 0% recall — unfixed — while chain recall fell from 100% to 35.3% and ring from 96.4%
  to 42.9%.
- Why it failed: the tighter catalogue-image crop is noisy — spot-checked one candidate crop directly and
  it collapsed to a 41×306-pixel sliver, not a representative view of the item. A noisy second signal
  fused with a wider, noisier candidate pool made the ranking worse across the board, not just for the
  kada.
- Rejected. `configs/default.yaml` stays on CLIP + crop (no re-rank) — the config that actually measures
  best. `eval/run_rerank.py` and `src/dyla_match/rerank.py` are kept in the repo as a documented, honestly
  labelled failed experiment, not wired into the default matcher path.
- Revisit if: a more reliable tight-crop/verification signal is found — e.g. a real local-feature matcher
  instead of a second whole-crop embedding — this is exactly `docs/PLAN.md`'s original "verify" stage
  (SuperPoint/LightGlue or patch mutual-nearest-neighbours), which this simpler attempt was a cheaper
  stand-in for and evidently isn't a substitute for.

## 2026-09-15: Crop-to-object preprocessing rejected (corrects same-day earlier entry)
- Source: mine (asked to push accuracy further); found while building the verification re-rank
- What happened: fixing a real bug in `object_crop` (naive min/max bbox blown out by scattered
  background noise, replaced with a "largest dense run" per axis -- see the rerank entry above) changed
  what the crop preprocessing actually does, so `eval/report_dinov2_crop.md` and `eval/report_clip_crop.md`
  were regenerated. New numbers: CLIP+crop real top-1 SKU **75.9% -> 51.7%**, DINOv2+crop **46.6% -> 31.0%**.
  The earlier same-day decision log entry ("kept crop on, small mixed effect") was correct for the buggy
  crop version and is now superseded -- the more correct crop hurts more, not less.
- Choice: crop-to-object preprocessing rejected entirely. `configs/default.yaml` reverted to
  `preprocess.object_crop: false` and `index.dir: data/index` (the plain, uncropped catalogue index) --
  i.e. back to the Phase 4 whole-image CLIP config, which remains the best-measured setup at 75.9%.
- Why it matters: this is the second time a "should help" preprocessing idea (per `docs/PLAN.md`'s
  predicted whole-image weakness) measured worse in practice on this specific catalogue/photo set.
  Whole-image cosine similarity over uncropped photos is, so far, still the best of everything tried.
- Revisit if: a proper object detector (rather than background-subtraction heuristics) is used instead --
  named as next-two-weeks item 3 in `DECISIONS.md`.

## 2026-09-15: Built the backend + frontend (Phase 6), stack as recommended
- Source: mine ("go ahead, start building the backend and frontend"), on Claude's recommended stack
  from the Phase 6 plan written down earlier the same day
- Built: `backend/main.py` (FastAPI: `/health`, `/match`, `/catalogue-image`), `backend/Dockerfile`
  (builds the catalogue + FAISS index at image-build time from committed metadata, same idea as
  `scripts/hydrate_catalogue_images.py`), `render.yaml`. `frontend/` (Next.js + Tailwind, ivory/cream/
  champagne palette per the design brief, upload UI, results grid with confidence bars).
- Verified locally: backend correctly returns the own-gold-chain as top-1 for a real stumper photo over
  HTTP; catalogue-image path-traversal attempt returns 404, not a file; frontend builds clean and the
  dev server serves the right markup/content. Not yet visually checked in an actual browser window — the
  Claude-in-Chrome browser tool wasn't responding this session (timed out, possibly needs a permission
  grant); a manual look is worth doing before deploying.
- Not yet deployed: Render needs my account and a paid-tier confirmation (free tier's ~512MB RAM is very
  likely too small for CLIP+torch, per the cost flag already in `docs/PLAN.md`); Vercel CLI here is
  already authenticated as me, so that deploy is a smaller, near-zero-cost step whenever I say go.
- Also asked Claude to write a prompt for a separate tool ("Anti-Gravity CLI", Gemini-based, large
  context) to do an independent full-repo bug/security scan, output to `docs/ANTIGRAVITY_AUDIT.md`. I
  run that myself; Claude reads the result once I share it.

## 2026-09-15: Backend host switched from Render to Hugging Face Spaces — no paid plans allowed
- Source: mine ("we can't buy any plan for Vercel or Render or anything")
- Options considered: Render free tier (~512MB RAM), Hugging Face Spaces free CPU tier (16GB RAM, no
  card), Google Cloud Run free tier (generous, but requires a billing account on file even for
  free-tier usage), Cloudflare Workers (no PyTorch support at all — would need a full re-architecture
  onto their hosted CLIP model and re-measuring every number in `DECISIONS.md`)
- Choice: Hugging Face Spaces (Docker SDK, free CPU). `render.yaml` removed (no longer the target);
  `scripts/deploy_hf_space.sh` added to populate a Space from a clean clone of its own git repo, reusing
  `backend/Dockerfile` as-is. Frontend stays on Vercel's free Hobby tier — already free, no change.
- Why: Render's free tier genuinely can't run this (CLIP+torch need more than ~512MB and free-tier
  spin-down makes it worse); Spaces gives 30x the RAM for the same $0, with no credit card anywhere in
  the flow, matching the hard constraint exactly.
- Trade-off named: Spaces free tier still sleeps after inactivity, so the first request after idle time
  will be slow (full model reload) — acceptable for a take-home demo, would not be for real traffic.
- Revisit if: this ever needs to handle real traffic rather than a demo, at which point a paid host with
  no sleep behavior becomes worth reconsidering.

## 2026-09-15: Anti-Gravity CLI audit (Gemini) — verified findings, fixed real bugs
- Source: mine (ran the audit prompt Claude drafted earlier); Claude verified each finding before
  acting on any of them rather than trusting the report blindly, then fixed the confirmed ones
- Full report: `docs/ANTIGRAVITY_AUDIT.md`. Verified and fixed:
  - **Critical:** self-sourced catalogue images (`own_*.jpg`) were gitignored with no `image_source_url`
    to rebuild them from — a genuinely clean checkout or Docker build would crash with `FileNotFoundError`
    on `build-index`. Whitelisted them in `.gitignore` and committed; `backend/Dockerfile` now copies
    them explicitly since the hydrate script can't fetch what has no source URL.
  - **Critical:** confirmed 1,528 duplicate `local_path` rows in `products.csv`; the hydrate script's
    16-thread pool could race on writing the same destination file. Deduplicated by destination before
    submitting to the pool, and made `download_and_resize` atomic (unique temp files + `os.replace`)
    so an interrupted run can't leave a corrupt file that later runs mistake for "already downloaded."
  - **Critical:** `embed.py` assumed `transformers>=5`'s `.pooler_output` return shape; `pyproject.toml`
    only pinned `>=4.40`, which returns a bare tensor on 4.x. A clean install resolving 4.x would crash.
    Now handles both.
  - **Critical:** `backend/main.py`'s `/match` read the entire upload into memory before checking its
    size — an oversized upload could exhaust server RAM before the check ever ran. Now reads in bounded
    chunks and aborts as soon as the limit is exceeded.
  - **High, and the most consequential one:** confirmed a real double-crop bug in `rerank.py` — the
    embedder it was given still had its own crop preprocessing on, so every explicit tight-crop this
    function built got cropped *again* inside `embedder.embed()`. This had made the re-rank experiment
    look catastrophically bad (31.0%) when the real number, bug fixed, is 63.8% — still below the 75.9%
    baseline and still doesn't fix the kada, but a materially different, less damning result than first
    reported. Corrected in `DECISIONS.md`.
  - **High:** confirmed the crop-to-object heuristic bisects annular jewellery (rings/bangles) — a
    bangle catalogue image cropped to a 56×269-pixel sliver, one rim only. Fixed (`_dense_extent`: union
    of every dense run per axis, not just the largest one) and re-measured: crop recovers some ground
    (CLIP+crop 51.7%→56.9%) but is still worse than the uncropped baseline. Rejected, for the third
    time, on a corrected number.
  - **Medium, and the more important correction to the write-up:** the audit's background-RGB check
    (verified directly, not trusted blind) shows the self-sourced items' catalogue reference photos
    share a background with every stumper photo (same home table), while the kada's real catalogue
    photo is a studio white background. This means the 100%/96.4% self-sourced numbers are partly
    inflated by background match, and the kada's 0% is at least as much a domain-gap problem as a
    plain-jewellery-similarity one. `DECISIONS.md`'s "Results" and "Next two weeks" rewritten around
    this corrected, more complete diagnosis.
  - Also fixed: insecure string-prefix path-traversal check (now `is_relative_to`), backend crashing if
    launched from a non-repo-root CWD (now anchors CWD to the repo root at import time), missing
    `pillow-heif` for the iPhone HEIC uploads the API already advertised supporting, frontend upload
    control being invisible to keyboard/screen-reader users (`display:none` → `sr-only` + proper
    role/tabIndex/keydown), no fetch timeout on the frontend (added, 90s, sized for the free-tier host's
    cold-start behaviour), iOS Safari's empty `file.type` on camera-roll photos being rejected outright
    (extension fallback added), `augment_stumper.py` silently doubling the synthetic set if run twice
    (now refuses to run if synthetic rows already exist), a missing `configs/dinov2.yaml`, and a
    div-by-zero guard in `far_frr_curve` for `n_thresholds<2`.
- Not changed, after checking: the macro-precision divisor (flagged as a possible bug) already matches
  sklearn's `zero_division=0` convention — made the code's intent explicit in a comment instead of
  changing the number. Client-controlled Content-Type spoofing on `/match` isn't exploitable as flagged,
  since the real validation is PIL actually decoding the file, not the client-supplied header — no
  change needed. The personal email in `scrape.py`'s User-Agent is intentional scraping etiquette
  (a contact address for the scraped sites' admins) and the repo is private — left as-is.
- Why this mattered: several "measured worse, rejected" conclusions from earlier the same day were
  partly artifacts of real bugs, not solely inherent limitations of the ideas being tested. Re-measuring
  after each fix, rather than trusting either the original numbers or the audit's claims blindly, is
  what actually earned the corrected write-up.
