#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
from typing import Any, Dict, List


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
    # Optional integrated report inputs
    ap.add_argument("--uq", default="uq_optimized.json")
    ap.add_argument("--uq-production", default="uq_production.json")
    ap.add_argument("--sweep-time", default="data/full_sweep_with_time.csv")
    ap.add_argument("--sweep-dyn", default="data/full_sweep_with_dynamic_ripple.csv")
    ap.add_argument("--integrated-out", default="artifacts/integrated_report.json")
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

    # Write integrated_report.json (optional)
    def _read_json(path: str) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"_missing": True, "path": path}

    def _read_csv_head(path: str, limit: int = 200) -> Dict[str, Any]:
        def _try(p: str) -> Dict[str, Any] | None:
            try:
                rows: List[Dict[str, Any]] = []
                with open(p, newline="", encoding="utf-8") as f:
                    r = csv.DictReader(f)
                    for i, row in enumerate(r):
                        if i >= limit:
                            break
                        rows.append(row)
                return {"path": p, "rows": rows, "n_rows": i + 1 if rows else 0}
            except Exception:
                return None
        got = _try(path)
        if got is not None:
            return got
        # Fallback: if path is data/..., try CWD filename
        if path.startswith("data/"):
            alt = path[len("data/") :]
            got = _try(alt)
            if got is not None:
                return got
        return {"_missing": True, "path": path}

    integrated: Dict[str, Any] = {
        "feasibility": data.get("feasibility"),
        "run_report": data,
        "uq": _read_json(args.uq),
        "uq_production": _read_json(args.uq_production),
        "sweeps": {
            "time": _read_csv_head(args.sweep_time),
            "dynamic_ripple": _read_csv_head(args.sweep_dyn),
        },
    }
    with open(args.integrated_out, "w", encoding="utf-8") as f:
        json.dump(integrated, f, indent=2)
    print(json.dumps({"wrote": args.integrated_out}))


if __name__ == "__main__":
    main()
