#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def _read(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"_missing": True, "path": path}


def main():
    ap = argparse.ArgumentParser(description="Emit KPI summary for production readiness")
    ap.add_argument("--feasibility", default="feasibility_gates_report.json")
    ap.add_argument("--metrics", default="metrics.json")
    ap.add_argument("--uq", default="uq_optimized.json")
    ap.add_argument("--cost-model", default="configs/cost_model.json", help="Optional cost model JSON for FOM calculation")
    ap.add_argument("--out", default="production_kpi.json")
    args = ap.parse_args()

    feas = _read(args.feasibility)
    mets = _read(args.metrics)
    uq = _read(args.uq)

    # Optional cost model
    cost_model: Dict[str, Any] = {}
    try:
        p = Path(args.cost_model)
        if p.exists():
            cost_model = json.loads(p.read_text())
    except Exception:
        cost_model = {}

    # Derive FOM: prefer feasibility report; otherwise a simple ratio from cost_model and metrics
    fom = feas.get("fom") or (feas.get("fom_details") or {}).get("fom")
    if fom is None and cost_model:
        try:
            price_per_antiproton = float(cost_model.get("price_per_antiproton", 0.0) or 0.0)
            energy_cost_per_J = float(cost_model.get("energy_cost_per_J", 0.0) or 0.0)
            energy_budget = float(mets.get("energy_budget_J", 0.0) or 0.0)
            denom = max(energy_cost_per_J * energy_budget, 1e-12)
            fom = price_per_antiproton / denom
        except Exception:
            fom = None

    kpi = {
        "stable": bool(feas.get("stable", False)),
        "gamma_ok": bool(feas.get("gamma_ok", False)),
        "yield_pass": bool(feas.get("antiproton_yield_pass", False)),
        "fom": fom,
        "energy_budget_J": mets.get("energy_budget_J"),
        "uq_n_samples": uq.get("n_samples"),
        "uq_means": uq.get("means"),
        "cost_model_used": bool(cost_model),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(kpi, f, indent=2)
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
