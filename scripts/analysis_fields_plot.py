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


def main():
    ap = argparse.ArgumentParser(description="Generate B-field ripple plot to PNG")
    ap.add_argument("--out", default="b_field_ripple.png")
    ap.add_argument("--series", default=None, help="JSON array of ripple fractions; if absent, use demo data")
    args = ap.parse_args()
    if args.series:
        arr = json.loads(args.series)
    else:
        arr = [0.00005, 0.00007, 0.00006, 0.00008, 0.00005]
    t_ms = [i for i in range(len(arr))]
    plot_b_field_ripple(t_ms, arr, args.out)
    print(json.dumps({"wrote": args.out}))


if __name__ == "__main__":
    main()
