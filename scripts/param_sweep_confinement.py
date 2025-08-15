#!/usr/bin/env python
from __future__ import annotations
import argparse
import csv
from reactor.metrics import confinement_efficiency_estimator


def main():
    ap = argparse.ArgumentParser(description="Param sweep for confinement efficiency over xi and B-field ripple")
    ap.add_argument("--xi-min", type=float, default=0.5)
    ap.add_argument("--xi-max", type=float, default=5.0)
    ap.add_argument("--xi-steps", type=int, default=10)
    ap.add_argument("--ripple-min", type=float, default=0.0)
    ap.add_argument("--ripple-max", type=float, default=0.02)
    ap.add_argument("--ripple-steps", type=int, default=10)
    ap.add_argument("--out", default="confinement_sweep.csv")
    args = ap.parse_args()

    xi_vals = [args.xi_min + i*(args.xi_max-args.xi_min)/max(args.xi_steps-1,1) for i in range(args.xi_steps)]
    ripple_vals = [args.ripple_min + j*(args.ripple_max-args.ripple_min)/max(args.ripple_steps-1,1) for j in range(args.ripple_steps)]

    with open(args.out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["xi", "b_field_ripple_pct", "efficiency"])
        for xi in xi_vals:
            for rp in ripple_vals:
                eff = confinement_efficiency_estimator(xi, rp)
                w.writerow([xi, rp, eff])


if __name__ == "__main__":
    main()
