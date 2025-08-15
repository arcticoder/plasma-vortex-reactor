#!/usr/bin/env python
from __future__ import annotations
import argparse
import json
from pathlib import Path
from reactor.core import Reactor
from reactor.config import load_json


def main():
    ap = argparse.ArgumentParser(description="Demo runner with optional timeline logging")
    ap.add_argument("--scenario", default=None, help="Path to scenario JSON")
    ap.add_argument("--timeline-log", default=None, help="NDJSON path for timeline events")
    ap.add_argument("--steps", type=int, default=10)
    ap.add_argument("--dt", type=float, default=1e-3)
    args = ap.parse_args()

    cfg = {}
    if args.scenario:
        cfg = load_json(args.scenario)

    timeline_path = args.timeline_log or cfg.get("timeline_log_path")
    xi = cfg.get("xi", 2.0)
    br = cfg.get("b_field_ripple_pct", 0.005)
    grid = tuple(cfg.get("grid", [32, 32]))
    nu = float(cfg.get("nu", 1e-3))

    R = Reactor(grid=grid, nu=nu, timeline_log_path=timeline_path, xi=xi, b_field_ripple_pct=br)
    for _ in range(int(args.steps)):
        R.step(dt=float(args.dt))
    print(json.dumps({"done": True, "timeline": timeline_path or None}))


if __name__ == "__main__":
    main()
