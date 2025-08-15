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
