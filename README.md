Plasma Vortex Reactor
=====================

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
