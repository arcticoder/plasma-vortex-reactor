from __future__ import annotations

import json
import subprocess
from pathlib import Path


def _run(cmd: list[str]) -> tuple[int, str, str]:
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr


def test_seed_determinism_envelope(tmp_path: Path) -> None:
    here = Path(__file__).resolve().parents[1]
    out1 = tmp_path/"env1.json"
    out2 = tmp_path/"env2.json"
    cmd = [
        "python", str(here/"scripts"/"envelope_sweep.py"),
        "--n-points","5","--seed","123",
        "--out-json", str(out1),
    ]
    rc,_,_ = _run(cmd)
    assert rc == 0
    cmd[-1] = str(out2)
    rc,_,_ = _run(cmd)
    assert rc == 0
    assert out1.read_text() == out2.read_text()


def test_seed_determinism_snr(tmp_path: Path) -> None:
    here = Path(__file__).resolve().parents[1]
    out1 = tmp_path/"snr1.json"
    out2 = tmp_path/"snr2.json"
    cmd = ["python", str(here/"scripts"/"snr_propagation.py"), "--seed", "7", "--out-json", str(out1)]
    rc,_,_ = _run(cmd)
    assert rc == 0
    cmd[-1] = str(out2)
    rc,_,_ = _run(cmd)
    assert rc == 0
    assert json.loads(out1.read_text()) == json.loads(out2.read_text())
