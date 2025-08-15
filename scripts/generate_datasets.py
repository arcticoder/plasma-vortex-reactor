#!/usr/bin/env python
from __future__ import annotations
import argparse, json
import numpy as np


def main():
    ap = argparse.ArgumentParser(description="Generate tiny synthetic datasets for gamma, b-field, and E_mag")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--outdir", default="datasets")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    gamma = list(140 + 20*rng.random(args.n))
    b = list(5.0 * (1.0 + 0.005*rng.standard_normal(args.n)))
    E = list(rng.random(args.n))
    open(f"{args.outdir}/gamma_series.json", "w").write(json.dumps(gamma))
    open(f"{args.outdir}/b_field_series.json", "w").write(json.dumps(b))
    open(f"{args.outdir}/E_mag.json", "w").write(json.dumps(E))


if __name__ == "__main__":
    main()
