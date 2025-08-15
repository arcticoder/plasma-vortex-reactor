#!/usr/bin/env python
from __future__ import annotations

import argparse
import json


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Merge feasibility, gate summary md, and "
            "timeline summary into run_report.json"
        )
    )
    ap.add_argument("--feasibility", default="feasibility_gates_report.json")
    ap.add_argument("--gate-md", default="gate_summary.md")
    ap.add_argument("--timeline-summary", default="timeline_summary.json")
    ap.add_argument("--out", default="run_report.json")
    args = ap.parse_args()
    data = {}
    try:
        with open(args.feasibility, "r", encoding="utf-8") as f:
            data["feasibility"] = json.load(f)
    except Exception:
        data["feasibility"] = {"error": f"missing: {args.feasibility}"}
    try:
        with open(args.timeline_summary, "r", encoding="utf-8") as f:
            data["timeline_summary"] = json.load(f)
    except Exception:
        data["timeline_summary"] = {"error": f"missing: {args.timeline_summary}"}
    try:
        # embed markdown as text
        data["gate_summary_md"] = open(args.gate_md, "r", encoding="utf-8").read()
    except Exception:
        data["gate_summary_md"] = f"missing: {args.gate_md}"
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
