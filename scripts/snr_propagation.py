#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.plotting import _mpl


def main() -> None:
    ap = argparse.ArgumentParser(description="Propagate SNR assumptions and visualize expected measurement error")
    ap.add_argument("--snr", type=float, default=20.0)
    ap.add_argument("--out-json", default="snr_propagation.json")
    ap.add_argument("--out-png", default="snr_propagation.png")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    import numpy as np
    np.random.seed(int(args.seed))
    snr = max(1e-6, float(args.snr))
    # simple model: relative std error ~ 1/snr
    rel_err = 1.0 / snr
    x = np.linspace(0, 1, 200)
    y_true = np.sin(2*np.pi*x)
    y_noisy = y_true + np.random.normal(0, rel_err, size=y_true.shape)

    Path(args.out_json).write_text(json.dumps({"snr": snr, "rel_error": rel_err}))

    try:
        plt = _mpl()
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(x, y_true, label="true", color="black")
        ax.plot(x, y_noisy, label="noisy", color="orange", alpha=0.7)
        ax.set_title(f"SNR Propagation (SNR={snr:g}, rel_err~{rel_err:.3f})")
        ax.legend(); fig.tight_layout(); fig.savefig(args.out_png, dpi=150); plt.close(fig)
    except Exception:
        # Best-effort: create a small placeholder so downstream steps don't fail on missing file
        try:
            Path(args.out_png).write_bytes(b"PNG placeholder - matplotlib not available\n")
        except Exception:
            pass


if __name__ == "__main__":
    main()
