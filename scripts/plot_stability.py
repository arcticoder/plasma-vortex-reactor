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
from reactor.plotting import _mpl


def main():
    ap = argparse.ArgumentParser(description="Plot Γ vs time to PNG")
    ap.add_argument("--out", default="artifacts/stability.png")
    ap.add_argument("--out-json", default=None, help="Optional JSON dump of t_ms and gamma arrays")
    ap.add_argument("--out-csv", default=None, help="Optional CSV dump of t_ms,gamma rows")
    ap.add_argument("--overlay-thresholds", action="store_true")
    ap.add_argument("--series", default=None, help="JSON array of gamma values; if absent, use demo")
    args = ap.parse_args()
    if args.series:
        gam = json.loads(args.series)
        t_ms = list(range(len(gam)))
    else:
        t_ms = [0, 2, 4, 6, 8, 10]
        gam = [150, 149.8, 150.2, 150.1, 149.9, 150.0]
    # Always plot the curve
    plot_stability_curve(t_ms, gam, args.out)
    # Optionally overlay threshold line on the same figure
    if args.overlay_thresholds:
        try:
            thr = json.loads(open("metrics.json").read())
            gmin = float(thr.get("gamma_min", 140.0))
            _mpl()
            import matplotlib.pyplot as _plt
            _plt.axhline(gmin, color="red", linestyle="--", label=f"Γ ≥ {gmin}")
            _plt.legend()
        except Exception:
            pass
    # Optionally write raw data
    try:
        if args.out_json:
            os.makedirs(os.path.dirname(os.path.abspath(args.out_json)) or ".", exist_ok=True)
            with open(args.out_json, "w", encoding="utf-8") as jf:
                json.dump({"t_ms": t_ms, "gamma": gam}, jf, indent=2)
        if args.out_csv:
            import csv as _csv
            os.makedirs(os.path.dirname(os.path.abspath(args.out_csv)) or ".", exist_ok=True)
            with open(args.out_csv, "w", newline="", encoding="utf-8") as cf:
                w = _csv.writer(cf)
                w.writerow(["t_ms", "gamma"])
                for t, g in zip(t_ms, gam):
                    w.writerow([t, g])
    except Exception:
        pass
    print(json.dumps({"wrote": args.out, **({"json": args.out_json} if args.out_json else {}), **({"csv": args.out_csv} if args.out_csv else {})}))


if __name__ == "__main__":
    main()
