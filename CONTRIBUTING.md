# Contributing

Thanks for contributing! Please follow these basics:

- Tests: add unit tests for new behavior. Run with `make test`.
- Lint: keep code clean with Ruff. Run `make lint`. CI enforces it.
- Types: aim for type hints; run `make types` (mypy) locally.
- CI: ensure workflows remain green. Prefer optional deps for plotting.
- Docs: update `docs/*` for metrics/gates and `README.md` when adding scripts.

PRs that change public behavior should include updates to tests and docs.

## Testing

- Use `pytest -q` for the fast suite.
- Markers:
	- `@pytest.mark.slow` for heavy sweeps/plots.
	- `@pytest.mark.production` for production-scale validations.
	- `@pytest.mark.hardware` for hardware adapter tests.

## CLI Entrypoints (pv-*)

After installing the package (editable install is fine), the following are available:

- `pv-dashboard`, `pv-kpi`, `pv-run-report`
- `pv-plot-fom`, `pv-plot-stability`, `pv-sweep-time`, `pv-sweep-dyn`
- `pv-hw-runner`, `pv-anomalies`, `pv-validate-schemas`
- `pv-snr`, `pv-bench`, `pv-cost-sweep`, `pv-snr-prop`, `pv-perf-budget`
