# Runbook: Demo → Feasibility → UQ → Reporting

1. Demo with timeline logging:
   ```
   python scripts/demo_runner.py --scenario examples/scenario_min.json --steps 10 --dt 1e-3
   ```
2. Generate feasibility report:
   ```
   python scripts/generate_feasibility_report.py --gamma-series "[150,150,150,120]" --dt 0.002 \
     --b-series "[5,5.01,4.99,5.02]" --E-mag "[0,1,2,3]" --out feasibility_gates_report.json --scenario-id demo-1 --fail-on-gate
   ```
3. UQ run (programmatic): use `reactor.uq.run_uq_sampling` and save results to `uq_results.json`.
4. Reporting: see `docs/ARTIFACT_SCHEMA.md` for artifact structures.

## Operational Artifacts

- feasibility_gates_report.json: Feasibility gates and reasons
- timeline.ndjson: Event stream from demos/runs
- integrated_report.json: Merged feasibility + UQ + sweep heads
- production_kpi.json: Key production KPIs and summary
- calibration.json: Ripple alpha calibration from dynamic sweep
- time_to_metrics.json/png: Time to reach yield/FOM targets
- progress_dashboard.html: HTML snapshot of roadmap/progress/UQ/VnV

### Artifact Generation Cheatsheet

- Integrated report: `python scripts/run_report.py --feasibility feasibility_gates_report.json --timeline-summary timeline_summary.json --uq uq_optimized.json --integrated-out integrated_report.json`
- Dashboard: `python scripts/generate_progress_dashboard.py --docs-dir docs --out progress_dashboard.html`

### Anomaly Handling and Dashboard Usage

- Generate synthetic anomalies: `python scripts/generate_timeline_anomalies.py --n 20 --out docs/timeline_anomalies.ndjson` (or `pv-anomalies`).
- The dashboard tolerates missing files and malformed lines, showing counts and the 10 most recent items.
- Use the navbar for quick jumps and the ok/warn/fail filters to toggle severities.
