"""Export Claude Code session transcripts for this project into logs/.

Writes a readable markdown file per session plus a copy of the raw JSONL.
Usage: python3 scripts/export_logs.py
"""
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOGS = REPO / "logs"
MAX_TOOL_CHARS = 3000  # truncate long tool inputs/outputs in the readable copy (raw copy is complete)


def project_transcript_dir() -> Path:
    # Claude Code stores transcripts under ~/.claude/projects/<cwd with "/" replaced by "-">
    slug = str(REPO).replace("/", "-")
    candidates = [p for p in (Path.home() / ".claude" / "projects").iterdir()
                  if p.name.lower() == slug.lower()]
    if not candidates:
        raise SystemExit(f"No transcript folder found for {REPO} (expected slug {slug})")
    return candidates[0]


def clip(text: str) -> str:
    return text if len(text) <= MAX_TOOL_CHARS else text[:MAX_TOOL_CHARS] + f"\n… [truncated {len(text) - MAX_TOOL_CHARS} chars]"


def render_content(content) -> list[str]:
    if isinstance(content, str):
        return [content]
    out = []
    for block in content:
        kind = block.get("type")
        if kind == "text":
            out.append(block["text"])
        elif kind == "tool_use":
            out.append(f"**Tool call — {block.get('name')}**\n```json\n{clip(json.dumps(block.get('input'), indent=2))}\n```")
        elif kind == "tool_result":
            res = block.get("content")
            if isinstance(res, list):
                res = "\n".join(b.get("text", f"[{b.get('type')}]") for b in res)
            out.append(f"**Tool result**\n```\n{clip(str(res))}\n```")
    return out


def export(jsonl: Path) -> Path:
    lines, first_ts = [], None
    for raw in jsonl.read_text().splitlines():
        rec = json.loads(raw)
        if rec.get("type") not in ("user", "assistant"):
            continue
        first_ts = first_ts or rec.get("timestamp", "")
        msg = rec.get("message", {})
        parts = [p for p in render_content(msg.get("content", "")) if p.strip()]
        if not parts:
            continue
        who = "User" if msg.get("role") == "user" else "Claude"
        if rec.get("isSidechain"):
            who += " (subagent)"
        lines.append(f"### {who} — {rec.get('timestamp', '')}\n\n" + "\n\n".join(parts))

    date = (first_ts or "unknown")[:10]
    out = LOGS / f"{date}_{jsonl.stem}.md"
    out.write_text(f"# Claude Code session {jsonl.stem}\n\n" + "\n\n---\n\n".join(lines) + "\n")
    (LOGS / "raw").mkdir(parents=True, exist_ok=True)
    shutil.copy2(jsonl, LOGS / "raw" / jsonl.name)
    return out


def main():
    LOGS.mkdir(exist_ok=True)
    for jsonl in sorted(project_transcript_dir().glob("*.jsonl")):
        print("wrote", export(jsonl).relative_to(REPO))


if __name__ == "__main__":
    main()
