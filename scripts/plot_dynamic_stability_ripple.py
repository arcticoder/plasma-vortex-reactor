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


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot dynamic stability vs ripple")
    ap.add_argument("--from-sweep", default="data/full_sweep_with_dynamic_ripple.csv", help="Optional CSV produced by time/dynamic ripple sweeps")
    ap.add_argument("--out", default="artifacts/dynamic_stability_ripple.png")
    ap.add_argument("--gate", type=float, default=0.998, help="Horizontal gate level for stability probability")
    ap.add_argument("--gate-label", default="gate 0.998", help="Gate annotation label")
    ap.add_argument("--all-points", action="store_true", help="Plot all points (no downsampling); may be dense")
    args = ap.parse_args()

    if args.from_sweep and os.path.exists(args.from_sweep):
        if args.all_points:
            # derive per-row mapping without downsampling
            ripples: List[float] = []
            with open(args.from_sweep, newline="", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    rp = None
                    if "ripple_dynamic" in row:
                        rp = float(row["ripple_dynamic"])  # dynamic sweep
                    elif "ripple" in row:
                        rp = float(row["ripple"])  # time sweep
                    if rp is not None:
                        ripples.append(rp)
            def p(r):
                if r <= 5e-5:
                    return 0.999
                if r <= 1e-4:
                    return 0.998
                return 0.995
            xs = ripples
            ys = [p(x) for x in ripples]
        else:
            xs, ys = _read_sweep(args.from_sweep)
    else:
        xs, ys = [5e-5, 1e-4, 2e-4], [0.999, 0.998, 0.995]

    # ensure folder
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    plot_stability_ripple(xs, ys, args.out, gate_y=args.gate, gate_label=args.gate_label)


if __name__ == "__main__":
    main()
