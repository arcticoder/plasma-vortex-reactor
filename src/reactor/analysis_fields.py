from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from .plotting import _mpl  # lazy-import helper for matplotlib


def simulate_b_field_ripple(
    n: int,
    base_T: float = 5.0,
    ripple_pct: float = 0.005,
    seed: Optional[int] = None,
) -> np.ndarray:
    if seed is None:
        # use global RNG for reproducibility if previously seeded
        from .random_utils import get_rng
        rng = get_rng()
    else:
        rng = np.random.default_rng(int(seed))
    noise = rng.normal(0.0, ripple_pct, size=int(n))
    series = base_T * (1.0 + noise)
    return series


def b_field_rms_fluctuation(series: np.ndarray) -> float:
    series = np.asarray(series, dtype=float)
    return float(np.std(series) / np.mean(series))


def estimate_density_from_em(
    E_mag: np.ndarray,
    gamma: float = 1.0,
    Emin: float = 0.0,
    ne_min: float = 0.0,
) -> np.ndarray:
    E_mag = np.asarray(E_mag, dtype=float)
    return gamma * np.clip(E_mag - Emin, 0.0, None) + ne_min


def plot_b_field_ripple(time_ms: Sequence[float], ripple_series: Sequence[float], out_png: str) -> None:
    """Plot B-field ripple vs time (ms) to PNG."""
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(time_ms, ripple_series, color='crimson')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Ripple (fraction)')
    ax.set_title('B-Field Ripple')
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
