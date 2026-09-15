"""Renders the per-condition accuracy chart in docs/assets/accuracy-chart.svg from eval/report_clip.md.

Hand-written SVG, not matplotlib -- one static chart for the README doesn't justify a new project
dependency. Re-run whenever eval/report_clip.md's real-photo numbers change.
"""
import re
from pathlib import Path

REPORT = Path("eval/report_clip.md")
OUT = Path("docs/assets/accuracy-chart.svg")

IVORY = "#faf6ef"
CHAMPAGNE = "#c9a86a"
CHAMPAGNE_DARK = "#a9834a"
CHARCOAL = "#2a2521"
STONE = "#78716c"
LINE = "#e7dcc8"


def parse_conditions(text: str) -> list[tuple[str, int, float]]:
    headline = text.split("## Headline")[1].split("\n---\n")[0]
    rows = re.findall(r"\| (\w+) \| (\d+) \| ([\d.]+) \| \[", headline.split("Per-condition")[1])
    return [(name, int(n), float(acc)) for name, n, acc in rows]


def render_svg(rows: list[tuple[str, int, float]]) -> str:
    rows = sorted(rows, key=lambda r: r[2])
    bar_h, gap, left_pad, right_pad, top_pad = 34, 14, 160, 90, 40
    width = 720
    height = top_pad + len(rows) * (bar_h + gap) + 20

    bars = []
    for i, (name, n, acc) in enumerate(rows):
        y = top_pad + i * (bar_h + gap)
        bar_w = (width - left_pad - right_pad) * acc
        pct = f"{acc * 100:.0f}%"
        bars.append(f"""
    <text x="{left_pad - 12}" y="{y + bar_h / 2 + 5}" text-anchor="end" font-size="14" fill="{CHARCOAL}" font-family="ui-sans-serif,system-ui">{name} (n={n})</text>
    <rect x="{left_pad}" y="{y}" width="{width - left_pad - right_pad}" height="{bar_h}" rx="6" fill="{IVORY}" stroke="{LINE}"/>
    <rect x="{left_pad}" y="{y}" width="{bar_w}" height="{bar_h}" rx="6" fill="{CHAMPAGNE}"/>
    <text x="{left_pad + bar_w + 10}" y="{y + bar_h / 2 + 5}" font-size="14" font-weight="600" fill="{CHAMPAGNE_DARK}" font-family="ui-sans-serif,system-ui">{pct}</text>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="white"/>
  <text x="{left_pad}" y="24" font-size="16" font-weight="600" fill="{CHARCOAL}" font-family="ui-sans-serif,system-ui">Top-1 SKU accuracy by condition (real photos, CLIP)</text>
  {''.join(bars)}
</svg>"""


def main():
    text = REPORT.read_text()
    rows = parse_conditions(text)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render_svg(rows))
    print(f"wrote {OUT} ({len(rows)} conditions)")


if __name__ == "__main__":
    main()
