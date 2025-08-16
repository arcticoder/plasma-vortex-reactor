# Operating Envelope

This figure summarizes the feasible operating space as a function of density n (cm^-3) and temperature T (eV), colored by the production Figure of Merit (FOM).

How to generate locally:

- CLI: `pv-envelope --n-points 30 --n-min 1e19 --n-max 1e21 --t-min 5 --t-max 50`
- Outputs: `operating_envelope.json`, `operating_envelope.csv`, `operating_envelope.png`

Interpretation:

- Higher FOM regions indicate more favorable yield-to-energy ratios.
- We present contours across decades of density using a log x-axis.
- This supports our KPI gates and dynamic ripple results in the paper.
