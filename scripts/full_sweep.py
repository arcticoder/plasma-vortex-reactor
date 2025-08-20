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

from param_sweep_confinement import full_sweep


def main():
    ap = argparse.ArgumentParser(description="Run full parameter sweep and save CSV")
    ap.add_argument("--out", default="full_sweep.csv")
    args = ap.parse_args()
    n_e_range = [1e19, 1e20, 1e21]
    T_e_range = [5.0, 10.0, 15.0]
    B_range = [5.0, 6.0]
    xi_range = [1.0, 2.0, 3.0]
    full_sweep(n_e_range, T_e_range, B_range, xi_range, out_csv=args.out)


if __name__ == "__main__":
    main()
