#!/usr/bin/env python3
"""Debug KPI trend plot: log-scale y, annotated, colored by stability.

Writes to `artifacts/kpi_trend.png` (overwrites) for quick inspection.
"""
from __future__ import annotations

import json
import glob
import os
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load_artifacts(pattern: str):
    files = sorted(glob.glob(pattern))
    rows = []
    for p in files:
        try:
            d = json.load(open(p))
        except Exception:
            continue
        # coerce numeric fom
        f = d.get('fom')
        try:
            fval = float(f) if f is not None else None
        except Exception:
            fval = None
        rows.append((p, fval, bool(d.get('stable', False)), d))
    return rows


def make_plot(rows, out_path: str):
    if not rows:
        print('no data to plot')
        return 1
    xs = list(range(len(rows)))
    ys = [abs(r[1]) if (r[1] is not None and abs(r[1])>0) else 1e-30 for r in rows]
    colors = ['green' if r[2] else 'red' for r in rows]
    labels = [Path(r[0]).name for r in rows]

    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(xs, ys, '-o', color='tab:blue', linewidth=1.5, markersize=6)
    for xi, yi, c, lab in zip(xs, ys, colors, labels):
        ax.scatter([xi], [yi], color=c, s=120, edgecolor='k', zorder=3)
        ax.text(xi, yi * 1.3, lab, rotation=30, fontsize=7, ha='center', va='bottom')

    ax.set_yscale('log')
    ax.set_xlabel('Run (sorted filenames)')
    ax.set_ylabel('abs(FOM) (log scale)')
    ax.set_title('KPI Trend (debug)')
    ax.grid(True, which='both', ls='--', alpha=0.4)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=45, fontsize=8)
    fig.tight_layout()
    os.makedirs(Path(out_path).parent, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print('wrote', out_path, 'points=', len(xs))
    return 0


def main():
    pattern = 'artifacts/production_kpi_*.json'
    out = 'artifacts/kpi_trend.png'
    rows = load_artifacts(pattern)
    rc = make_plot(rows, out)
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
