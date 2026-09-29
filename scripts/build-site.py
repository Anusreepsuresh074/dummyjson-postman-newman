#!/usr/bin/env python3
"""Assembles the latest main, data and defects reports into site/ for GitHub Pages.

Usage: scripts/build-site.py [reports dir] [site dir]   (defaults: reports/ and site/)

Each run's HTML report is copied to site/<mode>/index.html, and site/index.html links to them with
each run's one-line verdict from its summary.md (written by scripts/summarize.py).
"""

import html
import re
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/Anusreepsuresh074/dummyjson-postman-newman"
INTRO = (
    "The latest reports from CI. Headers and bodies are left out of the reports on purpose, "
    "because they contain credentials and tokens."
)
MODES = {
    "main": ("API tests", "Every functional folder: the run that decides pass or fail."),
    "data": ("Data-driven search", "One search request, run once per row of data/search-terms.csv."),
    "defects": ("Known defects", "Correct-behaviour checks for 13 recorded DummyJSON defects; expected to fail."),
}


def latest_run(reports, mode):
    runs = sorted(p for p in reports.glob(f"*-{mode}") if (p / "summary.md").exists())
    return runs[-1] if runs else None


def main():
    reports = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "reports"
    site = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "site"
    shutil.rmtree(site, ignore_errors=True)
    site.mkdir(parents=True)

    cards = []
    for mode, (title, about) in MODES.items():
        run = latest_run(reports, mode)
        if run is None:
            continue
        (site / mode).mkdir()
        shutil.copy(run / "report.html", site / mode / "index.html")
        first_line = (run / "summary.md").read_text().splitlines()[0]
        verdict = re.sub(r"\*\*(.+?)\*\*", r"\1", first_line.split(": ", 1)[1])
        cards.append(
            f'<a class="card" href="{mode}/"><h2>{html.escape(title)}</h2>'
            f'<p class="verdict">{html.escape(verdict)}</p><p>{html.escape(about)}</p>'
            f'<p class="when">Run {html.escape(run.name.split("-")[0])} UTC</p></a>'
        )

    built = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    (site / "index.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DummyJSON Postman + Newman reports</title>
<style>
  :root {{ --bg: #f7f7f5; --card: #fff; --text: #1d1d1b; --muted: #5c5c57; --line: #dddcd6; --accent: #2f5d8a; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #1b1b1a; --card: #262624; --text: #ecebe6; --muted: #a9a8a1; --line: #3a3a37; --accent: #8db4dc; }}
  }}
  body {{ margin: 0; background: var(--bg); color: var(--text); font: 16px/1.5 system-ui, sans-serif; }}
  main {{ max-width: 860px; margin: 0 auto; padding: 32px 16px; }}
  h1 {{ font-size: 1.6rem; margin: 0 0 4px; }}
  .sub {{ color: var(--muted); margin: 0 0 24px; }}
  .grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }}
  .card {{ display: block; background: var(--card); border: 1px solid var(--line); border-radius: 10px;
          padding: 16px; color: inherit; text-decoration: none; }}
  .card:hover {{ border-color: var(--accent); }}
  .card h2 {{ font-size: 1.1rem; margin: 0 0 8px; color: var(--accent); }}
  .verdict {{ font-weight: 600; margin: 0 0 8px; }}
  .card p {{ margin: 0 0 8px; }}
  .when, footer {{ color: var(--muted); font-size: 0.85rem; }}
  footer {{ margin-top: 24px; }}
  footer a {{ color: var(--accent); }}
</style>
</head>
<body>
<main>
  <h1>DummyJSON API tests: Postman + Newman</h1>
  <p class="sub">{INTRO}</p>
  <div class="grid">
    {"".join(cards)}
  </div>
  <footer>Built {built} · <a href="{REPO}">Source on GitHub</a></footer>
</main>
</body>
</html>
""")
    print(f"site built in {site} ({len(cards)} reports)")


if __name__ == "__main__":
    main()
