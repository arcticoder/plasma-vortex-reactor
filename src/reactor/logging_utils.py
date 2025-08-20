from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def append_event(
    path: str,
    event: str,
    status: str = "info",
    details: Optional[Dict[str, Any]] = None,
    code: Optional[str] = None,
) -> None:
    rec: Dict[str, Any] = {
        "event": event,
        "status": status,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    if details is not None:
        rec["details"] = dict(details)
    if code is not None:
        rec["code"] = str(code)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def summarize_timeline(path: str) -> Dict[str, Any]:
    """Summarize a timeline NDJSON file.

    Returns counts per event and first/last timestamps if present,
    and simple min/max for common details.
    """
    import math
    counts: Dict[str, int] = {}
    first_ts = None
    last_ts = None
    wmax_min = math.inf
    wmax_max = -math.inf
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                ev = rec.get("event", "?")
                counts[ev] = counts.get(ev, 0) + 1
                ts = rec.get("ts")
                if ts and first_ts is None:
                    first_ts = ts
                if ts:
                    last_ts = ts
                det = rec.get("details", {}) or {}
                if "wmax" in det:
                    wmax = float(det["wmax"])  
                    wmax_min = min(wmax_min, wmax)
                    wmax_max = max(wmax_max, wmax)
    except FileNotFoundError:
        return {"error": "timeline not found", "path": path}
    return {
        "path": path,
        "counts": counts,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "wmax_min": None if wmax_min == math.inf else wmax_min,
        "wmax_max": None if wmax_max == -math.inf else wmax_max,
    }
