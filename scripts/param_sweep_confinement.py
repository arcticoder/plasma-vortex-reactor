#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv

from reactor.metrics import confinement_efficiency_estimator

try:
    from reactor.plotting import quick_scatter  # type: ignore
except Exception:
    quick_scatter = None  # type: ignore


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Param sweep for confinement efficiency over xi and B-field ripple"
        )
    )
    ap.add_argument("--xi-min", type=float, default=0.5)
    ap.add_argument("--xi-max", type=float, default=5.0)
    ap.add_argument("--xi-steps", type=int, default=10)
    ap.add_argument("--ripple-min", type=float, default=0.0)
    ap.add_argument("--ripple-max", type=float, default=0.02)
    ap.add_argument("--ripple-steps", type=int, default=10)
    ap.add_argument("--out", default="confinement_sweep.csv")
    ap.add_argument("--plot", default=None, help="Optional PNG output; requires matplotlib")
    ap.add_argument(
        "--heatmap",
        default=None,
        help="Optional PNG heatmap path; requires matplotlib",
    )
    ap.add_argument("--json-out", default=None, help="Optional JSON output path for rows")
    args = ap.parse_args()

    xi_vals = [
        args.xi_min
        + i * (args.xi_max - args.xi_min) / max(args.xi_steps - 1, 1)
        for i in range(args.xi_steps)
    ]
    ripple_vals = [
        args.ripple_min
        + j * (args.ripple_max - args.ripple_min) / max(args.ripple_steps - 1, 1)
        for j in range(args.ripple_steps)
    ]

    # optional progress bar
    def prog_iter_default(x):
        return x
    try:
        from tqdm import tqdm  # type: ignore
        def prog_iter_tqdm(x):  # type: ignore
            return tqdm(x)
    except Exception:
        prog_iter_tqdm = None  # type: ignore
    prog_iter = prog_iter_tqdm or prog_iter_default

    with open(args.out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["xi", "b_field_ripple_pct", "efficiency"])
        rows = []
        for xi in prog_iter(xi_vals):
            for rp in ripple_vals:
                eff = confinement_efficiency_estimator(xi, rp)
                w.writerow([xi, rp, eff])
                rows.append({"xi": xi, "b_field_ripple_pct": rp, "efficiency": eff})
    if args.json_out:
        import json
        with open(args.json_out, "w", encoding="utf-8") as jf:
            json.dump({"rows": rows}, jf, indent=2)
    if args.plot and quick_scatter is not None:
        # flatten to a simple scatter over xi dimension by averaging over ripple
        import numpy as np

        rows2 = []
        for xi in xi_vals:
            effs = [confinement_efficiency_estimator(xi, rp) for rp in ripple_vals]
            rows2.append((xi, float(np.mean(effs))))
        xs = [r[0] for r in rows2]
        ys = [r[1] for r in rows2]
        try:
            quick_scatter(
                xs,
                ys,
                args.plot,
                xlabel="xi",
                ylabel="mean efficiency",
                title="Mean efficiency vs xi",
            )
        except Exception as e:  # pragma: no cover
            print(f"Plot failed: {e}")
    if args.heatmap and quick_scatter is not None:
        try:
            import numpy as np

            from reactor.plotting import _mpl

            plt = _mpl()
            Z = np.zeros((len(xi_vals), len(ripple_vals)))
            for i, xi in enumerate(xi_vals):
                for j, rp in enumerate(ripple_vals):
                    Z[i, j] = confinement_efficiency_estimator(xi, rp)
            fig, ax = plt.subplots(figsize=(5, 4))
            extent = (
                float(min(ripple_vals)),
                float(max(ripple_vals)),
                float(min(xi_vals)),
                float(max(xi_vals)),
            )
            im = ax.imshow(Z, origin='lower', aspect='auto', extent=extent)
            ax.set_xlabel('b_field_ripple_pct')
            ax.set_ylabel('xi')
            fig.colorbar(im, ax=ax, label='efficiency')
            fig.tight_layout()
            fig.savefig(args.heatmap, dpi=150)
            plt.close(fig)
        except Exception as e:  # pragma: no cover
            print(f"Heatmap plot failed: {e}")


if __name__ == "__main__":
    main()
