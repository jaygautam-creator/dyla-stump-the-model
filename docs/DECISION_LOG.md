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
