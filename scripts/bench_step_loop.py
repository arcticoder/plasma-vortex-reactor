#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

try:
    from reactor.core import Reactor
except Exception:
    Reactor = None  # type: ignore


def main():
    ap = argparse.ArgumentParser(description="Micro-benchmark Reactor.step loop")
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--dt", type=float, default=1e-4)
    ap.add_argument("--grid", default="32,32")
    ap.add_argument("--out", default="bench_step_loop.json")
    args = ap.parse_args()
    try:
        import numpy as _np
        _np.random.seed(0)
    except Exception:
        pass
    gx, gy = [int(x) for x in str(args.grid).split(",")]
    if Reactor is None:
        Path(args.out).write_text(json.dumps({"ok": False, "reason": "reactor not importable"}))
        return
    R = Reactor(grid=(gx, gy), nu=1e-3)
    t0 = time.perf_counter()
    for _ in range(args.steps):
        R.step(dt=args.dt)
    elapsed = time.perf_counter() - t0
    out = {"steps": args.steps, "dt": args.dt, "grid": [gx, gy], "elapsed_s": elapsed}
    Path(args.out).write_text(json.dumps(out))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
