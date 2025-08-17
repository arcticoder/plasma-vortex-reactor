#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from reactor.plotting import _mpl


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot dynamic ripple vs time from full_sweep_with_dynamic_ripple.csv")
    ap.add_argument("--from-csv", default="full_sweep_with_dynamic_ripple.csv")
    ap.add_argument("--out", default="dynamic_ripple_time.png")
    args = ap.parse_args()

    rows = []
    try:
        with open(args.from_csv, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows.append(r)
    except Exception:
        print(json.dumps({"skipped": True}))
        return
    if not rows:
        print(json.dumps({"skipped": True}))
        return
    try:
        import numpy as np
        plt = _mpl()
        t = np.array([float(r["t"]) for r in rows])
        rd = np.array([float(r["ripple_dynamic"]) for r in rows])
        fig, ax = plt.subplots(figsize=(5,3))
        ax.scatter(t, rd, s=8, alpha=0.6)
        ax.set_xlabel("t (s)"); ax.set_ylabel("ripple_dynamic")
        ax.set_title("Dynamic Ripple vs Time")
        fig.tight_layout(); fig.savefig(args.out, dpi=150); plt.close(fig)
        print(json.dumps({"wrote": args.out}))
    except Exception as e:
        print(json.dumps({"skipped": True, "reason": str(e)}))


if __name__ == "__main__":
    main()
