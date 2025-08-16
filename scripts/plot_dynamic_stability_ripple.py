#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import os
import sys
from typing import List, Tuple

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.analysis_stat import plot_stability_ripple


def _read_sweep(path: str) -> Tuple[List[float], List[float]]:
    # Derive a toy stability probability from ripple values (monotone decreasing)
    ripples: List[float] = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rp = None
            if "ripple_dynamic" in row:
                rp = float(row["ripple_dynamic"])  # dynamic sweep
            elif "ripple" in row:
                rp = float(row["ripple"])  # time sweep
            if rp is not None:
                ripples.append(rp)
    # Sample down to a few quantiles for plotting
    ripples_sorted = sorted(ripples)
    if not ripples_sorted:
        return [5e-5, 1e-4, 2e-4], [0.999, 0.998, 0.995]
    n = len(ripples_sorted)
    # Use approximate 10th, 50th, 90th percentiles
    percentiles = [0.1, 0.5, 0.9] if n >= 3 else [0.0, 0.5, 1.0]
    idx = [max(0, min(n-1, int(round(p * (n - 1))))) for p in percentiles]
    xs = [ripples_sorted[i] for i in idx]
    # Heuristic mapping ripple->prob
    def p(r):
        if r <= 5e-5:
            return 0.999
        if r <= 1e-4:
            return 0.998
        return 0.995
    ys = [p(x) for x in xs]
    return xs, ys


def main():
    ap = argparse.ArgumentParser(description="Plot dynamic stability vs ripple")
    ap.add_argument("--from-sweep", default=None, help="Optional CSV produced by time/dynamic ripple sweeps")
    ap.add_argument("--out", default="dynamic_stability_ripple.png")
    args = ap.parse_args()

    if args.from_sweep and os.path.exists(args.from_sweep):
        xs, ys = _read_sweep(args.from_sweep)
    else:
        xs, ys = [5e-5, 1e-4, 2e-4], [0.999, 0.998, 0.995]

    plot_stability_ripple(xs, ys, args.out)


if __name__ == "__main__":
    main()
