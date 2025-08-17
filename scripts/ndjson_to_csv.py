#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert JSONLines/NDJSON to CSV (flat keys)")
    ap.add_argument("--in", dest="inp", default="timeline.ndjson")
    ap.add_argument("--out", dest="out", default="timeline.csv")
    args = ap.parse_args()
    p = Path(args.inp)
    rows: List[Dict[str, Any]] = []
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # flatten one level of details if present
                det = obj.pop("details", None)
                if isinstance(det, dict):
                    for k, v in det.items():
                        obj[f"details.{k}"] = v
                rows.append(obj)
            except Exception:
                continue
    # collect headers
    headers: List[str] = []
    for r in rows:
        for k in r.keys():
            if k not in headers:
                headers.append(k)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(json.dumps({"wrote": args.out, "rows": len(rows)}))


if __name__ == "__main__":
    main()
