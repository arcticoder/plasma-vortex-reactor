#!/usr/bin/env python
from __future__ import annotations

import argparse
import json


def _flat(d, prefix=""):
    out = {}
    for k, v in (d or {}).items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(_flat(v, prefix=key))
        else:
            out[key] = v
    return out


def main():
    ap = argparse.ArgumentParser(description="Compare two feasibility reports and print deltas")
    ap.add_argument("a")
    ap.add_argument("b")
    args = ap.parse_args()
    A = json.loads(open(args.a, "r", encoding="utf-8").read())
    B = json.loads(open(args.b, "r", encoding="utf-8").read())
    fa = _flat(A)
    fb = _flat(B)
    keys = sorted(set(list(fa.keys()) + list(fb.keys())))
    deltas = {}
    for k in keys:
        if fa.get(k) != fb.get(k):
            deltas[k] = {"a": fa.get(k), "b": fb.get(k)}
    print(json.dumps({"deltas": deltas, "counts": {"changed": len(deltas), "total": len(keys)}}))


if __name__ == "__main__":
    main()
