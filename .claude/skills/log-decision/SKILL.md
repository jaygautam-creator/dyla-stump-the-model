---
name: log-decision
description: Record a project decision in docs/DECISION_LOG.md (and update docs/STATUS.md open decisions). Use whenever I make, accept, change, or overrule a decision.
---

# Log a decision

Append to the bottom of `docs/DECISION_LOG.md` using this format:

```
## YYYY-MM-DD: title
- Source: mine | suggested by Claude, accepted | suggested by Claude, changed | overruled Claude
- Options: ...
- Choice: ...
- Why / evidence: ... (numbers from eval/report.md if it's a measured choice)
- Revisit if: ...
```

Rules:
- Attribute honestly, including when I overrule a suggestion.
- If the decision was measured, cite the experiment and numbers; keep rejected options with their numbers.
- If it resolves an open decision in `docs/STATUS.md`, remove it from the open table and tick the checklist.
- If it changes the plan, update the relevant section of `docs/PLAN.md` too.
- Use today's absolute date.
