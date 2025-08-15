#!/usr/bin/env python
from __future__ import annotations

import argparse
import json


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Generate a simple gate summary markdown from feasibility report"
        )
    )
    ap.add_argument("--report", default="feasibility_gates_report.json")
    ap.add_argument("--out", default="gate_summary.md")
    args = ap.parse_args()
    rep = json.loads(open(args.report, "r", encoding="utf-8").read())
    lines = ["# Feasibility Gate Summary", "", f"- Stable: {'✅' if rep.get('stable') else '❌'}",
             f"- Gamma OK: {'✅' if rep.get('gamma_ok') else '❌'}",
             f"- B-field OK: {'✅' if rep.get('b_ok') else '❌'}",
             f"- Density OK: {'✅' if rep.get('dens_ok') else '❌'}"]
    open(args.out, "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
