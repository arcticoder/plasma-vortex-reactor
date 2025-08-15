from __future__ import annotations

"""Lightweight plotting helpers with optional matplotlib dependency.

Functions will no-op or raise a clear error if matplotlib is not available.
"""

from typing import Sequence, Optional


def _mpl():
    try:
        import matplotlib.pyplot as plt  # type: ignore
        return plt
    except Exception as e:  # pragma: no cover - environment-dependent
        raise RuntimeError("matplotlib is required for plotting but is not installed") from e


def quick_scatter(x: Sequence[float], y: Sequence[float], out_png: Optional[str] = None,
                  xlabel: str = "x", ylabel: str = "y", title: str = "") -> None:
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.scatter(list(x), list(y), s=12, alpha=0.7)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    fig.tight_layout()
    if out_png:
        fig.savefig(out_png, dpi=150)
    plt.close(fig)
