#!/usr/bin/env python
from __future__ import annotations

import argparse
import numpy as np

import os, sys
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.metrics import antiproton_yield_estimator
from reactor.plotting import _mpl
from reactor.thresholds import thresholds_from_json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="yield_density.png")
    ap.add_argument("--overlay-thresholds", action="store_true")
    ap.add_argument("--metrics", default="metrics.json")
    args = ap.parse_args()
    densities = np.array([1e19, 1e20, 1e21], dtype=float)
    yields = [antiproton_yield_estimator(n, 10.0, {"model": "physics"}) for n in densities]
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(5,4))
    ax.scatter(densities, yields, color="crimson")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Density (cm⁻³)")
    ax.set_ylabel("Yield (cm⁻³ s⁻¹)")
    ax.set_title("Yield vs. Density")
    # overlay threshold(s)
    if args.overlay_thresholds:
        try:
            thr = thresholds_from_json(args.metrics)
            ax.axhline(1e8, color="gray", linestyle=":", linewidth=1, label="Yield min (proxy)")
        except Exception:
            pass
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
