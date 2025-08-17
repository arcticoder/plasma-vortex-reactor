#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random


def main():
    ap = argparse.ArgumentParser(description="Generate synthetic timeline anomalies in NDJSON")
    ap.add_argument("--out", default="timeline_anomalies.ndjson")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--scenario-id", default="ci-demo")
    args = ap.parse_args()
    rnd = random.Random(args.seed)
    kinds = [
        ("hardware_timeout", "fail"),
        ("stability_drop", "warn"),
        ("cooldown", "ok"),
        ("overrun", "fail"),
        ("density_dip", "warn"),
    ]
    lines = []
    for i in range(args.n):
        ev, status = rnd.choice(kinds)
    details = {"i": i, "seed": args.seed, "severity": status, "scenario_id": args.scenario_id}
    lines.append(json.dumps({"event": ev, "status": status, "scenario_id": args.scenario_id, "details": details}))
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text("\n".join(lines) + "\n")
    print(json.dumps({"wrote": args.out, "n": args.n}))


if __name__ == "__main__":
    main()
