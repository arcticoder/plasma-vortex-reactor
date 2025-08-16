#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import numpy as np
from reactor.metrics import plot_fom_vs_yield


def main():
    ap = argparse.ArgumentParser(description="Plot FOM vs Yield to PNG")
    ap.add_argument("--out", default="fom_yield.png")
    args = ap.parse_args()
    yields = np.array([1e8, 1e10, 1e12], dtype=float)
    foms = np.array([0.05, 0.08, 0.12], dtype=float)
    plot_fom_vs_yield(yields, foms, args.out)
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
