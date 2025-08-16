#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import os, sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.analysis_fields import simulate_b_field_ripple
from reactor.analysis_stat import stability_probability


essential = {
    "desc": "Ablation: Compare stability with ripple control ON vs OFF",
    "metric": "stability_probability",
}


def run_once(n: int = 10000, base_T: float = 5.0, ripple_pct: float = 0.005, control: bool = True) -> float:
    import numpy as np
    series = simulate_b_field_ripple(n=n, base_T=base_T, ripple_pct=ripple_pct, seed=123)
    # Simple control: reduce ripple by factor 2 when control is ON
    if control:
        series = base_T + (series - base_T) * 0.5
    # Map B-series variance proxy to stability time series around 150
    gamma = np.ones_like(series) * 150.0 + (series - base_T) * 1e3
    return stability_probability(gamma, threshold=140.0, steps=n)


def main() -> None:
    ap = argparse.ArgumentParser(description="Ripple ablation study: control ON vs OFF")
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--ripple-pct", type=float, default=0.005)
    ap.add_argument("--out", default="ablation_ripple.json")
    args = ap.parse_args()

    p_on = run_once(n=int(args.n), ripple_pct=float(args.ripple_pct), control=True)
    p_off = run_once(n=int(args.n), ripple_pct=float(args.ripple_pct), control=False)
    delta = float(p_on - p_off)
    res = {"on": float(p_on), "off": float(p_off), "delta": delta, **essential}
    Path(args.out).write_text(json.dumps(res))
    print(json.dumps(res))


if __name__ == "__main__":
    main()
