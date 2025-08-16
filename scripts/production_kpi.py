#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
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
    ap.add_argument("--out", default="production_kpi.json")
    args = ap.parse_args()

    feas = _read(args.feasibility)
    mets = _read(args.metrics)
    uq = _read(args.uq)

    kpi = {
        "stable": bool(feas.get("stable", False)),
        "gamma_ok": bool(feas.get("gamma_ok", False)),
        "yield_pass": bool(feas.get("antiproton_yield_pass", False)),
        "fom": feas.get("fom") or (feas.get("fom_details") or {}).get("fom"),
        "energy_budget_J": mets.get("energy_budget_J"),
        "uq_n_samples": uq.get("n_samples"),
        "uq_means": uq.get("means"),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(kpi, f, indent=2)
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
