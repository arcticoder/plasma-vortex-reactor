#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot KPI trend from production_kpi*.json files")
    ap.add_argument("--glob", default="docs/production_kpi*.json")
    ap.add_argument("--out", default="kpi_trend.png")
    args = ap.parse_args()

    files: List[Path] = sorted(Path().glob(args.glob))
    if not files:
        # also include root production_kpi.json if present
        rp = Path("production_kpi.json")
        if rp.exists():
            files = [rp]
    xs: List[int] = []
    ys: List[float] = []
    for i, p in enumerate(files):
        try:
            data = json.loads(p.read_text())
            f = data.get("fom")
            if isinstance(f, (int, float)):
                xs.append(i)
                ys.append(float(f))
        except Exception:
            continue
    out = Path(args.out)
    if not xs:
        out.write_bytes(b"PNG placeholder - no KPI data\n")
        print("{}".format(json.dumps({"wrote": str(out), "n": 0})))
        return
    try:
        # best-effort plotting
        import sys as _sys
        s = Path(__file__).resolve().parents[1] / 'src'
        if str(s) not in _sys.path:
            _sys.path.insert(0, str(s))
        from reactor.plotting import _mpl  # type: ignore
        plt = _mpl()
        fig, ax = plt.subplots(figsize=(5,3))
        ax.plot(xs, ys, marker='o')
        ax.set_xlabel('Revision')
        ax.set_ylabel('FOM')
        ax.set_title('KPI Trend')
        fig.tight_layout(); fig.savefig(str(out), dpi=150); plt.close(fig)
    except Exception:
        out.write_bytes(b"PNG placeholder - matplotlib not available\n")
    print("{}".format(json.dumps({"wrote": str(out), "n": len(xs)})))


if __name__ == "__main__":
    main()
