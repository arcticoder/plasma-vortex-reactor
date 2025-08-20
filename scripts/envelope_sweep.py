#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.metrics import antiproton_yield_estimator, total_fom


def compute_fom(n_cm3: float, Te_eV: float) -> float:
    # Use physics model yield and proxy energy to get FOM
    y = antiproton_yield_estimator(n_cm3, Te_eV, {"model": "physics"})
    E_total = 1e11  # fixed proxy energy for envelope comparison
    return float(total_fom(y, E_total))


from typing import Any, Dict, List


def _frontier_topk(grid: List[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
    if k <= 0:
        return []
    return sorted(grid, key=lambda r: float(r.get("fom", 0.0)), reverse=True)[:k]


def main() -> None:
    ap = argparse.ArgumentParser(description="Operating envelope sweep: density vs temperature vs FOM")
    ap.add_argument("--n-points", type=int, default=20)
    ap.add_argument("--n-min", type=float, default=1e19)
    ap.add_argument("--n-max", type=float, default=1e21)
    ap.add_argument("--t-min", type=float, default=5.0)
    ap.add_argument("--t-max", type=float, default=50.0)
    # Tests expect JSON/CSV in CWD by default
    ap.add_argument("--out-json", default="operating_envelope.json")
    ap.add_argument("--out-csv", default="operating_envelope.csv")
    ap.add_argument("--out-png", default="operating_envelope.png")
    ap.add_argument("--seed", type=int, default=42, help="Seed for any stochastic models")
    ap.add_argument("--top-k", type=int, default=20, help="Emit top-k frontier JSON")
    ap.add_argument("--frontier-json", default="artifacts/operating_envelope_frontier.json")
    args = ap.parse_args()

    import numpy as np
    np.random.seed(int(args.seed))
    ns = np.geomspace(float(args.n_min), float(args.n_max), int(args.n_points))
    Ts = np.linspace(float(args.t_min), float(args.t_max), int(args.n_points))
    grid: List[Dict[str, Any]] = []
    for n in ns:
        for T in Ts:
            f = compute_fom(float(n), float(T))
            grid.append({"n_cm3": float(n), "Te_eV": float(T), "fom": float(f)})

    # Save JSON and CSV
    Path(Path(args.out_json).parent).mkdir(parents=True, exist_ok=True)
    Path(Path(args.out_csv).parent).mkdir(parents=True, exist_ok=True)
    Path(Path(args.frontier_json).parent).mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps({"grid": grid, "n_points": int(args.n_points)}))
    frontier = _frontier_topk(grid, int(args.top_k))
    Path(args.frontier_json).write_text(json.dumps({"frontier": frontier, "k": int(args.top_k)}))
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n_cm3", "Te_eV", "fom"])
        for row in grid:
            w.writerow([row["n_cm3"], row["Te_eV"], row["fom"]])

    # Plot
    try:
        import numpy as np

        from reactor.plotting import _mpl
        plt = _mpl()
        fig, ax = plt.subplots(figsize=(6,4))
        # contour plot of FOM over n, T
        N = np.array([r["n_cm3"] for r in grid])
        T = np.array([r["Te_eV"] for r in grid])
        F = np.array([r["fom"] for r in grid])
        # reshape into square if possible, else scatter-color
        k = int(args.n_points)
        if len(grid) == k*k:
            N2 = N.reshape(k,k)
            T2 = T.reshape(k,k)
            F2 = F.reshape(k,k)
            cs = ax.contourf(N2, T2, F2, levels=12, cmap="viridis")
            fig.colorbar(cs, ax=ax, label="FOM")
        else:
            sc = ax.scatter(N, T, c=F, cmap="viridis")
            fig.colorbar(sc, ax=ax, label="FOM")
        # highlight frontier points if any
        if frontier:
            NF = np.array([r["n_cm3"] for r in frontier])
            TF = np.array([r["Te_eV"] for r in frontier])
            ax.scatter(NF, TF, facecolors='none', edgecolors='red', s=60, label='frontier')
            ax.legend(loc='best')
        ax.set_xscale("log")
        ax.set_xlabel("Density n (cm^-3)")
        ax.set_ylabel("Temperature T (eV)")
        ax.set_title("Operating Envelope: FOM vs n,T")
        fig.tight_layout()
        Path(Path(args.out_png).parent).mkdir(parents=True, exist_ok=True)
        fig.savefig(args.out_png, dpi=150)
        plt.close(fig)
    except Exception:
        # plotting optional
        pass
    print(json.dumps({"ok": True, "out": [args.out_json, args.out_csv, args.out_png, args.frontier_json]}))


if __name__ == "__main__":
    main()
