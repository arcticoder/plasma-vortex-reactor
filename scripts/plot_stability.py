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

from reactor.analysis_stat import plot_stability_curve


def main():
    ap = argparse.ArgumentParser(description="Plot Γ vs time to PNG")
    ap.add_argument("--out", default="stability.png")
    ap.add_argument("--series", default=None, help="JSON array of gamma values; if absent, use demo")
    args = ap.parse_args()
    if args.series:
        gam = json.loads(args.series)
        t_ms = [i for i in range(len(gam))]
    else:
        t_ms = [0, 2, 4, 6, 8, 10]
        gam = [150, 149.8, 150.2, 150.1, 149.9, 150.0]
    plot_stability_curve(t_ms, gam, args.out)
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
