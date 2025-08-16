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

from reactor.metrics import antiproton_yield_estimator, total_fom
from reactor.uq import run_uq_sampling


def main():
    ap = argparse.ArgumentParser(description="Optimize targets via UQ sampling and save JSON")
    ap.add_argument("--samples", type=int, default=20)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--out", default="uq_optimized.json")
    args = ap.parse_args()

    def eval_fn(params):
        y = antiproton_yield_estimator(params["n_e"], params["T_e"], {"model": "physics"})
        E_total = params["E_total"]
        f = total_fom(y, E_total)
        return {"yield": y, "fom": f, "energy": E_total}

    out = run_uq_sampling(
        n_samples=args.samples,
        seed=args.seed,
        param_ranges={
            "n_e": (1e19, 1e21),
            "T_e": (5.0, 15.0),
            "E_total": (1e10, 1e12),
        },
        eval_fn=eval_fn,
    )
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
