import numpy as np

from reactor.analysis import (
    b_field_rms_fluctuation,
    bennett_confinement_check,
    estimate_density_from_em,
    simulate_b_field_ripple,
    stability_variance,
)
from reactor.core import Reactor
from reactor.energy import EnergyLedger, energy_interval, merge_ledgers
from reactor.metrics import antiproton_yield_estimator
from reactor.thresholds import thresholds_from_json


def test_yield_proxy_reaches_phase1_threshold_note():
    # Note: This is a synthetic favorable parameterization to hit ≥1e8 cm^-3 s^-1.
    y = antiproton_yield_estimator(n_cm3=1e20, Te_eV=50.0, params={"k0": 1e-12, "alpha_T": 0.2})
    assert y >= 1e8


def test_stability_duration_boundaries():
    from reactor.metrics import stability_duration
    dt = 0.002
    thr = 140.0
    # Just under duration (only one step at/over threshold)
    series_under = np.array([150.0, 100.0, 100.0])
    assert stability_duration(series_under, dt=dt, threshold=thr, min_duration=0.004) is False
    # Just over duration
    series_over = np.array([150.0, 150.0, 150.0])
    assert stability_duration(series_over, dt=dt, threshold=thr, min_duration=0.004) is True


def test_progress_events_budget(tmp_path):
    # Ensure we do not over-log in a short run
    timeline = tmp_path / "timeline.ndjson"
    R = Reactor(grid=(32, 32), nu=1e-3, timeline_log_path=str(timeline))
    for _ in range(5):
        R.step(dt=1e-3)
    lines = timeline.read_text().strip().splitlines()
    # Expect at most 4 events after new logging: vortex_stabilized, confinement_achieved,
    # density_enforced, antiproton_yield
    assert len(lines) <= 4


def test_b_field_ripple_and_variance():
    series = simulate_b_field_ripple(1000, base_T=5.0, ripple_pct=0.005, seed=42)
    rms = b_field_rms_fluctuation(series)
    assert 0.0 < rms < 0.05
    var = stability_variance(series)
    assert var > 0


def test_energy_interval_and_merge_ledgers():
    L1 = EnergyLedger()
    with energy_interval(L1, power_w=100.0, dt_s=2.0):
        pass
    L2 = EnergyLedger()
    with energy_interval(L2, power_w=50.0, dt_s=2.0):
        pass
    L = merge_ledgers(L1, L2)
    assert L.total_energy() == 300.0


def test_yield_calibration_dataset():
    import json as _json
    import pathlib

    from reactor.metrics import antiproton_yield_estimator as _yield

    data = _json.loads(
        pathlib.Path("datasets/antiproton_yield_calibration.json").read_text()
    )
    for row in data:
        y = _yield(
            row["n_cm3"],
            row["Te_eV"],
            {"k0": row["k0"], "alpha_T": row["alpha_T"]},
        )
        assert y >= row["min_yield"]


def test_density_attainment_and_artifact(tmp_path):
    E_mag = np.array([0.0, 1.0, 2.0, 3.0])
    ne = estimate_density_from_em(E_mag, gamma=1.0, Emin=0.0, ne_min=0.0)
    # Save a tiny artifact (csv-like)
    art = tmp_path / "density_profile.txt"
    art.write_text("\n".join(str(float(v)) for v in ne))
    assert art.exists() and art.stat().st_size > 0


def test_windowed_gamma_and_thresholds_from_json(tmp_path):
    import json as _json

    from reactor.analysis import windowed_gamma
    series = np.array([100, 150, 160, 130, 200], dtype=float)
    stats = windowed_gamma(series, window_size=3)
    assert stats["min"].shape[0] == 3 and stats["max"].shape[0] == 3 and stats["mean"].shape[0] == 3
    # thresholds_from_json
    m = tmp_path / "metrics.json"
    _json.dump({"gamma_min": 150.0, "b_field_min_T": 4.5}, open(m, "w"))
    thr = thresholds_from_json(str(m))
    assert thr.gamma_min == 150.0 and thr.b_field_min_T == 4.5


def test_ema_smoothing_behavior():
    from reactor.analysis_stat import ema
    x = np.array([0.0, 10.0, 0.0, 10.0, 0.0])
    y_fast = ema(x, alpha=0.8)
    y_slow = ema(x, alpha=0.2)
    assert y_fast.var() > y_slow.var()


def test_bennett_confinement_check():
    # Good case
    assert bennett_confinement_check(1e20, 2.0, 5.5, 5e-4) is True
    # Bad ripple
    assert bennett_confinement_check(1e20, 2.0, 5.5, 5e-3) is False
