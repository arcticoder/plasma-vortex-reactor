# Artifact Schema

This document enumerates minimal keys for generated artifacts.

## Timeline events (NDJSON)
Each line is a JSON object with:
- `event`: string, e.g., "vortex_stabilized", "confinement_achieved"
- `status`: string, e.g., "ok", "info"
- `details`: object (optional), key/value pairs with numeric or string metadata

## feasibility_gates_report.json
```
{
  "stable": bool,
  "gamma_ok": bool,
  "b_ok": bool,
  "dens_ok": bool,
  "gamma_stats": { "gamma_min": number, "gamma_max": number, "gamma_mean": number, "gamma_variance": number, "dt": number },
  "b_stats": { "b_mean_T": number, "b_rms_fraction": number },
  "density_stats": { "ne_max_cm3": number }
}
```

## uq_results.json
```
{
  "n_samples": int,
  "means": { "key": number, ... },
  "results": [ { "key": number, ... }, ... ]
}
```

## uq_production.json
Same structure as uq_results.json, generated with production-focused parameter ranges.

## full_sweep_with_time.csv
CSV with headers:
- n_e, T_e, B, xi, alpha, t, ripple, yield, E_total, fom, eta

## full_sweep_with_dynamic_ripple.csv
CSV with headers:
- n_e, T_e, B, xi, alpha, t, ripple_initial, ripple_dynamic, yield, E_total, fom, eta

## dynamic_stability_ripple.png
PNG scatter plot of stability probability vs ripple fraction.

## high_load_hardware_metrics.png
PNG time series of hardware metric under high-load conditions (synthetic or ingested).

## integrated_report.json
```
{
  "feasibility": { ... },
  "run_report": { ... },
  "uq": { ... },
  "uq_production": { ... },
  "sweeps": {
    "time": { "path": str, "n_rows": int, "rows": [ {csv_row...}, ... ] },
    "dynamic_ripple": { "path": str, "n_rows": int, "rows": [ {csv_row...}, ... ] }
  }
}
```
## progress_dashboard.html

- Produced by: `scripts/generate_progress_dashboard.py`
- Purpose: Quick HTML snapshot aggregating counts and recent items from docs/*.ndjson.
- Schema: HTML document (no strict JSON schema). Contains sections for:
  - roadmap.ndjson, roadmap-completed.ndjson
  - progress_log.ndjson, progress_log-completed.ndjson
  - UQ-TODO(.ndjson), UQ-TODO-RESOLVED(.ndjson)
  - VnV-TODO(.ndjson), VnV-TODO-RESOLVED(.ndjson)
  Each section includes a count and up to 10 most recent entries with titles/status.


## fom_report.json
```
{
  "energy_J": number,
  "n_pbar": number,
  "price_per_unit": number,
  "overhead_cost": number,
  "revenue": number,
  "total_cost": number,
  "FOM": number
}
```
