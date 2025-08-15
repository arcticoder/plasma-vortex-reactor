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
    args = ap.parse_args()
    with open(args.metrics, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    with open(args.report, "r", encoding="utf-8") as f:
        rep = json.load(f)
    # simple gate: require stable true when present
    ok = True
    if not rep.get("stable", False):
        ok = False
    # optional specific checks
    gthr = metrics.get("gamma_min", None)
    if gthr is not None and rep.get("gamma_stats"):
        if rep["gamma_stats"].get("gamma_max", 0.0) < float(gthr):
            ok = False
    if not ok:
        print(json.dumps({"gate": "feasibility", "ok": False}))
        sys.exit(2)
    print(json.dumps({"gate": "feasibility", "ok": True}))


if __name__ == "__main__":
    main()
