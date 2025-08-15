#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv

from reactor.uq import run_uq_sampling, save_results


def main():
    ap = argparse.ArgumentParser(description="Run a tiny UQ demo and save results")
    ap.add_argument("--samples", type=int, default=20)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--out-json", default="uq_results.json")
    ap.add_argument("--out-csv", default="uq_results.csv")
    args = ap.parse_args()

    def eval_fn(params):
        # trivial score: linear combination
        return {"score": 2*params["a"] + params["b"]}

    out = run_uq_sampling(
        args.samples,
        args.seed,
        param_ranges={"a": (0, 1), "b": (0, 1)},
        eval_fn=eval_fn,
    )
    save_results(args.out_json, out)
    # Write CSV of results
    rows = out.get("results", [])
    if rows:
        with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=sorted(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow(r)


if __name__ == "__main__":
    main()
