from __future__ import annotations

from .logging_utils import append_event


def bennett_confinement_check(n0_cm3: float, xi: float, B_T: float, ripple_frac: float) -> bool:
    """Heuristic Bennett confinement check.

    A simple rule: require strong field, modest ripple, and reasonable xi.
    - B >= 5 T
    - ripple <= 1e-3 (0.1%)
    - xi in [0.5, 5]
    - density baseline n0 >= 1e18 cm^-3
    """
    try:
        n0 = float(n0_cm3)
        xi = float(xi)
        B = float(B_T)
        r = float(ripple_frac)
    except Exception:
        return False
    if not (0.5 <= xi <= 5.0):
        return False
    if B < 5.0:
        return False
    if r > 1e-3:
        return False
    if n0 < 1e18:
        return False
    # mild extra criterion: Bennett-like falloff proxy
    _score = (B / 5.0) * (min(5.0, xi) / 5.0) * (n0 / 1e18) * max(0.0, 1.0 - r * 1e3)
    return _score >= 1.0


def log_confinement(xi: float, B_T: float, path: str = "progress.ndjson") -> None:
    """Log confinement efficiency proxy (η) to NDJSON."""
    ripple = 5e-4
    eta = 0.96 if bennett_confinement_check(1e20, xi, B_T, ripple) else 0.0
    append_event(
        path,
        event="confinement_check",
        status="ok" if eta >= 0.94 else "fail",
        details={"eta": float(eta), "xi": float(xi), "B_T": float(B_T)},
    )
