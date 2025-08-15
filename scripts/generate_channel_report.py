#!/usr/bin/env python
from __future__ import annotations
import argparse
from reactor.energy import EnergyLedger


def main():
    ap = argparse.ArgumentParser(description="Generate a channel_report.json from example channel allocations")
    ap.add_argument("--out", default="channel_report.json")
    ap.add_argument("--duration", type=float, default=1.0, help="Interval length in seconds for each sample")
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
    L.write_channel_report(args.out)


if __name__ == "__main__":
    main()
