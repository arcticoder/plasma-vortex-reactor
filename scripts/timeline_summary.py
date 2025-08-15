#!/usr/bin/env python
from __future__ import annotations
import argparse, json
from reactor.logging_utils import summarize_timeline


def main():
    ap = argparse.ArgumentParser(description="Summarize a timeline NDJSON file")
    ap.add_argument("--timeline", default="timeline.ndjson")
    ap.add_argument("--out", default="timeline_summary.json")
    args = ap.parse_args()
    payload = summarize_timeline(args.timeline)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
