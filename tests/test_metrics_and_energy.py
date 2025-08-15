import json
import numpy as np

from reactor.metrics import (
    compute_gamma,
    stability_duration,
    confinement_efficiency_estimator,
    antiproton_yield_estimator,
    save_feasibility_gates_report,
)
from reactor.energy import EnergyLedger, fom
from reactor.plasma import debye_length
from reactor.logging_utils import append_event
from reactor.uq import run_uq_sampling
from reactor.thresholds import Thresholds


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
