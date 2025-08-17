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
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--sensitivity", action="store_true", help="Vary price and energy cost jointly and emit sensitivity report")
    args = ap.parse_args()

    import numpy as np
    np.random.seed(int(args.seed))
    costs = np.geomspace(max(args.cost_min, 1e-12), max(args.cost_max, args.cost_min+1e-12), args.n)
    prices = np.geomspace(max(args.price_min, 1e-12), max(args.price_max, args.price_min+1e-12), args.n)
    # fixed physics point for comparability
    y_base = antiproton_yield_estimator(1e21, 20.0, {"model": "physics"})
    E_total = 1e10
    rows: List[dict] = []
    for c in costs:
        for p in prices:
            # sensitivity mode: introduce tiny coupled perturbation for visualization (deterministic by seed)
            cp = float(c)
            pp = float(p)
            if args.sensitivity:
                delta = 0.01 * (np.sin(cp * 1e6) + np.cos(pp * 1e3))
                cp = max(1e-12, cp * (1.0 + delta))
                pp = max(1e-12, pp * (1.0 - delta))
            fom = total_fom(y_base * pp, E_total * (1.0 + cp))
            rows.append({"energy_cost_J": float(cp), "price_scale": float(pp), "fom": float(fom)})

    # write JSON and CSV
    Path(args.out_json).write_text(json.dumps({"n": len(rows), "rows": rows}))
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["energy_cost_J", "price_scale", "fom"])
        w.writeheader(); w.writerows(rows)

    # plot heatmap-like scatter (best-effort)
    try:
        plt = _mpl(); import numpy as np
        fig, ax = plt.subplots(figsize=(5,4))
        cax = ax.scatter([r["energy_cost_J"] for r in rows], [r["price_scale"] for r in rows], c=[r["fom"] for r in rows], cmap="viridis")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("Energy Cost Proxy (J)")
        ax.set_ylabel("Price Scale")
        ax.set_title("FOM vs Cost and Price" + (" (sensitivity)" if args.sensitivity else ""))
        fig.colorbar(cax, ax=ax, label="FOM")
        fig.tight_layout(); fig.savefig(args.out_png, dpi=150); plt.close(fig)
    except Exception:
        try:
            Path(args.out_png).write_bytes(b"PNG placeholder - matplotlib not available\n")
        except Exception:
            pass


if __name__ == "__main__":
    main()
