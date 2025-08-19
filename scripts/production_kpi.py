#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Tuple


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
    ap.add_argument("--anomalies-ndjson", default="docs/timeline_anomalies.ndjson", help="Optional anomalies NDJSON to adjust KPI for fail severities")
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
            denom = energy_cost_per_J * energy_budget
            # Only compute fallback FOM if inputs are valid and positive; otherwise leave None
            if denom and denom > 0.0 and price_per_antiproton > 0.0:
                fom = price_per_antiproton / denom
            else:
                fom = None
        except Exception:
            fom = None

    # Optional anomalies adjustment: count 'fail' severities to degrade stability and FOM
    def _count_fail(ndjson_path: str) -> Tuple[int, int, int]:
        ok = warn = fail = 0
        try:
            p = Path(ndjson_path)
            if p.exists():
                for line in p.read_text().splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    status = str(rec.get("status") or rec.get("details", {}).get("severity") or "").strip()
                    if status == "fail":
                        fail += 1
                    elif status == "warn":
                        warn += 1
                    elif status == "ok":
                        ok += 1
        except Exception:
            pass
        return ok, warn, fail

    ok_c, warn_c, fail_c = _count_fail(args.anomalies_ndjson)

    kpi = {
        "stable": bool(feas.get("stable", False)),
        "gamma_ok": bool(feas.get("gamma_ok", False)),
        "yield_pass": bool(feas.get("antiproton_yield_pass", False)),
        "fom": fom,
        "energy_budget_J": mets.get("energy_budget_J"),
        "uq_n_samples": uq.get("n_samples"),
        "uq_means": uq.get("means"),
        "cost_model_used": bool(cost_model),
        "anomaly_counts": {"ok": ok_c, "warn": warn_c, "fail": fail_c},
    }

    # Apply anomaly impact: if any fail anomalies, mark unstable and reduce FOM slightly
    if fail_c > 0:
        try:
            kpi["stable"] = False
            if kpi["fom"] is not None:
                kpi["fom"] = float(kpi["fom"]) * 0.9
        except Exception:
            pass

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(kpi, f, indent=2)
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
