from __future__ import annotations
import numpy as np
from typing import Optional, Dict


def bennett_profile(n0: float, xi: float, r: np.ndarray) -> np.ndarray:
    """n(r) = n0 * (1 + xi^2 * r^2)^(-2)."""
    r2 = np.asarray(r) ** 2
    return n0 * (1.0 + (xi * xi) * r2) ** -2


def vorticity_evolution(omega: np.ndarray, psi: np.ndarray, nu: float, dt: float,
                        forcing: Optional[np.ndarray]) -> np.ndarray:
    """Small stable update: dt*rhs with u = perp(grad psi)."""
    w = np.asarray(omega, dtype=float)
    # velocity from streamfunction: u = (d_y psi, -d_x psi)
    dpsi_dx = np.roll(psi, -1, axis=1) - np.roll(psi, 1, axis=1)
    dpsi_dy = np.roll(psi, -1, axis=0) - np.roll(psi, 1, axis=0)
    ux, uy = dpsi_dy * 0.5, -dpsi_dx * 0.5
    # gradients of omega
    dw_dx = np.roll(w, -1, axis=1) - np.roll(w, 1, axis=1)
    dw_dy = np.roll(w, -1, axis=0) - np.roll(w, 1, axis=0)
    adv = ux * (0.5 * dw_dx) + uy * (0.5 * dw_dy)
    lap = (np.roll(w, 1, 0) + np.roll(w, -1, 0) + np.roll(w, 1, 1) + np.roll(w, -1, 1) - 4.0 * w)
    rhs = -adv + nu * lap
    if forcing is not None:
        rhs = rhs + forcing
    return w + dt * rhs


def drift_poisson_step(omega: np.ndarray, max_iter: int = 20) -> np.ndarray:
    """Solve -Laplace(psi) = omega with Jacobi iterations. Returns psi."""
    psi = np.zeros_like(omega, dtype=float)
    for _ in range(max_iter):
        psi = 0.25 * (np.roll(psi, 1, 0) + np.roll(psi, -1, 0) + np.roll(psi, 1, 1) + np.roll(psi, -1, 1) + omega)
    return psi


def microwave_maxwell(E: np.ndarray, sigma: float, eps_r: float, mu_r: float, k0: float) -> np.ndarray:
    """Shape-preserving attenuation proportional to sigma: E_next = E / (1 + alpha), alpha ~ sigma/eps_r."""
    alpha = max(0.0, float(sigma)) / max(1e-9, float(eps_r))
    return E / (1.0 + alpha)


def lg_mode(n: int, m: int, rho: np.ndarray, w: float) -> np.ndarray:
    """Simplified radial LG envelope (normalized to <=1)."""
    k = abs(int(n) - int(m))
    rr = np.asarray(rho) / max(1e-9, float(w))
    R = (rr ** k) * np.exp(-(rr ** 2))
    mx = np.max(R) if R.size else 1.0
    return R / (mx if mx > 0 else 1.0)


def kinetics_update(N: np.ndarray, dt: float, rates: Optional[Dict[str, float]] = None) -> np.ndarray:
    """Non-stiff kinetics step with optional linear decay k and source S: N_next = N + dt*(S - k*N)."""
    N = np.asarray(N, dtype=float)
    k = float((rates or {}).get("k", 0.0))
    S = float((rates or {}).get("S", 0.0))
    out = N + dt * (S - k * N)
    out[out < 0] = 0.0
    return out


def adiabatic_mu(m: float, vc: float, B: float) -> float:
    """mu = m * vc^2 / (2 * B) with guardrails for B."""
    B = max(1e-12, float(B))
    return float(m) * float(vc) * float(vc) / (2.0 * B)
