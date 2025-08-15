from __future__ import annotations
import json
from typing import Optional, Dict, Any, MutableMapping


def append_event(path: str, event: str, status: str = "info", details: Optional[Dict[str, Any]] = None) -> None:
    rec: Dict[str, Any] = {"event": event, "status": status}
    if details is not None:
        rec["details"] = dict(details)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
