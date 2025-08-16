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

from reactor.metrics import confinement_efficiency_estimator
from reactor.plotting import _mpl


def main():
    ap = argparse.ArgumentParser(description="Plot Confinement Efficiency vs. xi")
    ap.add_argument("--out", default="confinement_xi.png")
    args = ap.parse_args()
    xs = [0.5, 1.0, 2.0, 4.0]
    ys = [confinement_efficiency_estimator(x, 5e-4) for x in xs]
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(xs, ys, color="#9966FF")
    ax.set_xlabel("ξ")
    ax.set_ylabel("η")
    ax.set_title("Confinement Efficiency vs. ξ")
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
