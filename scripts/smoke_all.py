#!/usr/bin/env python
from __future__ import annotations

import subprocess
import sys


def sh(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    return subprocess.call(cmd)


def main():
    code = 0
    code |= sh(
        [
            sys.executable,
            "scripts/demo_runner.py",
            "--scenario",
            "examples/scenario_min.json",
            "--steps",
            "10",
            "--dt",
            "1e-3",
        ]
    )
    code |= sh(
        [
            sys.executable,
            "scripts/generate_feasibility_report.py",
            "--gamma-series",
            open("datasets/gamma_series.json").read(),
            "--dt",
            "0.002",
            "--b-series",
            open("datasets/b_field_series.json").read(),
            "--E-mag",
            open("datasets/E_mag.json").read(),
            "--out",
            "feasibility_gates_report.json",
            "--scenario-id",
            "smoke",
        ]
    )
    code |= sh([sys.executable, "scripts/uq_demo.py", "--samples", "10", "--seed", "123"])  
    sys.exit(code)


if __name__ == "__main__":
    main()
