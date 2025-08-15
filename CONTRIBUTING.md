# Contributing

Thanks for contributing! Please follow these basics:

- Tests: add unit tests for new behavior. Run with `make test`.
- Lint: keep code clean with Ruff. Run `make lint`. CI enforces it.
- Types: aim for type hints; run `make types` (mypy) locally.
- CI: ensure workflows remain green. Prefer optional deps for plotting.
- Docs: update `docs/*` for metrics/gates and `README.md` when adding scripts.

PRs that change public behavior should include updates to tests and docs.
