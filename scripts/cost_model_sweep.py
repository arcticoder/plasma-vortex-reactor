#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import List

import os, sys
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.metrics import total_fom, antiproton_yield_estimator
from reactor.plotting import _mpl


def main() -> None:
    ap = argparse.ArgumentParser(description="Sweep energy cost and price to study KPI sensitivity")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--cost-min", type=float, default=1e-10)
    ap.add_argument("--cost-max", type=float, default=1e-6)
    ap.add_argument("--price-min", type=float, default=1e-5)
    ap.add_argument("--price-max", type=float, default=1e-1)
    ap.add_argument("--out-json", default="cost_sweep.json")
    ap.add_argument("--out-csv", default="cost_sweep.csv")
    ap.add_argument("--out-png", default="cost_sweep.png")
    args = ap.parse_args()

    import numpy as np
    costs = np.geomspace(max(args.cost_min, 1e-12), max(args.cost_max, args.cost_min+1e-12), args.n)
    prices = np.geomspace(max(args.price_min, 1e-12), max(args.price_max, args.price_min+1e-12), args.n)
    # fixed physics point for comparability
    y_base = antiproton_yield_estimator(1e21, 20.0, {"model": "physics"})
    E_total = 1e10
    rows: List[dict] = []
    for c in costs:
        for p in prices:
            fom = total_fom(y_base * p, E_total * (1.0 + c))
            rows.append({"energy_cost_J": float(c), "price_scale": float(p), "fom": float(fom)})

    # write JSON and CSV
    Path(args.out_json).write_text(json.dumps({"n": len(rows), "rows": rows}))
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["energy_cost_J", "price_scale", "fom"])
        w.writeheader(); w.writerows(rows)

    # plot heatmap-like scatter
    plt = _mpl(); import numpy as np
    fig, ax = plt.subplots(figsize=(5,4))
    cax = ax.scatter([r["energy_cost_J"] for r in rows], [r["price_scale"] for r in rows], c=[r["fom"] for r in rows], cmap="viridis")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Energy Cost Proxy (J)")
    ax.set_ylabel("Price Scale")
    ax.set_title("FOM vs Cost and Price")
    fig.colorbar(cax, ax=ax, label="FOM")
    fig.tight_layout(); fig.savefig(args.out_png, dpi=150); plt.close(fig)


if __name__ == "__main__":
    main()
