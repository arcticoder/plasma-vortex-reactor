from __future__ import annotations
import argparse
import json
from .config import load_json
from .core import Reactor
from .metrics import save_feasibility_gates_report, confinement_efficiency_estimator
from .analysis import b_field_rms_fluctuation, estimate_density_from_em, stability_variance
from .logging_utils import append_event
try:
    from . import plotting as plotting_helpers  # type: ignore
except Exception:  # pragma: no cover
    plotting_helpers = None  # type: ignore


def cmd_demo(args: argparse.Namespace) -> None:
    cfg = load_json(args.scenario) if args.scenario else {}
    timeline_path = args.timeline_log or cfg.get("timeline_log_path")
    xi = cfg.get("xi", 2.0)
    br = cfg.get("b_field_ripple_pct", 0.005)
    grid = tuple(cfg.get("grid", [32, 32]))
    nu = float(cfg.get("nu", 1e-3))
    R = Reactor(grid=grid, nu=nu, timeline_log_path=timeline_path, xi=xi, b_field_ripple_pct=br)
    # log run seed for reproducibility, if timeline is enabled
    if timeline_path:
        append_event(timeline_path, event="run_started", status="ok", details={"seed": int(args.seed)})
    for _ in range(int(args.steps)):
        R.step(dt=float(args.dt))
    print(json.dumps({"done": True, "timeline": timeline_path or None, "seed": int(args.seed)}))


def cmd_param_sweep(args: argparse.Namespace) -> None:
    xi_vals = [args.xi_min + i*(args.xi_max-args.xi_min)/max(args.xi_steps-1,1) for i in range(args.xi_steps)]
    ripple_vals = [args.ripple_min + j*(args.ripple_max-args.ripple_min)/max(args.ripple_steps-1,1) for j in range(args.ripple_steps)]
    rows = []
    for xi in xi_vals:
        for rp in ripple_vals:
            eff = confinement_efficiency_estimator(xi, rp)
            rows.append({"xi": xi, "b_field_ripple_pct": rp, "efficiency": eff})
    # Save CSV if requested
    if args.out:
        import csv
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["xi", "b_field_ripple_pct", "efficiency"])
            w.writeheader()
            for r in rows:
                w.writerow(r)
    # Optional quick plot
    if args.plot and plotting_helpers is not None:
        try:
            xs = [r["xi"] for r in rows]
            ys = [r["efficiency"] for r in rows]
            plotting_helpers.quick_scatter(xs, ys, args.plot, xlabel="xi", ylabel="efficiency", title="Confinement efficiency sweep")
        except Exception as e:
            # keep CLI robust if plotting unavailable
            print(json.dumps({"warning": f"plotting failed: {e}"}))
    # Always print JSON summary for programmatic consumption
    print(json.dumps({"rows": rows}))


def cmd_feasibility(args: argparse.Namespace) -> None:
    # Thin wrapper around generate_feasibility_report behavior: expect precomputed arrays via JSON strings
    import numpy as np
    from .thresholds import Thresholds
    import sys
    thr = Thresholds()
    def _load_series(s):
        return np.array(json.loads(s), dtype=float) if s else None
    gamma_series = _load_series(args.gamma_series)
    b_series = _load_series(args.b_series)
    E_mag = _load_series(args.E_mag)
    gamma_ok = False
    gamma_stats = {}
    if gamma_series is not None and gamma_series.size > 0:
        gamma_stats = {
            "gamma_min": float(np.min(gamma_series)),
            "gamma_max": float(np.max(gamma_series)),
            "gamma_mean": float(np.mean(gamma_series)),
            "gamma_variance": stability_variance(gamma_series),
            "dt": args.dt,
        }
        needed = int(np.ceil(args.gamma_duration / max(args.dt, 1e-12)))
        mask = gamma_series >= args.gamma_threshold
        run = 0
        for m in mask:
            run = run + 1 if m else 0
            if run >= needed:
                gamma_ok = True
                break
    b_ok = False
    b_stats = {}
    if b_series is not None and b_series.size > 0:
        rms = b_field_rms_fluctuation(b_series)
        b_stats = {"b_mean_T": float(np.mean(b_series)), "b_rms_fraction": rms}
        b_ok = (rms <= args.b_ripple_max) and (np.mean(b_series) >= thr.b_field_min_T)
    dens_ok = False
    dens_stats = {}
    if E_mag is not None and E_mag.size > 0:
        ne = estimate_density_from_em(E_mag, gamma=1.0, Emin=0.0, ne_min=0.0)
        dens_stats = {"ne_max_cm3": float(np.max(ne))}
        dens_ok = float(np.max(ne)) >= args.density_threshold
    payload = {
        "stable": gamma_ok and b_ok and dens_ok,
        "gamma_ok": gamma_ok,
        "b_ok": b_ok,
        "dens_ok": dens_ok,
        "gamma_stats": gamma_stats,
        "b_stats": b_stats,
        "density_stats": dens_stats,
    }
    print(json.dumps(payload))
    if args.fail_on_gate and not payload.get("stable", False):
        sys.exit(2)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="reactor")
    sp = ap.add_subparsers(dest="cmd", required=True)
    # demo
    p_demo = sp.add_parser("demo")
    p_demo.add_argument("--scenario", default=None)
    p_demo.add_argument("--timeline-log", default=None)
    p_demo.add_argument("--steps", type=int, default=10)
    p_demo.add_argument("--dt", type=float, default=1e-3)
    p_demo.add_argument("--seed", type=int, default=123)
    p_demo.set_defaults(func=cmd_demo)
    # param sweep
    p_sweep = sp.add_parser("param-sweep")
    p_sweep.add_argument("--xi-min", type=float, default=0.5)
    p_sweep.add_argument("--xi-max", type=float, default=5.0)
    p_sweep.add_argument("--xi-steps", type=int, default=10)
    p_sweep.add_argument("--ripple-min", type=float, default=0.0)
    p_sweep.add_argument("--ripple-max", type=float, default=0.02)
    p_sweep.add_argument("--ripple-steps", type=int, default=10)
    p_sweep.add_argument("--out", default=None, help="Optional CSV output path")
    p_sweep.add_argument("--plot", default=None, help="Optional PNG path; requires matplotlib")
    p_sweep.set_defaults(func=cmd_param_sweep)
    # feasibility
    p_feas = sp.add_parser("feasibility")
    p_feas.add_argument("--gamma-series", default=None)
    p_feas.add_argument("--dt", type=float, default=1e-3)
    p_feas.add_argument("--b-series", default=None)
    p_feas.add_argument("--E-mag", default=None)
    p_feas.add_argument("--gamma-threshold", type=float, default=140.0)
    p_feas.add_argument("--gamma-duration", type=float, default=0.01)
    p_feas.add_argument("--density-threshold", type=float, default=1e20)
    p_feas.add_argument("--b-ripple-max", type=float, default=0.01)
    p_feas.add_argument("--fail-on-gate", action="store_true", help="Exit non-zero if any feasibility gate fails")
    p_feas.set_defaults(func=cmd_feasibility)
    return ap


def main():
    ap = build_parser()
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
