from __future__ import annotations

import json
from typing import Dict, Optional, Tuple, Any

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
    params: Optional[Dict[str, Any]] = None,
) -> float:
    """Yield rate density [1/(cm^3 s)] estimator.

    Supported models via params["model"]:
    - "physics" (pp cross-section model): σ_pp * n_e^2 * v_rel  (default σ_pp=1e-28 cm^2, v_rel=0.1c in cm/s)
    - "threshold": k0 * n * max(Te - E_th, 0)^alpha
    - "legacy" (default if unspecified): k0 * n * Te^alpha

    Args:
        n_cm3: electron density [cm^-3], clamped to >=0
        Te_eV: electron temperature [eV], clamped to >0 (unused in physics model)
        params: optional dict with keys depending on model
    """
    p = params or {}
    model = str(p.get("model", "legacy"))
    n = max(0.0, float(n_cm3))
    T = max(1e-12, float(Te_eV))

    if model == "physics":
        # Physics-based proxy: Yield = sigma_pp * n_e^2 * v_rel
        # Defaults: sigma_pp ~ 1e-28 cm^2, v_rel ~ 0.1c (in cm/s)
        sigma_pp = float(p.get("sigma_pp", 1e-28))  # [cm^2]
        c_cm_s = 3.0e10
        v_rel = float(p.get("v_rel", 0.1 * c_cm_s))  # [cm/s]
        return float(sigma_pp * (n ** 2) * v_rel)

    if model == "threshold":
        k0 = float(p.get("k0", p.get("sigma0", 1e-12)))
        alpha = float(p.get("alpha_T", 0.25))
        E_th = float(p.get("E_th", 0.0))
        excess = max(0.0, T - E_th)
        return max(0.0, k0 * n * (excess ** alpha))

    # legacy
    k0 = float(p.get("k0", p.get("sigma0", 1e-12)))
    alpha = float(p.get("alpha_T", 0.25))
    return max(0.0, k0 * n * (T ** alpha))


def pulsed_yield_enhancement(yield_base: float, I_beam: float = 1e6, tau_pulse: float = 1e-9) -> float:
    """Apply a pulsed-beam enhancement to a base yield.

    Heuristic scaling: boost ∝ I_beam^2 / tau_pulse (normalized by 1e12 for stability).
    Returns: enhanced yield (same units as input yield_base).
    """
    boost = (max(0.0, float(I_beam)) ** 2 / max(1e-30, float(tau_pulse))) / 1e12
    return float(max(0.0, float(yield_base)) * boost)


def channel_fom(yield_rate: float, E_channel_J: float) -> float:
    """Per-channel Figure of Merit proxy: Yield / (Energy × CostProxy).

    Uses a simple cost proxy of 1e8 to keep magnitudes tractable and align with tests.
    """
    Ej = max(1e-30, float(E_channel_J))
    return float(yield_rate) / (Ej * 1e8)


def total_fom(yield_rate: float, E_total_J: float) -> float:
    Ej = max(1e-30, float(E_total_J))
    return float(yield_rate) / (Ej * 1e8)


def log_yield(n_e_cm3: float, Te_eV: float, path: str = "progress.ndjson") -> None:
    """Compute and append a yield_calculated event to NDJSON log."""
    from .logging_utils import append_event

    y = antiproton_yield_estimator(n_e_cm3, Te_eV, {"model": "physics"})
    append_event(
        path,
        event="yield_calculated",
        status="ok" if y >= 1e8 else "warn",
        details={"yield_cm3_s": float(y), "n_e_cm3": float(n_e_cm3), "Te_eV": float(Te_eV)},
    )


def log_density(n_e_cm3: float, path: str = "progress.ndjson") -> None:
    """Append a density_check event to NDJSON log with simple pass/fail at 1e20 cm^-3."""
    from .logging_utils import append_event

    n_m3 = float(n_e_cm3) * 1e6
    append_event(
        path,
        event="density_check",
        status="ok" if n_m3 >= 1e26 else "fail",
        details={"n_m3": n_m3},
    )


def log_fom(yield_rate: float, E_total_J: float, path: str = "progress.ndjson") -> None:
    """Compute total FOM and append to NDJSON log."""
    from .logging_utils import append_event

    f = total_fom(yield_rate, E_total_J)
    append_event(
        path,
        event="fom_calculated",
        status="ok" if f >= 0.1 else "fail",
        details={"fom": float(f)},
    )


def log_stability(gamma: float, path: str = "progress.ndjson") -> None:
    from .logging_utils import append_event

    append_event(
        path,
        event="stability_check",
        status="ok" if float(gamma) >= 140.0 else "fail",
        details={"gamma": float(gamma)},
    )


def log_fom_edge(yield_rate: float, E_total_J: float, path: str = "progress.ndjson") -> None:
    from .logging_utils import append_event

    f = total_fom(yield_rate, E_total_J)
    append_event(path, event="fom_edge_check", status=("ok" if f >= 0.1 else "fail"), details={"fom": float(f), "yield": float(yield_rate), "E_total": float(E_total_J)})


def save_feasibility_gates_report(path: str, data: Dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def plot_fom_vs_yield(yields: np.ndarray, foms: np.ndarray, out_png: str) -> None:
    """Scatter plot FOM vs Yield to PNG."""
    from .plotting import _mpl

    ys = np.asarray(yields, dtype=float)
    fs = np.asarray(foms, dtype=float)
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(ys, fs, color="goldenrod")
    ax.set_xlabel("Yield (cm⁻³ s⁻¹)")
    ax.set_ylabel("FOM")
    ax.set_title("FOM vs Yield")
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
