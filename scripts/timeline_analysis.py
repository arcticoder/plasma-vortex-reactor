#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def _analyze(path: Path) -> Dict[str, Any]:
    stats: Dict[str, Any] = {
        "events": 0,
        "by_event": {},
        "by_status": {},
    }
    if not path.exists():
        return stats
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            stats["events"] += 1
            ev = str(rec.get("event") or rec.get("category") or "").strip() or "(unknown)"
            st = str(rec.get("status") or rec.get("details", {}).get("severity") or "").strip() or "(none)"
            stats["by_event"][ev] = int(stats["by_event"].get(ev, 0)) + 1
            stats["by_status"][st] = int(stats["by_status"].get(st, 0)) + 1
    except Exception:
        pass
    return stats


def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze timeline NDJSON and emit aggregate stats")
    ap.add_argument("--timeline", default="timeline_anomalies.ndjson")
    ap.add_argument("--out", default="timeline_stats.json")
    args = ap.parse_args()
    stats = _analyze(Path(args.timeline))
    Path(args.out).write_text(json.dumps(stats, indent=2))
    print(json.dumps({"wrote": args.out, "events": stats.get("events", 0)}))


if __name__ == "__main__":
    main()
