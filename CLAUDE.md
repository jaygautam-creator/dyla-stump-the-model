# Working notes for AI coding sessions

I use Claude Code as a pair programmer on this project. This file is loaded at the start of every
session so the tool has my context. It is written by me, for the tool.

## The project

Take-home for Thuli Studios (Dyla), Problem 2 "Stump the Model". I'm building a visual matcher that takes a
phone photo of a jewellery piece and returns the exact catalogue item (top-5 + confidence, or "not in
catalogue"), plus my own hard phone-photo test set and an evaluation harness that explains why it fails.
I chose jewellery because that is Dyla's sector.

## Where things are

| File | What it holds |
|---|---|
| `docs/PROJECT_BRIEF.md` | My notes on the company, the product, the problem, and what they're asking for |
| `docs/PLAN.md` | Solution, what goes beyond the brief, the refusal extension, architecture, eval method, phases |
| `docs/STATUS.md` | Current phase, open decisions, next step, session history. **Read this first.** |
| `docs/DECISION_LOG.md` | Every decision with options, reasoning, and whether it was mine or a suggestion I accepted |
| `DECISIONS.md` | The ≤2-page write-up I submit. Filled in at the end from the decision log and eval report |
| `logs/` | Exported AI session transcripts (required by the brief) |
| `scripts/export_logs.py` | Exports Claude Code transcripts into `logs/` |
| `.claude/skills/` | `resume`, `log-decision`, `export-logs` |

The original brief PDF is kept locally and not committed.

## Start of a session

1. Read `docs/STATUS.md`: phase, open decisions, next step.
2. If an open decision blocks the next step, ask me. Give a recommendation, but don't make the call.
3. Summarise where we are in a few lines and wait for my go-ahead unless I've already given an instruction.

## End of a session

1. Update `docs/STATUS.md` (checklist, next step, session history line).
2. Append decisions to `docs/DECISION_LOG.md`.
3. Run `python3 scripts/export_logs.py`.

## Rules

- I make the decisions. Propose options with a recommendation; I choose. Log honestly who decided what.
- Don't build ahead of what I've asked for.
- Keep it small and modular. I need to be able to explain and change every part live in the follow-up call.
  Every component should be swappable through config. No scaffolding for the sake of volume.
- Measure, don't assume. Any "better" claim needs a number from the harness. Keep rejected approaches and
  their numbers; they go into DECISIONS.md.
- Never tune thresholds or calibration on the test split.
- The stumper test set is frozen before I start improving the matcher.
- Name weaknesses openly.
- Machine: Apple M2, 8 GB RAM, ~29 GB free disk. CPU/MPS only, store resized images, watch memory.
- Scraping: respect robots.txt and terms, rate-limit, keep the source URL for every image.

## Submission checklist

- Private GitHub repo shared with the team
- Code (matcher + stumper harness)
- `logs/` with transcripts of every AI session
- `DECISIONS.md` ≤ 2 pages: architecture chosen and rejected, trade-offs, testing, where it breaks, next 2 weeks
- `README.md` that runs on a clean machine in under 5 minutes
- Email to careers@thuli.studio with LinkedIn and a short blurb
