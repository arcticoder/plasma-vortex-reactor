#!/usr/bin/env python3
"""Run several short demo->feasibility->production_kpi runs to produce artifacts/production_kpi_*.json

This helper is intended for CI-like reproducible runs that vary the energy budget
so the KPI trend shows a line rather than a single point.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / "src")

def run(cmd, env=None, check=True):
    ev = dict()
    if env:
        ev.update(env)
    try:
        print("RUN:", " ".join(cmd))
        subprocess.run(cmd, env={**{"PYTHONPATH": PY}, **ev}, check=check)
    except subprocess.CalledProcessError as e:
        print("Command failed:", e)
        raise

def main():
    ENEGS = [12_000_000, 11_500_000, 11_150_000, 10_800_000, 10_500_000]
    for i, eb in enumerate(ENEGS):
        tag = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + f"_{i:02d}"
        timeline = f"timeline_{tag}.ndjson"
        feas_orig = f"feasibility_{tag}.json"
        feas_nofom = f"feasibility_{tag}_nofom.json"
        outpk = Path("artifacts") / f"production_kpi_{tag}.json"

        # 1) demo run to create timeline events
        run(["python", "scripts/demo_runner.py", "--scenario", "examples/scenario_min.json", "--steps", "10", "--dt", "0.002", "--timeline-log", timeline, "--timeline-budget", "10", "--seed", str(123 + i)])

        # 2) feasibility generation with yield model (ensures antiproton_yield_pass present)
        run([
            "python",
            "scripts/generate_feasibility_report.py",
            "--gamma-series", "[150,150,150,150,150]",
            "--dt", "0.002",
            "--b-series", "[5,5,5,5]",
            "--E-mag", "[0,1e20,1e20,1e20]",
            "--yield-model", "threshold",
            "--n-cm3", "1e20",
            "--Te-eV", "10",
            "--bennett-n0", "1e20",
            "--bennett-xi", "2.0",
            "--bennett-B", "5.0",
            "--bennett-ripple", "5e-4",
            "--out", feas_orig,
        ])

        # 3) write a copy of the feasibility without 'fom' so production_kpi falls back to cost-model/metrics
        data = json.loads(Path(feas_orig).read_text())
        data.pop("fom", None)
        data.pop("fom_details", None)
        Path(feas_nofom).write_text(json.dumps(data, indent=2))
        print("wrote", feas_nofom)

        # 4) write metrics.json with this run's energy budget
        metrics = {"energy_budget_J": eb}
        Path("metrics.json").write_text(json.dumps(metrics, indent=2))
        print("wrote metrics.json energy_budget_J=", eb)

        # 5) run production_kpi to produce artifact
        run([
            "python",
            "scripts/production_kpi.py",
            "--feasibility",
            feas_nofom,
            "--metrics",
            "metrics.json",
            "--uq",
            "uq_optimized.json",
            "--cost-model",
            "configs/cost_model.json",
            "--out",
            str(outpk),
        ])

        # 6) validate gates using the original feasibility (which includes antiproton_yield_pass)
        run(["python", "scripts/metrics_gate.py", "--metrics", "metrics.json", "--report", feas_orig, "--require-yield"])
        print("wrote and validated:", outpk)

    # plot the trend from generated artifacts
    run(["python", "scripts/plot_kpi_trend.py", "--glob", "artifacts/production_kpi_*.json", "--require-passing", "--out", "artifacts/kpi_trend.png"])
    print("Plotted artifacts/kpi_trend.png")


if __name__ == "__main__":
    main()
