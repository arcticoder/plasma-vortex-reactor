from __future__ import annotations
import json
from typing import Dict, Any, Iterable
import numpy as np


def stability_variance(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.var(arr))


def simulate_b_field_ripple(n: int, base_T: float = 5.0, ripple_pct: float = 0.005, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, ripple_pct, size=int(n))
    series = base_T * (1.0 + noise)
    return series


def b_field_rms_fluctuation(series: np.ndarray) -> float:
    series = np.asarray(series, dtype=float)
    return float(np.std(series) / np.mean(series))


def estimate_density_from_em(E_mag: np.ndarray, gamma: float = 1.0, Emin: float = 0.0, ne_min: float = 0.0) -> np.ndarray:
    """Placeholder microwave-inspired density: ne = gamma * max(E - Emin, 0) + ne_min."""
    E_mag = np.asarray(E_mag, dtype=float)
    return gamma * np.clip(E_mag - Emin, 0.0, None) + ne_min


def write_economic_report(path: str, energy_J: float, n_pbar: float, price_per_unit: float, overhead_cost: float) -> Dict[str, Any]:
    revenue = n_pbar * price_per_unit
    cost = overhead_cost + energy_J  # simple proxy: energy_J stands for energy cost units
    fom = (revenue / cost) if cost > 0 else float('inf')
    payload = {
        "energy_J": energy_J,
        "n_pbar": n_pbar,
        "price_per_unit": price_per_unit,
        "overhead_cost": overhead_cost,
        "revenue": revenue,
        "total_cost": cost,
        "FOM": fom,
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
    return payload
