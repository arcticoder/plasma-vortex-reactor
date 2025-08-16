#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os, sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.plotting import _mpl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-json", default=None, help="Path to hardware metrics JSON (list of {t_ms, i}) or timeline NDJSON extract")
    ap.add_argument("--out", default="hardware_metrics.png")
    ap.add_argument("--high-load", action="store_true", help="Render a high-load variant (synthetic if no JSON)")
    ap.add_argument("--anomaly-threshold", type=float, default=1.3, help="Flag metric values above this threshold as anomalies")
    args = ap.parse_args()

    data = []
    if args.in_json and os.path.exists(args.in_json):
        # Accept either JSON list or NDJSON timeline with details.i
        txt = open(args.in_json, "r", encoding="utf-8").read().strip()
        if txt.startswith("["):
            data = json.loads(txt)
        else:
            # NDJSON: parse lines with details.i or details.t_ms
            data = []
            for line in txt.splitlines():
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                det = rec.get("details") or {}
                if "i" in det or "t_ms" in det:
                    data.append({"t_ms": det.get("t_ms"), "i": det.get("i")})
    else:
        # Fallback demo data
        if args.high_load:
            # Slightly elevated and more variable metric to represent high-load conditions
            vals = [1.0, 1.25, 1.35, 1.3, 1.2, 1.15, 1.1]
        else:
            vals = [1.0, 1.1, 1.2, 1.1, 1.0]
        data = [{"t_ms": i, "i": v} for i, v in enumerate(vals)]

    t_ms = [d.get("t_ms", i) for i, d in enumerate(data)]
    i_vals = [d.get("i", 0.0) for d in data]

    plt = _mpl()
    fig, ax = plt.subplots(figsize=(5,4))
    ax.plot(t_ms, i_vals, color="crimson")
    # Mark anomalies
    anomalies = [(t, v) for t, v in zip(t_ms, i_vals) if v is not None and float(v) >= args.anomaly_threshold]
    if anomalies:
        ax.scatter([t for t, _ in anomalies], [v for _, v in anomalies], color="orange", s=20, label="anomaly")
        ax.legend(loc="best")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Hardware Metric (i)")
    ax.set_title("Hardware State vs Time" + (" (High Load)" if args.high_load else ""))
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    plt.close(fig)
    print(json.dumps({"wrote": args.out, "anomalies": len(anomalies)}))


if __name__ == "__main__":
    main()
