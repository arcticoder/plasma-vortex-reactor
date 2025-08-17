# Operating Envelope Frontier

The operating envelope is computed via `scripts/envelope_sweep.py` and saved to:

- `operating_envelope.json` (grid of n, T, FOM)
- `operating_envelope.csv`
- `operating_envelope_frontier.json` (top-k frontier)
- `operating_envelope.png` (contour or scatter-colored plot)

Use the frontier to select scenarios for further validation.# Operating Envelope

This figure summarizes the feasible operating space as a function of density n (cm^-3) and temperature T (eV), colored by the production Figure of Merit (FOM).

How to generate locally:

- CLI: `pv-envelope --n-points 30 --n-min 1e19 --n-max 1e21 --t-min 5 --t-max 50`
- Outputs: `operating_envelope.json`, `operating_envelope.csv`, `operating_envelope.png`

Interpretation:

- Higher FOM regions indicate more favorable yield-to-energy ratios.
- We present contours across decades of density using a log x-axis.
- This supports our KPI gates and dynamic ripple results in the paper.
