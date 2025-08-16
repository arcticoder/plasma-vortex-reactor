#!/usr/bin/env python3
"""
Generate a simple HTML dashboard summarizing roadmap/progress/UQ/VnV NDJSON files.

Inputs (optional overrides via CLI):
  --docs-dir docs/            Directory containing NDJSON docs
  --out progress_dashboard.html

Output:
  progress_dashboard.html     Minimal HTML with counts and recent items

This script uses only the Python stdlib and tolerates missing files.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import os
from pathlib import Path
from typing import List, Dict, Any


NDJSON_FILES = [
    "roadmap.ndjson",
    "roadmap-completed.ndjson",
    "progress_log.ndjson",
    "progress_log-completed.ndjson",
    "UQ-TODO.ndjson",
    "UQ-TODO-RESOLVED.ndjson",
    "VnV-TODO.ndjson",
    "VnV-TODO-RESOLVED.ndjson",
    # Optional synthetic anomaly stream
    "timeline_anomalies.ndjson",
]


def _read_ndjson(p: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if not p.exists():
        return items
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            # tolerate malformed lines
            continue
    return items


def build_html(docs_dir: Path) -> str:
    sections: List[str] = []
    now = _dt.datetime.utcnow().isoformat() + "Z"
    sections.append(f"<p>Generated: {html.escape(now)}</p>")

    # Artifact links section (if files exist at repo root)
    artifacts = [
        "feasibility_gates_report.json",
        "integrated_report.json",
        "production_kpi.json",
        "calibration.json",
        "time_to_metrics.json",
        "time_to_metrics.png",
        "dynamic_stability_ripple.png",
        "high_load_hardware_metrics.png",
    ]
    found = [a for a in artifacts if Path(a).exists()]
    if found:
        sections.append("<h2>Artifacts</h2><ul>" + "".join(
            f"<li><a href='{html.escape(a)}'>{html.escape(a)}</a></li>" for a in found
        ) + "</ul>")

    nav_items: List[str] = []
    for name in NDJSON_FILES:
        p = docs_dir / name
        items = _read_ndjson(p)
        sec_id = html.escape(name.replace(".ndjson", "").replace("_", "-").replace(" ", "-").lower())
        nav_items.append(f"<a href='#sec-{sec_id}'>{html.escape(name)}</a>")
        sections.append(f"<h2 id='sec-{sec_id}'>" + html.escape(name) + f" ({len(items)})</h2>")
        if not items:
            sections.append("<p><em>No entries</em></p>")
            continue
        # Show up to 10 most recent items
        recent = items[-10:]
        sections.append("<ul>")
        for it in recent:
            # pick a nice title-ish field
            title = (
                it.get("title")
                or it.get("milestone")
                or it.get("event")
                or it.get("task")
                or it.get("description")
                or str(it)[:120]
            )
            status = it.get("status") or it.get("state") or it.get("category") or ""
            sections.append(
                f"<li><strong>{html.escape(str(title))}</strong>"
                + (f" <code>{html.escape(str(status))}</code>" if status else "")
                + "</li>"
            )
        sections.append("</ul>")

    navbar = (
        "<nav class='navbar'>"
        + " | ".join(nav_items)
        + "</nav>"
    )
    doc = (
        "<!doctype html>\n<html><head><meta charset='utf-8'>"
        "<title>Progress Dashboard</title>"
        "<style>"
        "body{font-family:sans-serif;margin:24px}"
        "code{background:#f4f4f4;padding:1px 4px;border-radius:3px}"
        ".navbar{position:sticky;top:0;background:#fff8;border-bottom:1px solid #ddd;padding:8px 0;margin-bottom:16px}"
        ".navbar a{margin-right:8px;text-decoration:none;color:#06c}"
        ".navbar a:hover{text-decoration:underline}"
        "</style>"
        "</head><body>\n<h1>Plasma Vortex Reactor — Progress Dashboard</h1>\n"
        + navbar
        + "\n".join(sections)
        + "\n</body></html>\n"
    )
    return doc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-dir", default="docs", help="Docs directory containing NDJSON files")
    ap.add_argument("--out", default="progress_dashboard.html", help="Output HTML path")
    args = ap.parse_args()
    docs_dir = Path(args.docs_dir)
    os.makedirs(docs_dir, exist_ok=True)
    html_doc = build_html(docs_dir)
    Path(args.out).write_text(html_doc)


if __name__ == "__main__":
    main()
