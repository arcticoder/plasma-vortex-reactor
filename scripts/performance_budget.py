#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import datetime as _dt


def main() -> None:
    ap = argparse.ArgumentParser(description="Enforce simple performance budgets against bench_step_loop.json")
    ap.add_argument("--bench", default="bench_step_loop.json")
    ap.add_argument("--max-elapsed-s", type=float, default=1.0, help="Maximum allowed elapsed seconds")
    ap.add_argument("--trend-out", default="bench_trend.jsonl", help="Append-only trend file")
    args = ap.parse_args()
    p = Path(args.bench)
    if not p.exists():
        raise SystemExit(f"Missing benchmark file: {p}")
    data = json.loads(p.read_text())
    elapsed = float(data.get("elapsed_s", 0.0))
    ok = elapsed <= float(args.max_elapsed_s)
    # append to trend
    with open(args.trend_out, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": _dt.datetime.utcnow().isoformat()+"Z", "elapsed_s": elapsed})+"\n")
    print(json.dumps({"ok": ok, "elapsed_s": elapsed, "budget_s": args.max_elapsed_s}))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
