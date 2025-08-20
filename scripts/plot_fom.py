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

from reactor.plotting import _mpl


def main():
    ap = argparse.ArgumentParser(description="Plot FOM vs Yield to PNG")
    ap.add_argument("--out", default="fom_yield.png")
    args = ap.parse_args()
    # If error bars are desired, render directly here
    xs = np.array([1e8, 1e10, 1e12], dtype=float)
    ys = np.array([0.05, 0.08, 0.12], dtype=float)
    yerr_lower = np.array([0.01, 0.01, 0.01], dtype=float)
    yerr_upper = np.array([0.01, 0.01, 0.01], dtype=float)
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.errorbar(xs, ys, yerr=[yerr_lower, yerr_upper], fmt='o', color='goldenrod', ecolor='khaki', elinewidth=1)
    ax.set_xlabel("Yield (cm⁻³ s⁻¹)")
    ax.set_ylabel("FOM")
    ax.set_title("FOM vs Yield")
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    plt.close(fig)
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
