from __future__ import annotations
from typing import Iterable, Dict
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
        return {"min": np.array([], dtype=float), "max": np.array([], dtype=float), "mean": np.array([], dtype=float)}
    means = (np.convolve(arr, np.ones(w), mode="valid") / w)
    mins = np.array([np.min(arr[i:i+w]) for i in range(arr.size - w + 1)], dtype=float)
    maxs = np.array([np.max(arr[i:i+w]) for i in range(arr.size - w + 1)], dtype=float)
    return {"min": mins, "max": maxs, "mean": means}
