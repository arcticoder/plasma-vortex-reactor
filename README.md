Plasma Vortex Reactor
=====================

![CI](https://github.com/arcticoder/plasma-vortex-reactor/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Unlicense-blue.svg)
![Phase](https://img.shields.io/badge/phase-3%20production-brightgreen)

A research and prototyping repository for a plasma vortex reactor targeting high-energy applications (e.g., antiproton production) via pair creation in controlled plasma vortices. This repo integrates vortex dynamics, kinetic modeling, confinement equilibria, and EM/laser-plasma coupling. It links to the broader arcticoder ecosystem for simulation, energy sourcing, and control.

- docs/: roadmap.ndjson, progress_log.ndjson, UQ-TODO.ndjson, VnV-TODO.ndjson
- src/: reactor package with light, testable stubs for math kernels and control glue
- tests/: pytest/unittest-style sanity and smoke tests

Open the multi-repo workspace: plasma-vortex-reactor.code-workspace

## Metrics Quickstart

- Run demo with timeline logging:
  ```
  python scripts/demo_runner.py --scenario examples/scenario_min.json --steps 10 --dt 1e-3
  ```
- Generate feasibility report from synthetic series:
  ```
  python scripts/generate_feasibility_report.py --gamma-series "[150,150,150,120]" --dt 0.002 \
    --b-series "[5,5.01,4.99,5.02]" --E-mag "[0,1,2,3]" --out feasibility_gates_report.json
  ```
- UQ results can be produced via `reactor.uq.run_uq_sampling` and saved to `uq_results.json`.

- Param sweep CSV:
  ```
  python scripts/param_sweep_confinement.py --out data/confinement_sweep.csv
  ```
  - Full time sweep (writes `data/full_sweep_with_time.csv` with t, ripple, yield, E_total, fom, eta):
  ```
  python scripts/param_sweep_confinement.py --full-sweep-with-time
  ```
  - Dynamic ripple sweep (writes `data/full_sweep_with_dynamic_ripple.csv` using `Reactor.adjust_ripple`):
  ```
  python scripts/param_sweep_confinement.py --full-sweep-with-dynamic-ripple
  ```
  - Bennett-profile checks (confinement ≥94%, Γ>140 for ≥10 ms):
  ```
  # Confinement (η) via Bennett check appears in sweep CSV rows as 'eta' booleans
  python scripts/param_sweep_confinement.py --full-sweep-with-time
  
  # Plot Γ timeline using a provided JSON array series and overlay thresholds; also dump raw data for numeric checks
  python scripts/plot_stability.py --series "[150,150,150,120]" --overlay-thresholds --out artifacts/stability.png \
    --out-json artifacts/stability_data.json --out-csv data/stability_data.csv
  ```
- Metrics gate check against metrics.json:
  ```
  python scripts/metrics_gate.py --metrics metrics.json --report feasibility_gates_report.json
  ```
- UQ demo:
  ```
  python scripts/uq_demo.py --samples 20 --seed 123
  ```

See `docs/ARTIFACT_SCHEMA.md` for artifact structures.

## Artifacts and Schemas

Artifacts produced by this repo:

- feasibility_gates_report.json (scripts/generate_feasibility_report.py)
- timeline.ndjson (scripts/demo_runner.py and Reactor timeline logging)
- gate_summary.md (scripts/gate_summary_md.py)
- channel_report.json (scripts/generate_channel_report.py)
- run_report.json (scripts/run_report.py)
  
## CLI Catalog

- plot_hardware_metrics.py: Plot metrics over time; supports NDJSON/JSON; `--high-load` variant.
- plot_dynamic_stability_ripple.py: Generate dynamic stability vs ripple plot from sweep CSV.
- run_report.py: Merge feasibility, timeline, UQ, and sweep heads into integrated_report.json.
- production_kpi.py: Produce production_kpi.json summary; respects optional configs/cost_model.json.
  - Also summarizes energy-per-antiproton for antiproton program comparisons.
- calibrate_ripple_alpha.py: Fit decay alpha from dynamic ripple sweep CSV.
- time_to_stability_yield.py: Compute time to reach yield/FOM thresholds and emit JSON/PNG.
  - Also supports reporting Γ duration and trap retention summary:
    - `--gamma-series '[150,150,...]' --gamma-dt 0.001 --gamma-threshold 140 --gamma-min-duration 0.01`
    - `--retention-csv data/retention_window.csv` (expects `retention_pct` or `retention` column)
- envelope_sweep.py: Density–Temperature operating envelope with FOM contours.
- ablation_ripple.py: Ablation of ripple control ON vs OFF.
- plot_kpi_trend.py: Plot KPI FOM trend across revisions (writes `artifacts/kpi_trend.png`).
- timeline_analysis.py: Analyze timeline anomalies/events to `timeline_stats.json`.

Examples:

```
python scripts/plot_hardware_metrics.py --out artifacts/hardware_metrics.png
python scripts/plot_dynamic_stability_ripple.py --from-sweep data/full_sweep_with_dynamic_ripple.csv --out artifacts/dynamic_stability_ripple.png
python scripts/run_report.py --feasibility feasibility_gates_report.json --timeline-summary timeline_summary.json --uq uq_optimized.json --integrated-out integrated_report.json
python scripts/production_kpi.py --feasibility feasibility_gates_report.json --metrics metrics.json --uq uq_optimized.json --cost-model configs/cost_model.json --out production_kpi.json
python scripts/calibrate_ripple_alpha.py --from-csv data/full_sweep_with_dynamic_ripple.csv --out calibration.json
python scripts/time_to_stability_yield.py --sweep-time data/full_sweep_with_time.csv --out-json artifacts/time_to_metrics.json --out-png artifacts/time_to_metrics.png
# Optional: include Γ duration and retention summary
python scripts/time_to_stability_yield.py \
  --sweep-time data/full_sweep_with_time.csv \
  --gamma-series "[150,150,150,150,120]" --gamma-dt 0.002 --gamma-threshold 140 --gamma-min-duration 0.01 \
  --retention-csv data/retention_window.csv \
  --out-json artifacts/time_to_metrics_gamma.json --out-png artifacts/time_to_metrics_gamma.png
python scripts/plot_kpi_trend.py --out artifacts/kpi_trend.png
python scripts/timeline_analysis.py --timeline docs/timeline_anomalies.ndjson --out timeline_stats.json
python scripts/envelope_sweep.py --n-points 12 --out-json artifacts/operating_envelope.json --out-csv data/operating_envelope.csv --out-png artifacts/operating_envelope.png
python scripts/ablation_ripple.py --n 5000 --out ablation_ripple.json
```


Schemas live under `docs/schemas/`:

- docs/schemas/metrics.schema.json
- docs/schemas/feasibility.schema.json
- docs/schemas/channel_report.schema.json

You can validate with `jsonschema` if installed.

## Optional extras

Install optional plotting/progress/validation extras:

```
pip install -r requirements-plot.txt
```

Note: Plotting scripts require `matplotlib`. Specifically, `plot_hardware_metrics.py` depends on the plotting extra.

By default, plotting and analysis scripts now write outputs under `artifacts/` (images/json) and place generated CSV inputs under `data/` to avoid cluttering the repo root.

Dynamic ripple vs time plot:
- The helper will auto-generate `data/full_sweep_with_dynamic_ripple.csv` if missing by invoking the sweep script.
- Usage:
  - `python scripts/plot_dynamic_ripple_time.py --from-csv data/full_sweep_with_dynamic_ripple.csv --out artifacts/dynamic_ripple_time.png`
  - If no data or matplotlib is available, a small placeholder PNG is written so downstream steps never fail.

Why do some stability plots show only three points from many CSV rows?
- `scripts/plot_dynamic_stability_ripple.py` samples ripple values at approximate 10th/50th/90th percentiles to keep the figure readable. To plot all points, pass `--all-points`.
  - Example: `python scripts/plot_dynamic_stability_ripple.py --from-sweep data/full_sweep_with_dynamic_ripple.csv --all-points --out artifacts/dynamic_stability_ripple.png`

Order of operations (to produce artifacts/integrated_report.json):
- Run the demo to produce `timeline.ndjson` and `metrics.json`.
- Generate `feasibility_gates_report.json` (e.g., with datasets or scenario outputs).
- Optionally run `uq_optimize.py` (writes `uq_optimized.json`) and `param_sweep_confinement.py --full-sweep-with-time/--full-sweep-with-dynamic-ripple` (writes `data/full_sweep_with_*.csv`).
- Run `run_report.py --integrated-out artifacts/integrated_report.json` (defaults will look in `data/` for sweeps).
  - If `data/full_sweep_with_time.csv` is missing, run:
    `python scripts/param_sweep_confinement.py --full-sweep-with-time`

### Additional CLI entry points

Console scripts installed with the package:

- pv-plot-fom, pv-plot-stability
- pv-run-report, pv-kpi
- pv-sweep-time, pv-sweep-dyn
- pv-hw-runner
- pv-snr, pv-bench
- pv-build-artifacts
- pv-anomalies, pv-validate-schemas
- pv-cost-sweep, pv-snr-prop, pv-perf-budget
- pv-envelope, pv-ablation-ripple

## Releases and Artifacts

The CI workflow uploads a bundle of artifacts on each push/PR, including:

- integrated_report.json, production_kpi.json, feasibility_gates_report.json
- time_to_metrics.{json,png}, calibration.json
- key plots: artifacts/production_fom_yield.png, artifacts/stability.png, artifacts/dynamic_stability_ripple.png
- KPI trend: artifacts/kpi_trend.png
- anomalies summary: anomalies_summary.json
- envelope: operating_envelope.{json,csv,png}; ablation: ablation_ripple.json
- utility outputs: artifacts/sensor_noise.png, artifacts/bench_step_loop.json, artifacts/bench_trend.jsonl
- analysis outputs: artifacts/cost_sweep.{json,csv,png}, artifacts/snr_propagation.{json,png}

Materials for reviewers: see `dist/repro-bundle.tgz` for a one-command reproduction runner and open key plots (artifacts/operating_envelope.png, artifacts/dynamic_stability_ripple.png, artifacts/envelope_dual_panel.png) directly from the Artifacts list.

## What's novel

- CI-enforced KPI gates and performance budgets with trend plotting and PR badges.
- Dynamic ripple adjustment pipeline with ablation study and stability probability gates.
- Operating envelope characterization (n,T → FOM) feeding into scenario selection.
- Reproducible artifacts and a minimal repro bundle tarball for reviewers.
- KPI trend transparency (`artifacts/kpi_trend.png`).

## Try it: Three Scenarios

- Minimal:
  - `python scripts/demo_runner.py --scenario examples/scenario_min.json --steps 10 --dt 1e-3`
- Edge:
  - `python scripts/demo_runner.py --scenario examples/scenario_edge.json --steps 100 --dt 1e-3`
- Production:
  - `python scripts/demo_runner.py --scenario examples/scenario_production.json --steps 1000 --dt 1e-3`

Note on the CI badge: The badge reflects the latest default-branch workflow run. If it appears failing on the GitHub page but local runs pass, check the last Actions run for details; intermittent flaky network steps can be retried.

## Documentation

See `docs/` for detailed documentation, including:

- `docs/ARTIFACT_SCHEMA.md`: Schema and structure of artifacts produced by the repository.
- `docs/usage.md`: Detailed usage instructions and examples for all scripts and tools.
- `docs/development.md`: Guidelines for development, testing, and contributing to the repository.
