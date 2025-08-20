from __future__ import annotations

from typing import Dict, Iterable, Sequence

import numpy as np


def stability_variance(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.var(arr))


def windowed_gamma(series: Iterable[float], window_size: int) -> Dict[str, np.ndarray]:
    arr = np.asarray(list(series), dtype=float)
    w = int(window_size)
    if w <= 0:
        raise ValueError("window_size must be >= 1")
    if arr.size < w:
        return {
            "min": np.array([], dtype=float),
            "max": np.array([], dtype=float),
            "mean": np.array([], dtype=float),
        }
    means = (np.convolve(arr, np.ones(w), mode="valid") / w)
    mins = np.array([np.min(arr[i:i+w]) for i in range(arr.size - w + 1)], dtype=float)
    maxs = np.array([np.max(arr[i:i+w]) for i in range(arr.size - w + 1)], dtype=float)
    return {"min": mins, "max": maxs, "mean": means}


def ema(series: Iterable[float], alpha: float) -> np.ndarray:
    """Exponential moving average with smoothing factor alpha in (0,1]."""
    arr = np.asarray(list(series), dtype=float)
    if arr.size == 0:
        return arr
    a = float(alpha)
    if not (0 < a <= 1):
        raise ValueError("alpha must be in (0,1]")
    out = np.empty_like(arr)
    out[0] = arr[0]
    for i in range(1, arr.size):
        out[i] = a*arr[i] + (1-a)*out[i-1]
    return out


def stability_probability(series: Iterable[float], threshold: float = 140.0, steps: int | None = None) -> float:
    """Probability that series values are >= threshold over the given number of steps.

    If steps is None, use the full series length.
    """
    arr = np.asarray(list(series), dtype=float)
    if arr.size == 0:
        return 0.0
    N = int(steps) if steps is not None else arr.size
    N = max(1, min(N, arr.size))
    sel = arr[:N]
    stable_steps = int(np.sum(sel >= float(threshold)))
    return float(stable_steps) / float(N)


def plot_stability_curve(time_ms: Sequence[float], gamma_series: Sequence[float], out_png: str) -> None:
    """Plot Γ vs time (ms) to PNG."""
    from .plotting import _mpl  # lazy import matplotlib

    plt = _mpl()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(list(time_ms), list(gamma_series), color="royalblue")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Γ")
    ax.set_title("Stability (Γ) vs Time")
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


def plot_stability_ripple(
    ripples: Sequence[float],
    probabilities: Sequence[float],
    out_png: str,
    gate_y: float | None = None,
    gate_label: str | None = None,
) -> None:
    """Plot stability probability vs. ripple fraction to PNG.

    Optional gate_y draws a horizontal gate line with an annotation.
    """
    import numpy as _np

    from .plotting import _mpl
    r = _np.asarray(list(ripples), dtype=float)
    p = _np.asarray(list(probabilities), dtype=float)
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(r, p, color="royalblue")
    ax.set_xlabel("Ripple (fraction)")
    ax.set_ylabel("Stability Probability")
    ax.set_title("Stability vs. Ripple")
    if gate_y is not None:
        y = float(gate_y)
        ax.axhline(y, color="#d73a49" if y > 0 else "#999", linestyle="--", linewidth=1.0)
        if gate_label:
            # place the label at the right side
            ax.text(
                0.98,
                y,
                str(gate_label),
                color="#d73a49",
                ha="right",
                va="bottom",
                fontsize=9,
                transform=ax.get_yaxis_transform(),
            )
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
