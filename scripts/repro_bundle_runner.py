#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    py = sys.executable
    # Best-effort sequence mirroring CI
    run([py, "scripts/demo_runner.py", "--scenario", "examples/scenario_min.json", "--steps", "10", "--dt", "1e-3", "--seed", "123"])
    run([py, "scripts/generate_feasibility_report.py", "--gamma-series", (root/"datasets/gamma_series.json").read_text(), "--dt", "0.002", "--b-series", (root/"datasets/b_field_series.json").read_text(), "--E-mag", (root/"datasets/E_mag.json").read_text(), "--out", "feasibility_gates_report.json", "--scenario-id", "repro", "--require-yield", "--require-fom"])
    run([py, "scripts/production_kpi.py", "--feasibility", "feasibility_gates_report.json", "--metrics", "metrics.json", "--uq", "uq_optimized.json", "--out", "production_kpi.json"])
    run([py, "scripts/bench_step_loop.py", "--steps", "200", "--dt", "1e-4", "--out", "bench_step_loop.json"])
    run([py, "scripts/performance_budget.py", "--bench", "bench_step_loop.json", "--max-elapsed-s", "2.0", "--trend-out", "bench_trend.jsonl"])
    print(json.dumps({"done": True}))


if __name__ == "__main__":
    main()
