from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

import numpy as np


def _grad(field: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    f = np.asarray(field, dtype=float)
    dfx = 0.5 * (np.roll(f, -1, axis=1) - np.roll(f, 1, axis=1))
    dfy = 0.5 * (np.roll(f, -1, axis=0) - np.roll(f, 1, axis=0))
    return dfx, dfy


def compute_gamma(rho: np.ndarray, p: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Estimate Γ ~ |∇p × ∇ρ| / max(ρ^2, eps). 2D scalar proxy via out-of-plane cross component.

    Args:
        rho: mass density (units arbitrary), must be non-negative.
        p: pressure-like scalar field.
        eps: small stabilizer to avoid divide-by-zero.
    """
    rho_arr = np.asarray(rho, dtype=float)
    if (rho_arr < 0).any():
        raise ValueError("rho must be non-negative")
    drx, dry = _grad(rho_arr)
    dpx, dpy = _grad(p)
    cross = dpx * dry - dpy * drx
    denom = np.maximum(eps, rho_arr ** 2)
    return np.abs(cross) / denom


def stability_duration(
    gamma_series: np.ndarray,
    dt: float,
    threshold: float,
    min_duration: float,
) -> bool:
    """True if Γ >= threshold holds continuously for at least min_duration seconds."""
    gamma_series = np.asarray(gamma_series, dtype=float)
    needed = int(np.ceil(min_duration / max(dt, 1e-12)))
    mask = gamma_series >= threshold
    if needed <= 1:
        return bool(mask.any())
    run = 0
    for m in mask:
        if m:
            run += 1
            if run >= needed:
                return True
        else:
            run = 0
    return False


def confinement_efficiency_estimator(xi: float, b_field_ripple_pct: float) -> float:
    """Heuristic efficiency in [0,1] with mild penalties for ripple and large ξ.

    Args:
        xi: Bennett profile parameter ξ (dimensionless)
        b_field_ripple_pct: RMS fluctuation fraction (e.g., 0.005 for 0.5%)
    """
    base = 0.96
    ripple_pen = 2.0 * max(0.0, float(b_field_ripple_pct))
    xi_pen = 0.01 * np.tanh(abs(float(xi)) / 5.0)
    return float(np.clip(base - ripple_pen - xi_pen, 0.0, 1.0))


def antiproton_yield_estimator(
    n_cm3: float,
    Te_eV: float,
    params: Optional[Dict[str, float]] = None,
) -> float:
    """Yield rate density [1/(cm^3 s)] estimator.

    Default model (legacy): k0 * n * Te^alpha.
    Threshold model (set params["model"]="threshold"): k0 * n * max(Te - E_th, 0)^alpha.

    Args:
        n_cm3: electron density [cm^-3], clamped to >=0
        Te_eV: electron temperature [eV], clamped to >0
        params: optional dict with keys:
            - model: "threshold" to use threshold-inspired form
            - k0 or sigma0: prefactor [1/(cm^3 s eV^alpha)]
            - alpha_T: temperature exponent
            - E_th: threshold temperature [eV]
    """
    p = params or {}
    model = str(p.get("model", "legacy"))
    k0 = float(p.get("k0", p.get("sigma0", 1e-12)))
    alpha = float(p.get("alpha_T", 0.25))
    n = max(0.0, float(n_cm3))
    T = max(1e-12, float(Te_eV))
    if model == "threshold":
        E_th = float(p.get("E_th", 0.0))
        excess = max(0.0, T - E_th)
        return max(0.0, k0 * n * (excess ** alpha))
    # legacy
    return max(0.0, k0 * n * (T ** alpha))


def save_feasibility_gates_report(path: str, data: Dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
