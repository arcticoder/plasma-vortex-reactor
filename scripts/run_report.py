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
    ap.add_argument("--channel-report", default="channel_report.json")
    ap.add_argument("--yield-report", default=None)
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
    # channel report merge
    try:
        with open(args.channel_report, "r", encoding="utf-8") as f:
            ch = json.load(f)
        data["channel_report"] = ch
        data["channel_fom_summary"] = {
            "total_fom": ch.get("total_fom"),
            "top_channels": sorted((ch.get("channel_fom") or {}).items(), key=lambda kv: kv[1], reverse=True)[:3],
        }
    except Exception:
        data["channel_report"] = {"error": f"missing: {args.channel_report}"}
    # yield report merge (if provided)
    if args.yield_report:
        try:
            with open(args.yield_report, "r", encoding="utf-8") as f:
                data["yield_report"] = json.load(f)
        except Exception:
            data["yield_report"] = {"error": f"missing: {args.yield_report}"}
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
