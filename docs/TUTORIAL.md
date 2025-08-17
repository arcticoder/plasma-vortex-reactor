# Contributor Tutorial

This short tutorial shows how to run the demo and build core artifacts locally.

- Create a virtual environment and install requirements.
- Run the demo runner on the minimal scenario.
- Generate the progress dashboard.

Steps:

1. python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
2. python scripts/demo_runner.py --scenario examples/scenario_min.json --steps 5 --dt 1e-3 --seed 1
3. python scripts/generate_progress_dashboard.py --docs-dir docs --out progress_dashboard.html --fom-trend

Expected outputs: timeline.ndjson, feasibility_gates_report.json, progress_dashboard.html.
