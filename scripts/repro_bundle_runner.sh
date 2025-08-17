#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${HERE}/.."
cd "${ROOT}"
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
python scripts/demo_runner.py --scenario examples/scenario_min.json --steps 10 --dt 1e-3 --seed 123
python scripts/generate_feasibility_report.py --gamma-series "$(cat datasets/gamma_series.json)" --dt 0.002 --b-series "$(cat datasets/b_field_series.json)" --E-mag "$(cat datasets/E_mag.json)" --out feasibility_gates_report.json --scenario-id repro --require-yield --require-fom
python scripts/production_kpi.py --feasibility feasibility_gates_report.json --metrics metrics.json --uq uq_optimized.json --out production_kpi.json || true
python scripts/bench_step_loop.py --steps 200 --dt 1e-4 --out bench_step_loop.json
python scripts/performance_budget.py --bench bench_step_loop.json --max-elapsed-s 2.0 --trend-out bench_trend.jsonl || true
python scripts/plot_bench_trend.py --in bench_trend.jsonl --out bench_trend.png || true
echo "Repro complete. Outputs: feasibility_gates_report.json, production_kpi.json, bench_step_loop.json, bench_trend.png"