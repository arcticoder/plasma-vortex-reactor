# Metrics Guide

This guide explains how each metric is computed and where it is recorded.

- Gamma (Γ) stability:
  - Computation: Use `reactor.analysis.windowed_gamma` and `reactor.metrics.stability_duration`.
  - Recording: Included in feasibility report (`scripts/generate_feasibility_report.py`) under `gamma_stats`.
- Confinement efficiency:
  - Computation: `reactor.metrics.confinement_efficiency_estimator(xi, b_field_ripple_pct)`.
  - Recording: Emitted as `confinement_achieved` timeline event when threshold is met.
- B-field stability:
  - Computation: `reactor.analysis.b_field_rms_fluctuation(series)`.
  - Recording: Included in feasibility report under `b_stats`.
- Plasma density attainment:
  - Computation: `reactor.analysis.estimate_density_from_em(E_mag, ...)`.
  - Recording: `density_stats` in feasibility report.
- Energy per antiproton:
  - Computation: `reactor.energy.EnergyLedger.energy_per_antiproton()`.
  - Recording: Not persisted by default; include in economic report (`reactor.analysis.write_economic_report`).
- Channel energy allocation:
  - Computation: `reactor.energy.EnergyLedger.add_channel_energy` and `merge_ledgers`.
  - Recording: `scripts/generate_channel_report.py` emits `channel_report.json`.

See `docs/ARTIFACT_SCHEMA.md` for artifact keys and `docs/RUNBOOK.md` for end-to-end steps.
