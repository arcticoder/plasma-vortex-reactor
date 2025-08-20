import json

import numpy as np

from reactor.energy import (
    EnergyLedger,
    apply_lg_enhancement,
    fom,
    lg_mode_enhancement,
    merge_ledgers,
    optimize_lg_enhancement,
)
from reactor.logging_utils import append_event
from reactor.metrics import (
    antiproton_yield_estimator,
    compute_gamma,
    confinement_efficiency_estimator,
    save_feasibility_gates_report,
    stability_duration,
)
from reactor.plasma import debye_length
from reactor.thresholds import Thresholds
from reactor.uq import run_uq_sampling


def test_compute_gamma_and_duration():
    rho = np.ones((16, 16))
    p = np.zeros_like(rho)
    g = compute_gamma(rho, p)
    assert g.shape == rho.shape
    # build gamma_series with sustained threshold
    thr = Thresholds()
    series = np.array([10, 50, 200, 300, 50, 10], dtype=float)
    ok = stability_duration(series, dt=0.002, threshold=thr.gamma_min, min_duration=0.004)
    assert ok is True


def test_confinement_efficiency_and_yield_estimator():
    eff = confinement_efficiency_estimator(xi=2.0, b_field_ripple_pct=0.005)
    assert 0.0 <= eff <= 1.0
    y = antiproton_yield_estimator(n_cm3=1e20, Te_eV=10.0, params={"k0": 1e-20, "alpha_T": 0.1})
    assert y > 0


def test_energy_ledger_and_fom(tmp_path):
    el = EnergyLedger()
    el.add_power_sample(1000.0, 1.0)  # 1 kJ
    assert el.total_energy() == 1000.0
    assert el.energy_per_antiproton() == float("inf")
    el.set_yield(1e3)
    epa = el.energy_per_antiproton()
    assert 0 < epa < 1000.0
    f = fom(0.5, 100.0, 1000.0)
    assert np.isclose(f, 0.05)
    # channels
    el.add_channel_energy("coils", power_w=200.0, dt_s=2.0)
    el.add_channel_energy("heaters", power_w=100.0, dt_s=1.0)
    ch = el.channels()
    assert ch.get("coils", 0) > ch.get("heaters", 0)
    # merge channels
    el2 = EnergyLedger()
    el2.add_channel_energy("coils", power_w=50.0, dt_s=2.0)
    M = merge_ledgers(el, el2)
    assert M.channels()["coils"] >= ch["coils"]
    # enhancement reduces total reported energy
    base = el.total_energy()
    el.apply_enhancement(10.0)
    assert el.total_energy() == base / 10.0
    # reduction ratio utility
    assert EnergyLedger.total_energy_reduction(2700000000.0, 11150000.0) >= 242.0


def test_lg_mode_enhancement_and_context():
    L = EnergyLedger()
    L.add_power_sample(1000.0, 1.0)
    base = L.total_energy()
    f = lg_mode_enhancement(power_W=1000.0, l_index=2)
    assert f >= 1.0
    with apply_lg_enhancement(L, power_W=1000.0, l_index=2):
        assert L.total_energy() <= base / 1.0  # reduced or equal
    # restored
    assert L.total_energy() == base


def test_optimize_lg_enhancement():
    E_base = 1e12
    E_red = optimize_lg_enhancement(E_base, gamma=150.0, l_index=2)
    assert E_red <= 1e11


def test_metrics_gate_script(tmp_path):
    import json as _json
    import subprocess
    import sys
    metrics = {"gamma_min": 140.0}
    report_pass = {
        "stable": True,
        "gamma_ok": True,
        "b_ok": True,
        "dens_ok": True,
        "gamma_stats": {"gamma_max": 200},
    }
    report_fail = {
        "stable": False,
        "gamma_ok": False,
        "b_ok": True,
        "dens_ok": True,
        "gamma_stats": {"gamma_max": 100},
    }
    mp = tmp_path / "metrics.json"
    rp = tmp_path / "feas.json"
    mp.write_text(_json.dumps(metrics))
    rp.write_text(_json.dumps(report_pass))
    code = subprocess.call(
        [
            sys.executable,
            "scripts/metrics_gate.py",
            "--metrics",
            str(mp),
            "--report",
            str(rp),
        ]
    )
    assert code == 0
    rp.write_text(_json.dumps(report_fail))
    code2 = subprocess.call(
        [
            sys.executable,
            "scripts/metrics_gate.py",
            "--metrics",
            str(mp),
            "--report",
            str(rp),
        ]
    )
    assert code2 != 0


def test_plasma_debye_length():
    lam = debye_length(T_eV=10.0, n_m3=1e26)
    assert lam > 0


def test_logging_and_uq(tmp_path):
    logp = tmp_path / "progress.ndjson"
    append_event(str(logp), event="vortex_stabilized", status="ok", details={"rho": 1.0})
    data = logp.read_text().strip().splitlines()
    rec = json.loads(data[0])
    assert rec["event"] == "vortex_stabilized"

    # UQ run with trivial eval_fn
    def eval_fn(params):
        return {"score": params["a"] + params["b"]}

    out = run_uq_sampling(5, seed=123, param_ranges={"a": (0, 1), "b": (0, 1)}, eval_fn=eval_fn)
    assert out["n_samples"] == 5
    assert "means" in out and "score" in out["means"]

    # feasibility gates report
    rep = tmp_path / "feasibility_gates_report.json"
    save_feasibility_gates_report(str(rep), {"stable": True, "Gamma_min": 150.0})
    data = json.loads(rep.read_text())
    assert data["stable"] is True and data["Gamma_min"] >= 140
