#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import random
import time

from reactor.config import load_json
from reactor.core import Reactor


def main():
    ap = argparse.ArgumentParser(description="Demo runner with optional timeline logging")
    ap.add_argument("--scenario", default=None, help="Path to scenario JSON")
    ap.add_argument("--timeline-log", default=None, help="NDJSON path for timeline events")
    ap.add_argument("--steps", type=int, default=10)
    ap.add_argument("--dt", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument(
        "--timeline-budget",
        type=int,
        default=10,
        help="Max events to log; beyond this, suppress",
    )
    ap.add_argument(
        "--enforce-density",
        action="store_true",
        help="Enable density enforcement checks during steps",
    )
    ap.add_argument(
        "--json-out",
        default=None,
        help="If provided, write a tiny JSON summary to this path",
    )
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
    from reactor.random_utils import set_seed
    set_seed(int(args.seed))
    R = Reactor(
        grid=grid,
        nu=nu,
        timeline_log_path=timeline_path,
        xi=xi,
        b_field_ripple_pct=br,
    timeline_budget=int(args.timeline_budget)
        if args.timeline_budget is not None
    else None,
    enforce_density=bool(args.enforce_density),
    )
    # log a run_started event with seed if timeline is enabled
    if timeline_path:
        from reactor.logging_utils import append_event as _append_event
        _append_event(
            str(timeline_path),
            event="run_started",
            status="ok",
            details={"seed": int(args.seed)},
        )
    t0 = time.perf_counter()
    t0_ns = time.perf_counter_ns()
    # naive budget enforcement: just stop logging after N events by nulling the path
    events_logged = 0
    for i in range(int(args.steps)):
        st = time.perf_counter()
        st_ns = time.perf_counter_ns()
        R.step(dt=float(args.dt))
        et = time.perf_counter()
        et_ns = time.perf_counter_ns()
        # include timing in timeline events by emitting a generic step event
        if timeline_path and events_logged < args.timeline_budget:
            from reactor.logging_utils import append_event
            append_event(
                str(timeline_path),
                event="step",
                status="ok",
                details={
                    "i": i,
                    "dt": float(args.dt),
                    "elapsed_s": et - st,
                    "elapsed_ns": int(et_ns - st_ns),
                    "seed": int(args.seed),
                },
            )
        if timeline_path and events_logged >= args.timeline_budget:
            R.timeline_log_path = None
        else:
            events_logged += 1
    t1 = time.perf_counter()
    t1_ns = time.perf_counter_ns()
    summary = {
        "done": True,
        "timeline": timeline_path or None,
        "elapsed_s": t1 - t0,
        "elapsed_ns": int(t1_ns - t0_ns),
        "seed": int(args.seed),
    }
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
