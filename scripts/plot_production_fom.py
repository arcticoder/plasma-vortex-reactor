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
    ap.add_argument("--out", default="production_fom.png")
    ap.add_argument("--Te-eV", type=float, default=10.0)
    args = ap.parse_args()

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


if __name__ == "__main__":
    main()
