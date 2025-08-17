#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def _read(path: str) -> Dict[str, Any]:
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}


def main() -> None:
    ap = argparse.ArgumentParser(description="Compute compact KPI diff vs baseline")
    ap.add_argument("--baseline", default="baseline_kpi.json")
    ap.add_argument("--current", default="production_kpi.json")
    ap.add_argument("--out", default="kpi_diff.json")
    args = ap.parse_args()
    base = _read(args.baseline)
    cur = _read(args.current)
    base_f = base.get("fom")
    cur_f = cur.get("fom")
    delta: float | None
    if isinstance(base_f, (int, float)) and isinstance(cur_f, (int, float)):
        delta = float(cur_f) - float(base_f)
    else:
        delta = None
    out = {
        "stable": {"baseline": base.get("stable"), "current": cur.get("stable")},
        "fom": {"baseline": base_f, "current": cur_f, "delta": delta},
        "energy_budget_J": {"baseline": base.get("energy_budget_J"), "current": cur.get("energy_budget_J")},
    }
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
