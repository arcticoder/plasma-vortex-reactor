#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any


def main() -> None:
    ap = argparse.ArgumentParser(description="Dual-panel: envelope (FOM) + time-to-stability/yield overlay")
    ap.add_argument("--envelope", default="operating_envelope.json")
    ap.add_argument("--time-metrics", default="time_to_metrics.json")
    ap.add_argument("--out", default="envelope_dual_panel.png")
    args = ap.parse_args()

    try:
        env = json.loads(Path(args.envelope).read_text())
        grid = env.get("grid", [])
    except Exception:
        grid = []
    try:
        tm = json.loads(Path(args.time_metrics).read_text())
    except Exception:
        tm = {}
    # Build simple scatter coloring by FOM and overlay lines from time metrics
    try:
        from reactor.plotting import _mpl
        import numpy as np
        plt = _mpl()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        if grid:
            N = np.array([float(r.get("n_cm3", 0.0)) for r in grid])
            T = np.array([float(r.get("Te_eV", 0.0)) for r in grid])
            F = np.array([float(r.get("fom", 0.0)) for r in grid])
            sc = ax1.scatter(N, T, c=F, cmap="viridis")
            fig.colorbar(sc, ax=ax1, label="FOM")
            ax1.set_xscale('log')
            ax1.set_xlabel('Density n (cm^-3)')
            ax1.set_ylabel('Temperature T (eV)')
            ax1.set_title('Operating Envelope')
        # Right panel: time to metrics (if present)
        t_series = tm.get("time_ms_series") or tm.get("time_ms") or []
        e_series = tm.get("energy_J_series") or tm.get("energy_J") or []
        stab_ms = tm.get("time_to_stability_ms")
        yield_ms = tm.get("time_to_yield_ms")
        if t_series and e_series:
            ax2.plot(t_series, e_series, color='teal', label='Energy')
        if stab_ms is not None:
            ax2.axvline(stab_ms, color='green', linestyle='--', label='Stability')
        if yield_ms is not None:
            ax2.axvline(yield_ms, color='orange', linestyle='--', label='Yield')
        ax2.set_xlabel('Time (ms)')
        ax2.set_ylabel('Energy (J)')
        ax2.set_title('Time-to-Stability/Yield')
        ax2.legend(loc='best')
        fig.tight_layout()
        fig.savefig(args.out, dpi=150)
        plt.close(fig)
        print(json.dumps({"wrote": args.out}))
    except Exception as e:
        # optional plotting dependency might be missing
        print(json.dumps({"skipped": True, "reason": str(e)}))


if __name__ == "__main__":
    main()
