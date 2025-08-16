#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import os, sys
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.plotting import _mpl


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot performance bench trend from JSONL")
    ap.add_argument("--in", dest="inp", default="bench_trend.jsonl")
    ap.add_argument("--out", default="bench_trend.png")
    args = ap.parse_args()
    p = Path(args.inp)
    if not p.exists():
        # no trend yet; emit empty placeholder
        Path(args.out).write_bytes(b"")
        return
    xs = []
    ys = []
    for line in p.read_text().splitlines():
        try:
            obj = json.loads(line)
            xs.append(obj.get("ts"))
            ys.append(float(obj.get("elapsed_s", 0.0)))
        except Exception:
            continue
    if not ys:
        Path(args.out).write_bytes(b"")
        return
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(6,3))
    ax.plot(range(len(ys)), ys, marker="o", color="teal")
    ax.set_xlabel("Run #")
    ax.set_ylabel("Elapsed (s)")
    ax.set_title("Bench Trend")
    fig.tight_layout(); fig.savefig(args.out, dpi=150); plt.close(fig)


if __name__ == "__main__":
    main()
