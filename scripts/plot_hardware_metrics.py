#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os, sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.plotting import _mpl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-json", default=None, help="Path to hardware metrics JSON (list of {t_ms, i})")
    ap.add_argument("--out", default="hardware_metrics.png")
    args = ap.parse_args()

    data = []
    if args.in_json and os.path.exists(args.in_json):
        data = json.loads(open(args.in_json, "r").read())
    else:
        # Fallback demo data
        data = [{"t_ms": i, "i": v} for i, v in enumerate([1.0, 1.1, 1.2, 1.1, 1.0])]

    t_ms = [d.get("t_ms", i) for i, d in enumerate(data)]
    i_vals = [d.get("i", 0.0) for d in data]

    plt = _mpl()
    fig, ax = plt.subplots(figsize=(5,4))
    ax.plot(t_ms, i_vals, color="crimson")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Hardware Metric (i)")
    ax.set_title("Hardware State vs Time")
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
