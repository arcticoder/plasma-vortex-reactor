#!/usr/bin/env python
"""
Deprecated: progress dashboard generator has been removed.
This stub remains to avoid breaking external references. It exits 0 and writes no files.
"""
from __future__ import annotations
import sys

def main() -> int:
    print("progress dashboard is deprecated; use scripts/plot_kpi_trend.py instead", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
