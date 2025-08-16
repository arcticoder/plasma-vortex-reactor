#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import os
import sys

# Ensure repository sources are importable when running from scripts/ directly
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from reactor.metrics import confinement_efficiency_estimator, antiproton_yield_estimator
from reactor.analysis import bennett_confinement_check

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
    ap.add_argument("--plot-confinement-energy", default=None, help="Optional PNG plotting confinement vs synthetic energy reduction factor")
    ap.add_argument("--full-sweep-with-ripple", action="store_true", help="Write full_sweep_with_ripple.csv for small demo ranges")
    ap.add_argument("--full-sweep-with-time", action="store_true", help="Write full_sweep_with_time.csv including time and FOM columns")
    ap.add_argument("--full-sweep-with-dynamic-ripple", action="store_true", help="Write full_sweep_with_dynamic_ripple.csv including time-varying ripple via Reactor.adjust_ripple")
    ap.add_argument(
        "--heatmap",
        default=None,
        help="Optional PNG heatmap path; requires matplotlib",
    )
    ap.add_argument("--json-out", default=None, help="Optional JSON output path for rows")
    ap.add_argument("--jsonl-out", default=None, help="Optional JSONL (NDJSON) output path; one row per line")
    ap.add_argument("--seed", type=int, default=None, help="Optional seed for deterministic behavior")
    args = ap.parse_args()

    # Deterministic grid by construction; seed reserved for future stochastic variants
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
    if args.json_out or args.jsonl_out:
        import json
        if args.json_out:
            with open(args.json_out, "w", encoding="utf-8") as jf:
                json.dump({"rows": rows}, jf, indent=2)
        if args.jsonl_out:
            with open(args.jsonl_out, "w", encoding="utf-8") as jlf:
                for r in rows:
                    jlf.write(json.dumps(r) + "\n")
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

    # Optional confinement vs energy-reduction scatter (synthetic mapping)
    if args.plot_confinement_energy:
        try:
            import numpy as np
            from reactor.plotting import _mpl  # type: ignore

            plt = _mpl()
            # Build synthetic dataset: map efficiency in [0,1] to reduction factor ~ [100, 300]
            effs = np.linspace(0.9, 0.96, 4)
            reductions = np.array([200, 220, 242, 260])
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.scatter(effs, reductions, c='teal')
            ax.set_xlabel('Confinement Efficiency (η)')
            ax.set_ylabel('Energy Reduction Factor')
            ax.set_title('Confinement vs. Energy Reduction')
            fig.tight_layout()
            fig.savefig(args.plot_confinement_energy, dpi=150)
            plt.close(fig)
        except Exception as e:  # pragma: no cover
            print(f"Confinement-energy plot failed: {e}")

    # Optional full sweep utility can be imported by other scripts

    if args.full_sweep_with_ripple:
        # Small demo ranges to keep CI fast
        from itertools import product
        n_e_range = [1e19, 1e20, 1e21]
        T_e_range = [5.0, 10.0, 20.0]
        B_range = [4.5, 5.0, 5.5]
        xi_range = [1.0, 2.0, 4.0]
        alpha_range = [0.0, 0.01]
        rows = []
        for n_e, T_e, B, xi, alpha in product(n_e_range, T_e_range, B_range, xi_range, alpha_range):
            ripple = 0.01 * max(0.0, 1.0 - alpha * 0.1)  # t=0.1 proxy
            y = antiproton_yield_estimator(n_e, T_e, {"model": "physics"})
            eta_ok = bennett_confinement_check(n_e, xi, B, ripple)
            rows.append({"n_e": n_e, "T_e": T_e, "B": B, "xi": xi, "alpha": alpha, "yield": y, "eta": bool(eta_ok)})
        with open("full_sweep_with_ripple.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow(r)

    if args.full_sweep_with_time:
        # Include time dimension and compute FOM using a simple energy proxy E_total = t * 1e6
        from itertools import product
        import csv as _csv
        import math as _math

        n_e_range = [1e19, 1e20, 1e21]
        T_e_range = [5.0, 10.0, 20.0]
        B_range = [4.5, 5.0, 5.5]
        xi_range = [1.0, 2.0, 4.0]
        alpha_range = [0.0, 0.01]
        t_range = [0.01, 0.1, 1.0]  # seconds
        rows = []
        for n_e, T_e, B, xi, alpha, t in product(n_e_range, T_e_range, B_range, xi_range, alpha_range, t_range):
            ripple = 0.01 * max(0.0, 1.0 - alpha * t)
            y = antiproton_yield_estimator(n_e, T_e, {"model": "physics"})
            # energy proxy and FOM
            E_total = max(1e-9, t) * 1e6
            from reactor.metrics import total_fom as _fom
            f = _fom(y, E_total)
            eta_ok = bennett_confinement_check(n_e, xi, B, ripple)
            rows.append({"n_e": n_e, "T_e": T_e, "B": B, "xi": xi, "alpha": alpha, "t": t, "ripple": ripple, "yield": y, "E_total": E_total, "fom": f, "eta": bool(eta_ok)})
        with open("full_sweep_with_time.csv", "w", newline="", encoding="utf-8") as f:
            w = _csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow(r)

    if args.full_sweep_with_dynamic_ripple:
        # Use Reactor.adjust_ripple to evolve ripple vs time given a synthetic B_series around mean B
        from itertools import product
        import numpy as _np
        from reactor.core import Reactor as _Reactor
        from reactor.analysis_fields import b_field_rms_fluctuation as _ripple

        n_e_range = [1e19, 1e20, 1e21]
        T_e_range = [5.0, 10.0, 20.0]
        B_range = [5.0]  # use single mean for series generation
        xi_range = [1.0, 2.0, 4.0]
        alpha_range = [0.0, 0.01]
        t_range = [0.01, 0.1, 1.0]
        rows = []
        for n_e, T_e, B, xi, alpha, t in product(n_e_range, T_e_range, B_range, xi_range, alpha_range, t_range):
            # build B_series around B with small Gaussian ripple
            base = float(B)
            series = _np.ones(256) * base + _np.random.normal(0, 5e-5, 256)
            R = _Reactor(grid=(16, 16), nu=1e-3, b_series=series)
            R._time_s = float(t)
            ripple0 = _ripple(R.B_series if R.B_series is not None else series)
            ripple1 = R.adjust_ripple(alpha=float(alpha))
            y = antiproton_yield_estimator(n_e, T_e, {"model": "physics"})
            E_total = max(1e-9, t) * 1e6
            from reactor.metrics import total_fom as _fom
            f = _fom(y, E_total)
            eta_ok = bennett_confinement_check(n_e, xi, base, ripple1)
            rows.append({
                "n_e": n_e, "T_e": T_e, "B": base, "xi": xi, "alpha": alpha, "t": t,
                "ripple_initial": ripple0, "ripple_dynamic": ripple1,
                "yield": y, "E_total": E_total, "fom": f, "eta": bool(eta_ok)
            })
        if rows:
            import csv as _csv
            with open("full_sweep_with_dynamic_ripple.csv", "w", newline="", encoding="utf-8") as f:
                w = _csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                for r in rows:
                    w.writerow(r)


def full_sweep(n_e_range, T_e_range, B_range, xi_range, out_csv: str = "full_sweep.csv") -> None:
    from itertools import product
    import csv as _csv
    rows = []
    for n_e, T_e, B, xi in product(n_e_range, T_e_range, B_range, xi_range):
        y = antiproton_yield_estimator(n_e, T_e, {"model": "physics"})
        eta = bennett_confinement_check(n0_cm3=n_e, xi=xi, B_T=B, ripple_frac=5e-4)
        rows.append({"n_e": n_e, "T_e": T_e, "B": B, "xi": xi, "yield": y, "eta": bool(eta)})
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = _csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def optimize_confinement(I_p_range, r_p_range, B_range, out_csv: str = "optimized_confinement.csv") -> None:
    """Optimize confinement to achieve eta >= 0.94 using xi derived from I_p, r_p, B.

    xi = I_p / (5π r_p B). Use ripple=5e-4 and n0=1e20 cm^-3 as defaults for Bennett check.
    Writes rows meeting eta>=0.94.
    """
    from itertools import product
    import math as _math
    import csv as _csv

    rows = []
    for I_p, r_p, B in product(I_p_range, r_p_range, B_range):
        xi = float(I_p) / (5.0 * _math.pi * float(r_p) * float(B) + 1e-12)
        ripple = 5e-4
        eta = confinement_efficiency_estimator(xi, ripple)
        bennett_ok = bennett_confinement_check(1e20, xi, B, ripple)
        if eta >= 0.94 and bennett_ok:
            rows.append({"I_p": I_p, "r_p": r_p, "B": B, "xi": xi, "eta": eta})
    if rows:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            w = _csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow(r)


if __name__ == "__main__":
    main()
