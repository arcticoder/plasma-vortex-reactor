#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import datetime as _dt
from typing import Any, Dict


def _load_budget_config(path: str | None) -> Dict[str, Any]:
    if not path:
        return {}
    try:
        p = Path(path)
        if p.exists():
            return json.loads(p.read_text())
    except Exception:
        return {}
    return {}


def _shield(label: str, status: str, color: str) -> str:
    # Simple Markdown shield using shields.io (no external call, just link)
    import urllib.parse as _u
    url = f"https://img.shields.io/badge/{_u.quote(label)}-{_u.quote(status)}-{_u.quote(color)}"
    return f"![{label}]({url})"


def main() -> None:
    ap = argparse.ArgumentParser(description="Enforce simple performance budgets against bench_step_loop.json")
    ap.add_argument("--bench", default="bench_step_loop.json")
    ap.add_argument("--max-elapsed-s", type=float, default=1.0, help="Maximum allowed elapsed seconds")
    ap.add_argument("--trend-out", default="bench_trend.jsonl", help="Append-only trend file")
    ap.add_argument("--budget-config", default="configs/metrics_budget.json")
    ap.add_argument("--job-summary", default="perf_budget_summary.md")
    ap.add_argument("--min-fom", type=float, default=None, help="Minimum allowed FOM from production_kpi.json (override or fallback to budget-config)")
    args = ap.parse_args()
    p = Path(args.bench)
    if not p.exists():
        raise SystemExit(f"Missing benchmark file: {p}")
    data = json.loads(p.read_text())
    elapsed = float(data.get("elapsed_s", 0.0))
    # Allow override from config
    budget_cfg = _load_budget_config(args.budget_config)
    max_elapsed = float(budget_cfg.get("bench", {}).get("max_elapsed_s", args.max_elapsed_s))
    ok = elapsed <= max_elapsed
    # derive min_fom from args or budget config
    min_fom = args.min_fom
    if min_fom is None:
        try:
            min_fom = float(budget_cfg.get("kpi", {}).get("min_fom"))
        except Exception:
            min_fom = None
    # append to trend
    with open(args.trend_out, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": _dt.datetime.utcnow().isoformat()+"Z", "elapsed_s": elapsed})+"\n")
    # Optional FOM check
    fom_ok = True
    fom_val = None
    try:
        if min_fom is not None and Path("production_kpi.json").exists():
            kpi = json.loads(Path("production_kpi.json").read_text())
            fom_val = kpi.get("fom")
            if isinstance(fom_val, (int, float)):
                fom_ok = float(fom_val) >= float(min_fom)
    except Exception:
        pass
    result = {"ok": ok and fom_ok, "elapsed_s": elapsed, "budget_s": max_elapsed, "fom": fom_val, "min_fom": min_fom}
    print(json.dumps(result))
    if not (ok and fom_ok):
        raise SystemExit(1)
    # Write a small job summary markdown with a badge
    try:
        badge = _shield("perf", "ok" if ok else "fail", "brightgreen" if ok else "red")
        summary = f"# Performance Budget\n\n{badge}  Elapsed: {elapsed:.3f}s / Budget: {max_elapsed:.3f}s\n"
        if min_fom is not None:
            summary += f"\nMin FOM: {min_fom}  | Current FOM: {fom_val if fom_val is not None else 'n/a'}\n"
        Path(args.job_summary).write_text(summary)
    except Exception:
        pass


if __name__ == "__main__":
    main()
