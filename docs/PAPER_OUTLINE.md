# Paper Outline (Draft)

Title: Plasma Vortex Reactor: CI-validated Modeling Pipeline with Stability KPI Gates and Dynamic Ripple Control

Abstract:
- Problem framing and contribution summary.
- CI-enforced performance and artifact reproducibility.

1. Introduction
- Motivation: stability and production yield in compact plasma vortex reactors.
- Prior art and gaps.
- Our contributions: KPI gates, dynamic ripple control, UQ, reproducible CI artifacts.

2. Methods
2.1. Reactor Model and Metrics
- Core equations (vorticity update, Debye length check), yield estimator, FOM.
- Stability metrics: variance, probability gates.
2.2. Dynamic Ripple Control
- B-field ripple simulation, adjustment law, calibration.
2.3. Parameter Sweeps and UQ
- Time/dynamic ripple sweeps; UQ optimize run.
2.4. CI and Reproducibility
- Performance budget, artifacts, schema validation, PR summaries.

3. Results
3.1. Operating Envelope
- FOM vs (n, T) with contours across orders of magnitude.
3.2. KPI Gates
- Stability probability vs ripple with horizontal gate annotations.
3.3. Dynamic Ripple Effect
- Ablation study (control ON vs OFF), delta improvement.
3.4. Benchmarks and Trends
- Micro-benchmark trendline and budget badge.

4. Discussion
- Sensitivity, limitations, and future extensions.

5. Reproducibility Package
- Minimal inputs and run scripts (bundle tarball), schema-validated outputs.

Appendix
- Schemas and CLI catalog.

## Figures List
- Fig 1: Operating envelope (operating_envelope.png)
- Fig 2: Stability vs ripple with gate (dynamic_stability_ripple.png)
- Fig 3: Production FOM vs yield (production_fom_yield.png)
- Fig 4: Time-to-stability/yield (time_to_metrics.png)
- Fig 5: Bench trend (bench_trend.png)
- Fig 6: Ablation ripple control (bar/line from ablation_ripple.json)
- Fig 7: B-field ripple visualization (b_field_ripple.png)
