#!/usr/bin/env python
from __future__ import annotations
import argparse
import json
from pathlib import Path
from reactor.core import Reactor
import time, random
from reactor.config import load_json


def main():
    ap = argparse.ArgumentParser(description="Demo runner with optional timeline logging")
    ap.add_argument("--scenario", default=None, help="Path to scenario JSON")
    ap.add_argument("--timeline-log", default=None, help="NDJSON path for timeline events")
    ap.add_argument("--steps", type=int, default=10)
    ap.add_argument("--dt", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--timeline-budget", type=int, default=10, help="Max events to log; beyond this, suppress")
    args = ap.parse_args()

    cfg = {}
    if args.scenario:
        cfg = load_json(args.scenario)

    timeline_path = args.timeline_log or cfg.get("timeline_log_path")
    xi = cfg.get("xi", 2.0)
    br = cfg.get("b_field_ripple_pct", 0.005)
    grid = tuple(cfg.get("grid", [32, 32]))
    nu = float(cfg.get("nu", 1e-3))

    random.seed(args.seed)
    R = Reactor(grid=grid, nu=nu, timeline_log_path=timeline_path, xi=xi, b_field_ripple_pct=br)
    t0 = time.perf_counter()
    # naive budget enforcement: just stop logging after N events by nulling the path
    events_logged = 0
    for i in range(int(args.steps)):
        st = time.perf_counter()
        R.step(dt=float(args.dt))
        et = time.perf_counter()
        # include timing in timeline events by emitting a generic step event
        if timeline_path and events_logged < args.timeline_budget:
            from reactor.logging_utils import append_event
            append_event(str(timeline_path), event="step", status="ok", details={"i": i, "dt": float(args.dt), "elapsed_s": et - st, "seed": int(args.seed)})
        if timeline_path and events_logged >= args.timeline_budget:
            R.timeline_log_path = None
        else:
            events_logged += 1
    t1 = time.perf_counter()
    print(json.dumps({"done": True, "timeline": timeline_path or None, "elapsed_s": t1 - t0, "seed": int(args.seed)}))


if __name__ == "__main__":
    main()
