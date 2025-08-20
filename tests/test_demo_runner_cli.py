import subprocess
import sys


def test_demo_runner_enforce_density(tmp_path):
    tl = tmp_path / "timeline.ndjson"
    code = subprocess.call(
        [
            sys.executable,
            "scripts/demo_runner.py",
            "--scenario",
            "examples/scenario_min.json",
            "--steps",
            "5",
            "--dt",
            "1e-3",
            "--seed",
            "5",
            "--timeline-log",
            str(tl),
            "--enforce-density",
        ]
    )
    assert code == 0
    if tl.exists():
        lines = tl.read_text().strip().splitlines()
        assert len(lines) >= 1
