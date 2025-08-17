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
from typing import List, Dict, Any, Tuple, Optional


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


def _anomalies_counts(items: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for it in items:
        sev = str(it.get("status") or it.get("details", {}).get("severity") or "").strip()
        if not sev:
            continue
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def _plot_fom_trend(kpi_paths: List[Path], out_png: Path) -> None:
    # Try to read FOMs in chronological order and plot a simple trend
    try:
        xs: List[int] = []
        ys: List[float] = []
        for i, kp in enumerate(kpi_paths):
            try:
                data = json.loads(kp.read_text())
                f = data.get("fom")
                if isinstance(f, (int, float)):
                    xs.append(i)
                    ys.append(float(f))
            except Exception:
                continue
        if not xs:
            out_png.write_bytes(b"PNG placeholder - no FOM data\n")
            return
        try:
            # Lazy import matplotlib via reactor.plotting helper
            sys_path_added = False
            import sys as _sys, os as _os
            _src = Path(__file__).resolve().parents[1] / 'src'
            if str(_src) not in _sys.path:
                _sys.path.insert(0, str(_src)); sys_path_added = True
            from reactor.plotting import _mpl  # type: ignore
            plt = _mpl()
            fig, ax = plt.subplots(figsize=(5,3))
            ax.plot(xs, ys, marker='o')
            ax.set_xlabel('Revision')
            ax.set_ylabel('FOM')
            ax.set_title('FOM Trend')
            fig.tight_layout(); fig.savefig(str(out_png), dpi=150); plt.close(fig)
        except Exception:
            out_png.write_bytes(b"PNG placeholder - matplotlib not available\n")
    except Exception:
        try:
            out_png.write_bytes(b"PNG placeholder - error\n")
        except Exception:
            pass


def build_html(docs_dir: Path, fom_trend: bool = False, fom_trend_out: Optional[Path] = None) -> str:
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
    export_summary: Dict[str, Any] = {"generated": now, "sections": []}
    anomalies_counts: Dict[str, int] = {}
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
        export_summary["sections"].append({"name": name, "count": len(items), "recent": recent})
        # Special: show anomaly counts summary badge and trend sparkline for anomalies file
        if name == "timeline_anomalies.ndjson":
            anomalies_counts = _anomalies_counts(items)
            if anomalies_counts:
                badges = " ".join(
                    f"<span class='badge'>{html.escape(k)}={v}</span>" for k, v in anomalies_counts.items()
                )
                # Build a tiny sparkline for cumulative 'fail' events across the last 50 items
                last = items[-50:]
                cum = []
                c = 0
                for it in last:
                    if (it.get('status') == 'fail') or (it.get('details', {}).get('severity') == 'fail'):
                        c += 1
                    cum.append(c)
                if cum:
                    w, h = 200, 40
                    mx = max(cum) or 1
                    points = []
                    for i, v in enumerate(cum):
                        x = int(i * (w - 2) / max(1, len(cum) - 1)) + 1
                        y = int(h - 1 - (v / mx) * (h - 2))
                        points.append(f"{x},{y}")
                    svg = f"<svg width='{w}' height='{h}' viewBox='0 0 {w} {h}'><polyline fill='none' stroke='#d73a49' stroke-width='2' points='{" ".join(points)}' /></svg>"
                    sections.append(f"<div>Fail trend (last {len(cum)}): {svg}</div>")
                sections.append(f"<p>Severity counts: {badges}</p>")
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
            cls = "status-ok" if status == "ok" else ("status-warn" if status == "warn" else ("status-fail" if status == "fail" else ""))
            badge = f"<span class='badge {cls}'>{html.escape(str(status))}</span>" if status else ""
            sections.append(f"<li class='item {cls}'><strong>{html.escape(str(title))}</strong> {badge}</li>")
        sections.append("</ul>")

    # Optionally plot FOM trend from production_kpi.json history at repo root (and docs dir if present)
    if fom_trend:
        kp_list: List[Path] = []
        # Collect a simple set: current production_kpi.json and any found copies under docs
        root_kp = Path("production_kpi.json")
        if root_kp.exists():
            kp_list.append(root_kp)
        # Look for dated snapshots (optional convention)
        for p in sorted(docs_dir.glob("production_kpi*.json")):
            kp_list.append(p)
        if fom_trend_out is None:
            fom_trend_out = Path("progress_dashboard_fom_trend.png")
        _plot_fom_trend(kp_list, fom_trend_out)
        if fom_trend_out.exists():
            sections.append(f"<h2>FOM Trend</h2><p><img src='{html.escape(str(fom_trend_out))}' alt='FOM Trend'></p>")

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
        ".badge{padding:1px 6px;border-radius:10px;font-size:12px;margin-left:6px}"
        ".status-ok .badge{background:#e6ffed;color:#22863a;border:1px solid #34d058}"
        ".status-warn .badge{background:#fff5e6;color:#b08800;border:1px solid #ffd33d}"
        ".status-fail .badge{background:#ffeef0;color:#cb2431;border:1px solid #d73a49}"
        ".filters{margin:8px 0} .filters label{margin-right:12px}"
        ".item{margin:2px 0} .hidden{display:none}"
        "</style>"
        "</head><body>\n<h1>Plasma Vortex Reactor — Progress Dashboard</h1>\n"
        + navbar
    + "<div class='filters'>\n"
        + "<label><input type='checkbox' id='toggle-ok' checked> ok</label>"
        + "<label><input type='checkbox' id='toggle-warn' checked> warn</label>"
        + "<label><input type='checkbox' id='toggle-fail' checked> fail</label>"
    + "<label style='margin-left:16px'>Scenario: <input id='scenario-filter' placeholder='contains...'></label>"
        + "</div>\n"
        + "\n".join(sections)
    + "\n<script>const toggles={ok:true,warn:true,fail:true};let scenario='';function apply(){['ok','warn','fail'].forEach(s=>document.querySelectorAll('.status-'+s).forEach(el=>{const txt=(el.textContent||'').toLowerCase();const show=(toggles[s] && (!scenario || txt.includes(scenario)));el.style.display=(show?'':'none');}));}document.getElementById('toggle-ok').addEventListener('change',e=>{toggles.ok=e.target.checked;apply();});document.getElementById('toggle-warn').addEventListener('change',e=>{toggles.warn=e.target.checked;apply();});document.getElementById('toggle-fail').addEventListener('change',e=>{toggles.fail=e.target.checked;apply();});document.getElementById('scenario-filter').addEventListener('input',e=>{scenario=(e.target.value||'').toLowerCase().trim();apply();});apply();</script>"
        + "\n</body></html>\n"
    )
    # Optionally persist anomalies summary for validation and PR consumption
    try:
        (Path("anomalies_summary.json")).write_text(json.dumps({"generated": now, "counts": anomalies_counts}))
    except Exception:
        pass
    return doc


def export_json(docs_dir: Path, out: Path) -> None:
    # Reuse build_html logic to collect the same summary but write JSON only
    now = _dt.datetime.utcnow().isoformat() + "Z"
    summary: Dict[str, Any] = {"generated": now, "sections": []}
    for name in NDJSON_FILES:
        p = docs_dir / name
        items = _read_ndjson(p)
        recent = items[-10:]
        summary["sections"].append({"name": name, "count": len(items), "recent": recent})
    out.write_text(json.dumps(summary))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-dir", default="docs", help="Docs directory containing NDJSON files")
    ap.add_argument("--out", default="progress_dashboard.html", help="Output HTML path")
    ap.add_argument("--json-out", default="progress_dashboard.json", help="Optional JSON summary export")
    ap.add_argument("--fom-trend", action="store_true", help="Generate a FOM trend plot for the dashboard")
    ap.add_argument("--fom-trend-out", default="progress_dashboard_fom_trend.png")
    args = ap.parse_args()
    docs_dir = Path(args.docs_dir)
    os.makedirs(docs_dir, exist_ok=True)
    html_doc = build_html(docs_dir, fom_trend=bool(args.fom_trend), fom_trend_out=Path(args.fom_trend_out))
    Path(args.out).write_text(html_doc)
    if args.json_out:
        export_json(docs_dir, Path(args.json_out))


if __name__ == "__main__":
    main()
