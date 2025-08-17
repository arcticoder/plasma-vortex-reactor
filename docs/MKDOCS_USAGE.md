# MkDocs usage

This repository uses MkDocs with the Material theme and mkdocstrings for API docs.

- Config file: `mkdocs.yml`
- Docs live under `docs/`
- API page: `docs/api.md` (driven by mkdocstrings for the `reactor` package)

## Quick start

- Build site locally (serves at http://127.0.0.1:8000 by default):
  - mkdocs serve
- Build static site:
  - mkdocs build

The CI builds the site and uploads it to GitHub Pages. Artifacts are collected from `artifacts/` and linked where relevant.

## mkdocs.yml reference

Key sections in `mkdocs.yml`:

- site_name: Title of the site
- nav: Navigation tree; points to files under `docs/`
- theme: Using `material`
- plugins:
  - search
  - mkdocstrings (Python handler)

