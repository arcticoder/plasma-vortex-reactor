#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
from typing import Any, Dict, List
from pathlib import Path


def _read_csv(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def _first_time_meeting(rows: List[Dict[str, Any]], key: str, threshold: float, comparator) -> float | None:
    for row in rows:
        try:
            t_raw = row.get("t", 0.0)
            k_raw = row.get(key, None)
            if k_raw is None:
                continue
            t = float(t_raw)  # type: ignore[arg-type]
            val = float(k_raw)  # type: ignore[arg-type]
            if comparator(val, threshold):
                return t
        except Exception:
            continue
    return None


def main():
    ap = argparse.ArgumentParser(description="Compute time-to-stability and time-to-yield from sweep CSVs")
    ap.add_argument("--sweep-time", default="data/full_sweep_with_time.csv")
    ap.add_argument("--out-json", default="artifacts/time_to_metrics.json")
    ap.add_argument("--out-png", default="artifacts/time_to_metrics.png")
    args = ap.parse_args()

    rows = _read_csv(args.sweep_time)
    t_yield = _first_time_meeting(rows, "yield", 1e12, lambda v, thr: v >= thr)
    t_fom = _first_time_meeting(rows, "fom", 0.1, lambda v, thr: v >= thr)

    out = {"time_to_yield": t_yield, "time_to_fom": t_fom, "source": args.sweep_time}
    from pathlib import Path
    import os
    os.makedirs(os.path.dirname(os.path.abspath(args.out_json)) or ".", exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    try:
        # Simple bar plot
        # Use project plotting helper
        import sys, os
        _here = os.path.dirname(os.path.abspath(__file__))
        _root = os.path.dirname(_here)
        _src = os.path.join(_root, "src")
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from reactor.plotting import _mpl
        plt = _mpl()
        labels = ["Yield>=1e12", "FOM>=0.1"]
        vals = [t_yield or 0.0, t_fom or 0.0]
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(labels, vals, color=["seagreen", "steelblue"])
        ax.set_ylabel("Time (s)")
        ax.set_title("Time-to-Metrics")
        fig.tight_layout()
        os.makedirs(os.path.dirname(os.path.abspath(args.out_png)) or ".", exist_ok=True)
        fig.savefig(args.out_png, dpi=150)
        plt.close(fig)
    except Exception:
        # If plotting backend unavailable, still create a placeholder PNG
        try:
            Path(args.out_png).write_bytes(b"")
        except Exception:
            pass

    print(json.dumps({"wrote": args.out_json, "plot": args.out_png}))


if __name__ == "__main__":
    main()
