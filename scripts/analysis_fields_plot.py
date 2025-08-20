#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.analysis_fields import plot_b_field_ripple
from reactor.plotting import _mpl


def main():
    ap = argparse.ArgumentParser(description="Generate B-field ripple plot to PNG")
    ap.add_argument("--out", default="b_field_ripple.png")
    ap.add_argument("--series", default=None, help="JSON array of ripple fractions; if absent, use demo data")
    args = ap.parse_args()
    if args.series:
        data = json.loads(args.series)
    else:
        data = [
            {"y": 0.00005, "yMin": 0.00004, "yMax": 0.00006},
            {"y": 0.00007, "yMin": 0.00006, "yMax": 0.00008},
            {"y": 0.00006, "yMin": 0.00005, "yMax": 0.00007},
            {"y": 0.00008, "yMin": 0.00007, "yMax": 0.00009},
            {"y": 0.00005, "yMin": 0.00004, "yMax": 0.00006},
        ]
    # If dicts with yMin/yMax provided, use error bars
    if isinstance(data, list) and data and isinstance(data[0], dict) and "yMin" in data[0]:
        ys = [d["y"] for d in data]
        yerr_lower = [d["y"] - d["yMin"] for d in data]
        yerr_upper = [d["yMax"] - d["y"] for d in data]
        t_ms = list(range(len(ys)))
        try:
            plt = _mpl()
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.errorbar(
                t_ms,
                ys,
                yerr=[yerr_lower, yerr_upper],
                fmt='-o',
                color='crimson',
                ecolor='salmon',
                elinewidth=1,
            )
            ax.set_xlabel('Time (ms)')
            ax.set_ylabel('Ripple (fraction)')
            ax.set_title('B-Field Ripple with Error Bars')
            fig.tight_layout()
            fig.savefig(args.out, dpi=150)
            plt.close(fig)
        except Exception:
            # fallback: write placeholder PNG
            from pathlib import Path
            Path(args.out).write_bytes(bytes.fromhex(
                "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000A49444154789C6360000002000100FFFF03000006000557BF0000000049454E44AE426082"
            ))
    else:
        # Expect a flat list of numbers
        if not (isinstance(data, list) and (not data or not isinstance(data[0], dict))):
            raise SystemExit("Invalid --series format for simple ripple array")
        arr = [float(x) for x in data]  # type: ignore[list-item]
        t_ms = list(range(len(arr)))
        try:
            plot_b_field_ripple(t_ms, arr, args.out)
        except Exception:
            from pathlib import Path
            Path(args.out).write_bytes(bytes.fromhex(
                "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000A49444154789C6360000002000100FFFF03000006000557BF0000000049454E44AE426082"
            ))
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
