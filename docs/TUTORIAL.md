# Contributor Tutorial

This short tutorial shows how to run the demo and build core artifacts locally.

- Create a virtual environment and install requirements.
- Run the demo runner on the minimal scenario.

Steps:

1. python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
2. python scripts/demo_runner.py --scenario examples/scenario_min.json --steps 5 --dt 1e-3 --seed 1
3. python scripts/plot_kpi_trend.py --out artifacts/kpi_trend.png
4. python scripts/plot_dynamic_ripple_time.py --from-csv data/full_sweep_with_dynamic_ripple.csv --out artifacts/dynamic_ripple_time.png

Notes:
- If the CSV is missing, the dynamic ripple plot script will attempt to generate it using the parameter sweep utility.

Expected outputs: timeline.ndjson, feasibility_gates_report.json, artifacts/kpi_trend.png.
