#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import numpy as np
from reactor.metrics import antiproton_yield_estimator, total_fom, plot_fom_vs_yield


def main():
    ap = argparse.ArgumentParser(description="Plot production-focused FOM vs Yield")
    ap.add_argument("--out", default="production_fom_yield.png")
    ap.add_argument("--Te-eV", type=float, default=10.0)
    ap.add_argument("--fixed", action="store_true", help="Plot fixed production points for CI artifact")
    ap.add_argument("--overlay-thresholds", action="store_true")
    args = ap.parse_args()

    if args.fixed:
        # Use fixed points as requested for production artifact
        yields = np.array([1e12, 1e13, 1e14], dtype=float)
        foms = np.array([0.12, 0.15, 0.18], dtype=float)
    else:
        # Sample points representative of production regimes
        n_vals = np.array([1e19, 1e20, 1e21], dtype=float)
        E_vals = np.array([1e8, 1e9, 1e10], dtype=float)
        yields = []
        foms = []
        for n, E in zip(n_vals, E_vals):
            y = antiproton_yield_estimator(n, args.Te_eV, {"model": "physics"})
            f = total_fom(y, E)
            yields.append(y)
            foms.append(f)

    plot_fom_vs_yield(np.array(yields), np.array(foms), args.out)
    if args.overlay_thresholds:
        try:
            import json as _json
            from reactor.plotting import _mpl
            plt = _mpl()
            m = _json.loads(open(os.path.join(_root, "metrics.json")).read())
            thr = float(m.get("fom_min", 0.1))
            import matplotlib.pyplot as _plt  # type: ignore
            _plt.axhline(thr, color="red", linestyle="--", label=f"FOM ≥ {thr}")
            _plt.legend()
        except Exception:
            pass


if __name__ == "__main__":
    main()
