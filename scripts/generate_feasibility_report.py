#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

import numpy as np

from reactor.analysis import (
    b_field_rms_fluctuation,
    estimate_density_from_em,
    stability_variance,
)
from reactor.metrics import save_feasibility_gates_report
from reactor.thresholds import Thresholds


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Generate feasibility_gates_report.json from synthetic/collected stats"
        )
    )
    ap.add_argument("--out", default="feasibility_gates_report.json")
    ap.add_argument("--gamma-series", help="JSON array of gamma values over time", default=None)
    ap.add_argument("--dt", type=float, default=1e-3)
    ap.add_argument("--b-series", help="JSON array of B-field time series [T]", default=None)
    ap.add_argument(
        "--E-mag",
        help="JSON array of E-field magnitude for density estimate",
        default=None,
    )
    ap.add_argument("--gamma-threshold", type=float, default=Thresholds.gamma_min)
    ap.add_argument("--gamma-duration", type=float, default=Thresholds.gamma_duration_s)
    ap.add_argument("--density-threshold", type=float, default=Thresholds.density_min_cm3)
    ap.add_argument("--b-ripple-max", type=float, default=Thresholds.b_ripple_max_pct)
    ap.add_argument(
        "--scenario-id",
        default=None,
        help="Identifier for the scenario/config used",
    )
    ap.add_argument(
        "--fail-on-gate",
        action="store_true",
        help="Exit non-zero if any feasibility gate fails",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write file; just print summary",
    )
    ap.add_argument(
        "--validate",
        action="store_true",
        help="Validate JSON with jsonschema if available",
    )
    ap.add_argument(
        "--schema",
        default="docs/schemas/feasibility.schema.json",
        help="Path to feasibility JSON schema",
    )
    args = ap.parse_args()

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
        # simple continuous window check
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_id": args.scenario_id,
    }
    # Optional schema validation
    if args.validate:
        try:
            import jsonschema  # type: ignore
            with open(args.schema, "r", encoding="utf-8") as f:
                schema = json.load(f)
            jsonschema.validate(instance=payload, schema=schema)
        except Exception as e:
            print(json.dumps({"warning": f"validation failed or jsonschema missing: {e}"}))
    if not args.dry_run:
        save_feasibility_gates_report(args.out, payload)
    print(json.dumps(payload, indent=2))
    if args.fail_on_gate and not payload["stable"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
