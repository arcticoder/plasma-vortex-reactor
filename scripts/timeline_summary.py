#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from reactor.logging_utils import summarize_timeline


def main():
    ap = argparse.ArgumentParser(description="Summarize a timeline NDJSON file")
    ap.add_argument("--timeline", default="timeline.ndjson")
    ap.add_argument("--out", default="timeline_summary.json")
    args = ap.parse_args()
    payload = summarize_timeline(args.timeline)
    # compute perf percentiles if elapsed_s present in timeline details
    try:
        vals = []
        with open(args.timeline, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                det = rec.get("details", {}) or {}
                if "elapsed_s" in det:
                    vals.append(float(det["elapsed_s"]))
        if vals:
            vals_sorted = sorted(vals)
            def pct(p: float) -> float:
                if not vals_sorted:
                    return 0.0
                k = min(
                    len(vals_sorted) - 1,
                    max(0, int(round((p / 100.0) * (len(vals_sorted) - 1)))),
                )
                return float(vals_sorted[k])
            payload["perf_percentiles"] = {"p50": pct(50), "p90": pct(90), "p99": pct(99)}
            payload["perf_count"] = len(vals_sorted)
    except Exception:
        pass
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
