Plasma Vortex Reactor
=====================

![CI](https://github.com/arcticoder/plasma-vortex-reactor/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
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
  python scripts/param_sweep_confinement.py --out confinement_sweep.csv
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
- progress_dashboard.html (scripts/generate_progress_dashboard.py)
## CLI Catalog

- plot_hardware_metrics.py: Plot metrics over time; supports NDJSON/JSON; `--high-load` variant.
- plot_dynamic_stability_ripple.py: Generate dynamic stability vs ripple plot from sweep CSV.
- run_report.py: Merge feasibility, timeline, UQ, and sweep heads into integrated_report.json.
- production_kpi.py: Produce production_kpi.json summary; respects optional configs/cost_model.json.
- calibrate_ripple_alpha.py: Fit decay alpha from dynamic ripple sweep CSV.
- time_to_stability_yield.py: Compute time to reach yield/FOM thresholds and emit JSON/PNG.
- generate_progress_dashboard.py: Build progress_dashboard.html aggregating docs/*.ndjson.

Examples:

```
python scripts/plot_hardware_metrics.py --out hardware_metrics.png
python scripts/plot_dynamic_stability_ripple.py --from-sweep full_sweep_with_dynamic_ripple.csv --out dynamic_stability_ripple.png
python scripts/run_report.py --feasibility feasibility_gates_report.json --timeline-summary timeline_summary.json --uq uq_optimized.json --integrated-out integrated_report.json
python scripts/production_kpi.py --feasibility feasibility_gates_report.json --metrics metrics.json --uq uq_optimized.json --cost-model configs/cost_model.json --out production_kpi.json
python scripts/calibrate_ripple_alpha.py --from-csv full_sweep_with_dynamic_ripple.csv --out calibration.json
python scripts/time_to_stability_yield.py --sweep-time full_sweep_with_time.csv --out-json time_to_metrics.json --out-png time_to_metrics.png
python scripts/generate_progress_dashboard.py --docs-dir docs --out progress_dashboard.html
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

### Progress Dashboard (HTML)

Generate a quick snapshot of roadmap/progress/UQ/VnV NDJSON:

```
python scripts/generate_progress_dashboard.py --docs-dir docs --out progress_dashboard.html
```
Open progress_dashboard.html in a browser.

### Additional CLI entry points

Console scripts installed with the package:

- pv-plot-fom, pv-plot-stability
- pv-run-report, pv-kpi
- pv-sweep-time, pv-sweep-dyn
- pv-dashboard
- pv-hw-runner
- pv-snr, pv-bench
- pv-build-artifacts
- pv-anomalies, pv-validate-schemas
- pv-cost-sweep, pv-snr-prop, pv-perf-budget

## Releases and Artifacts

The CI workflow uploads a bundle of artifacts on each push/PR, including:

- integrated_report.json, production_kpi.json, feasibility_gates_report.json
- time_to_metrics.{json,png}, calibration.json
- key plots: production_fom_yield.png, stability.png, dynamic_stability_ripple.png
- dashboard: progress_dashboard.html (+ progress_dashboard.json)
- utility outputs: sensor_noise.png, bench_step_loop.json, bench_trend.jsonl
- analysis outputs: cost_sweep.{json,csv,png}, snr_propagation.{json,png}

## Try it: Three Scenarios

- Minimal:
  - `python scripts/demo_runner.py --scenario examples/scenario_min.json --steps 10 --dt 1e-3`
- Edge:
  - `python scripts/demo_runner.py --scenario examples/scenario_edge.json --steps 100 --dt 1e-3`
- Production:
  - `python scripts/demo_runner.py --scenario examples/scenario_production.json --steps 1000 --dt 1e-3`
