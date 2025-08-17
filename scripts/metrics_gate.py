#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Check feasibility_gates_report.json against metrics.json gates"
        )
    )
    ap.add_argument("--metrics", default="metrics.json")
    ap.add_argument("--report", default="feasibility_gates_report.json")
    ap.add_argument(
        "--require-yield",
        action="store_true",
        help="Also require antiproton_yield_pass=true in the report",
    )
    ap.add_argument(
        "--scenario",
        default=None,
        help="Optional scenario path or name to enable scenario-specific gates (e.g., high-load)",
    )
    args = ap.parse_args()
    try:
        with open(args.metrics, "r", encoding="utf-8") as f:
            metrics = json.load(f)
    except Exception as e:
        print(json.dumps({"gate": "feasibility", "ok": False, "error": f"metrics load failed: {e}"}))
        sys.exit(2)
    try:
        with open(args.report, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            rep = json.loads(txt)
    except Exception as e:
        print(json.dumps({"gate": "feasibility", "ok": False, "error": f"report load failed: {e}", "path": args.report}))
        sys.exit(2)
    # simple gate: require stable true when present
    ok = True
    reasons = []
    if not rep.get("stable", False):
        ok = False
        reasons.append("unstable")
    # optional specific checks
    gthr = metrics.get("gamma_min", None)
    if gthr is not None and rep.get("gamma_stats"):
        if rep["gamma_stats"].get("gamma_max", 0.0) < float(gthr):
            ok = False
            reasons.append(f"gamma_max<{gthr}")
    # optional yield gate
    if args.require_yield:
        if not rep.get("antiproton_yield_pass", False):
            ok = False
            reasons.append("yield_gate_fail")

    # High-load branch: require FOM >= 0.1 and include reason breakdown
    if args.scenario and ("high_load" in args.scenario or "production" in args.scenario):
        fom = rep.get("fom", None)
        if fom is None and isinstance(rep.get("fom_details"), dict):
            fom = rep["fom_details"].get("fom")
        if fom is not None and float(fom) < 0.1:
            ok = False
            reasons.append("fom<0.1")

    if not ok:
        print(json.dumps({"gate": "feasibility", "ok": False, "reasons": reasons}))
        sys.exit(2)
    print(json.dumps({"gate": "feasibility", "ok": True}))


if __name__ == "__main__":
    main()
