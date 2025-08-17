from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_pv_envelope_monotonicity(tmp_path: Path) -> None:
    here = Path(__file__).resolve().parents[1]
    env_json = tmp_path / "env.json"
    env_csv = tmp_path / "env.csv"
    env_png = tmp_path / "env.png"
    # fewer points for quick check
    cmd = [
        "python",
        str(here / "scripts" / "envelope_sweep.py"),
        "--n-points",
        "5",
        "--n-min",
        "1e20",
        "--n-max",
        "1e20",
        "--t-min",
        "10.0",
        "--t-max",
        "30.0",
        "--out-json",
        str(env_json),
        "--out-csv",
        str(env_csv),
        "--out-png",
        str(env_png),
    ]
    res = subprocess.run(cmd, capture_output=True)
    assert res.returncode == 0
    data = json.loads(env_json.read_text())
    grid = data.get("grid", [])
    # Fixed n, increasing T should not decrease legacy yield-based FOM strictly; allow ties
    # Extract FOM sequence ordered by T
    rows = sorted(grid, key=lambda r: float(r["Te_eV"]))
    foms = [float(r["fom"]) for r in rows]
    for a, b in zip(foms, foms[1:]):
        assert b >= a - 1e-12
