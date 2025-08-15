#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import sys

# Ensure repository sources are importable when running from scripts/ directly
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.energy import EnergyLedger
from reactor.energy import fom as _fom


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Generate a channel_report.json from example channel allocations"
        )
    )
    ap.add_argument("--out", default="channel_report.json")
    ap.add_argument(
        "--duration",
        type=float,
        default=1.0,
        help="Interval length in seconds for each sample",
    )
    args = ap.parse_args()

    L = EnergyLedger()
    # Example channel powers (Watts)
    channels = {
        "heaters": 500.0,
        "coils": 1200.0,
        "lasers": 300.0,
        "rf": 200.0,
    }
    for name, p in channels.items():
        L.add_channel_energy(name, power_w=p, dt_s=args.duration)
    # Compute simple FOM proxy per channel as inverse energy fraction proxy
    total = sum(L.channels().values()) or 1.0
    ch_fom = {k: float((total / max(v, 1e-12))) for k, v in L.channels().items()}
    payload = {
        "total_energy_J": L.total_energy(),
        "channels": L.channels(),
        "channel_fom": ch_fom,
        "total_fom": float(sum(ch_fom.values())),
    }
    import json as _json
    with open(args.out, "w", encoding="utf-8") as f:
        _json.dump(payload, f, indent=2)
    # Optional validate against schema if jsonschema is available
    try:
        import json  # type: ignore

        import jsonschema  # type: ignore

        with open(
            "docs/schemas/channel_report.schema.json", "r", encoding="utf-8"
        ) as f:
            schema = json.load(f)
        with open(args.out, "r", encoding="utf-8") as f:
            _payload = json.load(f)
        jsonschema.validate(instance=_payload, schema=schema)
    except Exception:
        pass


if __name__ == "__main__":
    main()
