from __future__ import annotations
import numpy as np


def debye_length(T_eV: float, n_m3: float) -> float:
    """Compute Debye length λD = sqrt(eps0 kB T / (2 n e^2)). Inputs in eV and m^-3.
    Constants: eps0=8.854e-12 F/m, kB=1.380649e-23 J/K, 1 eV = 1.602e-19 J, e=1.602e-19 C
    """
    eps0 = 8.854e-12
    e = 1.602e-19
    eV_J = 1.602e-19
    kB = 1.380649e-23
    # Approximate T[K] ~ T[eV] * eV_J / kB
    T_K = float(T_eV) * eV_J / kB
    n = max(1e-30, float(n_m3))
    lam2 = eps0 * kB * T_K / (2.0 * n * e * e)
    return float(np.sqrt(max(lam2, 0.0)))
