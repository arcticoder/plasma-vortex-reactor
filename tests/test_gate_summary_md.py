from __future__ import annotations

import json
from pathlib import Path


def test_gate_summary_md_snapshot(tmp_path: Path):
    rep = {
        "stable": True,
        "gamma_ok": True,
        "b_ok": False,
        "dens_ok": True,
    }
    out = tmp_path / "gate_summary.md"
    open(tmp_path / "feasibility_gates_report.json", "w", encoding="utf-8").write(json.dumps(rep))
    import subprocess
    import sys
    subprocess.check_call(
        [
            sys.executable,
            "scripts/gate_summary_md.py",
            "--report",
            str(tmp_path / "feasibility_gates_report.json"),
            "--out",
            str(out),
        ]
    )
    content = out.read_text(encoding="utf-8").strip()
    expected = "\n".join([
        "# Feasibility Gate Summary",
        "",
        "- Stable: ✅",
        "- Gamma OK: ✅",
        "- B-field OK: ❌",
        "- Density OK: ✅",
    ]).strip()
    assert content == expected
