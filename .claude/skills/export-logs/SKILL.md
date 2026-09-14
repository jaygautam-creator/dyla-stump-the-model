---
name: export-logs
description: Export all Claude Code session transcripts for this project into logs/ (required for the take-home submission). Use at the end of every session or when the user says "save logs" / "export logs".
---

# Export session logs

The brief says: "A submission without logs is not evaluated." Export every session.

1. Run: `python3 scripts/export_logs.py`
   - Reads every `*.jsonl` transcript for this project from `~/.claude/projects/<project-slug>/`
   - Writes a readable `logs/<date>_<session-id>.md` and copies the raw file to `logs/raw/`
   - Safe to re-run; it overwrites with the latest version.
2. Report which files were written.
3. Reminder: transcripts from other tools (Cursor, ChatGPT, etc.) must be exported manually into `logs/`.
4. Before submission, skim the exports for secrets (API keys, tokens) and redact them.
