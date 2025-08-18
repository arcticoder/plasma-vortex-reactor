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
        # Ensure local package is importable when running from scripts/
        import sys, os
        _here = os.path.dirname(os.path.abspath(__file__))
        _root = os.path.dirname(_here)
        _src = os.path.join(_root, 'src')
        if _src not in sys.path:
            sys.path.insert(0, _src)
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
        # Accept multiple keys and units (s vs ms)
        t_series = tm.get("time_ms_series") or tm.get("time_ms") or []
        if (not t_series) and ("time_s_series" in tm):
            try:
                t_series = [float(x) * 1000.0 for x in (tm.get("time_s_series") or [])]
            except Exception:
                t_series = []
        e_series = tm.get("energy_J_series") or tm.get("energy_J") or []

        # Markers: stability/yield
        stab_ms = tm.get("time_to_stability_ms")
        yield_ms = tm.get("time_to_yield_ms")
        # Fallback: seconds-only keys from time_to_stability_yield.py
        if stab_ms is None:
            v = tm.get("time_to_fom") or tm.get("time_to_stability")
            if isinstance(v, (int, float)):
                stab_ms = float(v) * 1000.0
        if yield_ms is None:
            v = tm.get("time_to_yield") or tm.get("time_to_yield_s")
            if isinstance(v, (int, float)):
                yield_ms = float(v) * 1000.0

        # Plot series if both time and energy available
        if t_series and e_series:
            try:
                ax2.plot(t_series, e_series, color='teal', label='Energy')
            except Exception:
                pass
        # Always plot markers if present; if they coincide, draw one combined line
        x_vals = []
        if (stab_ms is not None) and (yield_ms is not None):
            try:
                s_val = float(stab_ms)
                y_val = float(yield_ms)
                tol = max(1e-6, 0.001 * max(abs(s_val), abs(y_val)))
                if abs(s_val - y_val) <= tol:
                    ax2.axvline(s_val, color='purple', linestyle='--', label='Yield & Stability')
                    x_vals.append(s_val)
                else:
                    ax2.axvline(s_val, color='green', linestyle='--', label='Stability')
                    ax2.axvline(y_val, color='orange', linestyle='--', label='Yield')
                    x_vals.extend([s_val, y_val])
            except Exception:
                # Fallback to plotting whichever parses
                if stab_ms is not None:
                    try:
                        sv = float(stab_ms)
                        ax2.axvline(sv, color='green', linestyle='--', label='Stability')
                        x_vals.append(sv)
                    except Exception:
                        pass
                if yield_ms is not None:
                    try:
                        yv = float(yield_ms)
                        ax2.axvline(yv, color='orange', linestyle='--', label='Yield')
                        x_vals.append(yv)
                    except Exception:
                        pass
        else:
            if stab_ms is not None:
                try:
                    sv = float(stab_ms)
                    ax2.axvline(sv, color='green', linestyle='--', label='Stability')
                    x_vals.append(sv)
                except Exception:
                    pass
            if yield_ms is not None:
                try:
                    yv = float(yield_ms)
                    ax2.axvline(yv, color='orange', linestyle='--', label='Yield')
                    x_vals.append(yv)
                except Exception:
                    pass
        # If no series was provided, set some sensible limits so markers are visible
        if not (t_series and e_series):
            if x_vals:
                xmax = max(x_vals) * 1.1 if max(x_vals) > 0 else 1.0
                ax2.set_xlim(left=0.0, right=xmax)
            ax2.set_ylim(bottom=0.0, top=1.0)
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
