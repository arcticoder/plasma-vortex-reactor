# Ablation Study: Ripple Control ON vs OFF

We compare the stability probability metric with ripple control enabled vs disabled.

- CLI: `pv-ablation-ripple --n 20000 --ripple-pct 0.005`
- Output: `ablation_ripple.json`

Result fields:
- `on`: stability probability with control enabled
- `off`: stability probability without control
- `delta`: difference (on - off)

This ablation isolates the effect of the dynamic ripple adjustment and is referenced in the paper.
