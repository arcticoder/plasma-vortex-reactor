from __future__ import annotations
import numpy as np


def simulate_b_field_ripple(n: int, base_T: float = 5.0, ripple_pct: float = 0.005, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(int(seed))
    noise = rng.normal(0.0, ripple_pct, size=int(n))
    series = base_T * (1.0 + noise)
    return series


def b_field_rms_fluctuation(series: np.ndarray) -> float:
    series = np.asarray(series, dtype=float)
    return float(np.std(series) / np.mean(series))


def estimate_density_from_em(E_mag: np.ndarray, gamma: float = 1.0, Emin: float = 0.0, ne_min: float = 0.0) -> np.ndarray:
    E_mag = np.asarray(E_mag, dtype=float)
    return gamma * np.clip(E_mag - Emin, 0.0, None) + ne_min
