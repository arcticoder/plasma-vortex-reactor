#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
from typing import List, Tuple


def _read_csv(path: str) -> Tuple[List[float], List[float]]:
    xs: List[float] = []
    ys: List[float] = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            # Prefer dynamic ripple; fallback to ripple
            rip = row.get("ripple_dynamic") or row.get("ripple")
            if rip is None:
                continue
            xs.append(float(rip))
            ys.append(float(row.get("t", 0.0)))
    return xs, ys


def _fit_alpha(xs: List[float], ys: List[float]) -> float:
    # Simple proportional fit: ripple ~ exp(-alpha * t) => alpha ~ -ln(r2/r1)/(t2-t1)
    if len(xs) < 2 or len(ys) < 2:
        return 0.01
    try:
        import math
        # Find two points far apart in time
        i1, i2 = 0, len(ys) - 1
        t1, t2 = ys[i1], ys[i2]
        r1, r2 = xs[i1], xs[i2]
        if t2 <= t1 or r2 <= 0 or r1 <= 0:
            return 0.01
        return max(1e-6, min(1.0, -math.log(r2 / r1) / (t2 - t1)))
    except Exception:
        return 0.01


def main():
    ap = argparse.ArgumentParser(description="Calibrate ripple decay alpha from sweep CSV")
    ap.add_argument("--from-csv", default="data/full_sweep_with_dynamic_ripple.csv")
    ap.add_argument("--out", default="artifacts/calibration.json")
    args = ap.parse_args()

    xs, ys = _read_csv(args.from_csv)
    alpha = _fit_alpha(xs, ys)
    out = {"alpha": alpha, "source": args.from_csv}
    import os
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
