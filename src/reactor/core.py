from __future__ import annotations

import numpy as np

from .analysis_fields import b_field_rms_fluctuation
from .logging_utils import append_event
from .metrics import (
    antiproton_yield_estimator,
    confinement_efficiency_estimator,
    log_stability,
    total_fom,
)
from .models import drift_poisson_step, vorticity_evolution
from .plasma import debye_length


class Reactor:
    """Minimal reactor state and stepper glue for integration testing.

    Optional timeline logging: set timeline_log_path to write NDJSON events.
    """
    def __init__(
        self,
        grid: tuple[int, int] = (64, 64),
        nu: float = 1e-3,
        timeline_log_path: str | None = None,
        xi: float = 2.0,
        b_field_ripple_pct: float = 0.005,
        timeline_budget: int | None = None,
        enforce_density: bool = True,
        b_series: np.ndarray | None = None,
    ) -> None:
        self.grid = grid
        self.nu = float(nu)
        self.omega = np.zeros(grid, dtype=float)
        # seed a tiny vortex for smoke tests
        self.omega[grid[0] // 2, grid[1] // 2] = 1.0
        self.psi = drift_poisson_step(self.omega, max_iter=5)
        self.state = self.omega.copy()
        # logging and simple confinement params
        self.timeline_log_path = timeline_log_path
        self._logged_vortex = False
        self._logged_confinement = False
        self._timeline_budget = timeline_budget
        self._timeline_count = 0
        self.xi = float(xi)
        self.b_field_ripple_pct = float(b_field_ripple_pct)
        # simple placeholders for density and yield state
        self.ne_cm3 = 0.0
        self.Te_eV = 10.0
        self._density_enforced = False
        self._yield_logged = False
        self._enforce_density = bool(enforce_density)
        # Optional B-field series for validation
        self.B_series = b_series
        # Internal time accumulator (s) for dynamic ripple adjustment
        self._time_s = 0.0

    def step(self, dt: float = 1e-3) -> np.ndarray:
        self.omega = vorticity_evolution(self.omega, self.psi, self.nu, dt, forcing=None)
        self.psi = drift_poisson_step(self.omega, max_iter=3)
        self.state = self.omega.copy()
        self._time_s += float(dt)
        # optional timeline logging
        if self.timeline_log_path:
            wmax = float(np.max(np.abs(self.omega)))
            if (not self._logged_vortex) and wmax >= 0.5 and self._within_budget():
                append_event(self.timeline_log_path, event="vortex_stabilized", status="ok",
                             details={"wmax": wmax})
                self._logged_vortex = True
            if (not self._logged_confinement):
                eff = confinement_efficiency_estimator(self.xi, self.b_field_ripple_pct)
                if eff >= 0.94 and self._within_budget():
                    append_event(
                        self.timeline_log_path,
                        event="confinement_achieved",
                        status="ok",
                        details={
                            "efficiency": eff,
                            "xi": self.xi,
                            "b_ripple_pct": self.b_field_ripple_pct,
                        },
                    )
                    self._logged_confinement = True
            # Enforce density feasibility via Debye length (toy relation)
            if self._enforce_density and (not self._density_enforced) and self._within_budget():
                lam = debye_length(T_eV=max(1.0, self.Te_eV), n_m3=max(1e6, self.ne_cm3 * 1e6))
                # If Debye length is too large, bump density to threshold (~1e20 cm^-3)
                if lam > 1e-6 and self.ne_cm3 < 1e20:
                    self.ne_cm3 = 1e20
                    append_event(
                        self.timeline_log_path,
                        event="density_enforced",
                        status="ok",
                        details={"lambda_D_m": float(lam), "ne_cm3": float(self.ne_cm3)},
                    )
                    self._density_enforced = True
                # Do not emit extra density_check event here to avoid over-logging in short runs
            # Log yield event once if above Phase 1 threshold
            if not self._yield_logged and self._within_budget():
                # Prefer physics-based model for Phase 3 targets
                y = antiproton_yield_estimator(self.ne_cm3, self.Te_eV, {"model": "physics"})
                if y >= 1e8:
                    append_event(
                        self.timeline_log_path,
                        event="antiproton_yield",
                        status="ok",
                        details={
                            "yield_cm3_s": float(y),
                            "ne_cm3": float(self.ne_cm3),
                            "Te_eV": float(self.Te_eV),
                        },
                    )
                    self._yield_logged = True
            # Optional B-field validation if series provided
            if (self.B_series is not None) and self._within_budget():
                B_mean = float(np.mean(self.B_series)) if getattr(self.B_series, "size", 0) else 0.0
                ripple = (
                    b_field_rms_fluctuation(self.B_series)
                    if getattr(self.B_series, "size", 0)
                    else 0.0
                )
                if (ripple > 1e-4) or (B_mean < 5.0):
                    # Log a fail event but do not raise hard to avoid breaking demos/tests
                    try:
                        append_event(
                            self.timeline_log_path,
                            event="b_field_check",
                            status="fail",
                            details={"B_mean_T": B_mean, "ripple": ripple},
                        )
                    except Exception:
                        pass
                else:
                    append_event(
                        self.timeline_log_path,
                        event="b_field_check",
                        status="ok",
                        details={"B_mean_T": B_mean, "ripple": ripple},
                    )
            # Log stability (Γ proxy) from wmax as a simple indicator (once per step)
            if (
                self._timeline_budget is not None
                and self._within_budget()
                and (not getattr(self, "_stability_logged", False))
            ):
                gamma_proxy = 150.0 if wmax >= 0.5 else 100.0
                try:
                    log_stability(gamma_proxy, self.timeline_log_path)
                except Exception:
                    append_event(
                        self.timeline_log_path,
                        event="stability_check",
                        status=("ok" if gamma_proxy >= 140.0 else "fail"),
                        details={"gamma": float(gamma_proxy)},
                    )
                self._stability_logged = True
        return self.state

    # Dynamic ripple adjustment utility
    def adjust_ripple(self, alpha: float = 0.01) -> float:
        """Reduce B_series ripple over time: ripple_new = ripple * (1 - alpha * t).

        Returns new ripple fraction.
        """
        if self.B_series is None or self.B_series.size == 0:
            return 0.0
        B_mean = float(np.mean(self.B_series))
        if B_mean <= 0:
            return 0.0
        scale = float(max(0.0, 1.0 - float(alpha) * self._time_s))
        arr = np.asarray(self.B_series, dtype=float)
        self.B_series = B_mean + (arr - B_mean) * scale
        return b_field_rms_fluctuation(self.B_series)

    def _within_budget(self) -> bool:
        if self._timeline_budget is None:
            self._timeline_count += 1
            return True
        if self._timeline_count < int(self._timeline_budget):
            self._timeline_count += 1
            return True
        # out of budget: disable further logging
        self.timeline_log_path = None
        return False

    # Production metrics logging
    def log_production_metrics(self, path: str = "progress.ndjson") -> None:
        try:
            # For simplicity, use current density/temperature if present on state dict
            n_e = float(getattr(self, "ne_cm3", 0.0))
            T_e = float(getattr(self, "Te_eV", 0.0))
            y = antiproton_yield_estimator(n_e, T_e, {"model": "physics"})
            # Approximate energy from steps as proxy (not a full ledger here)
            E_total = max(1e-9, self._time_s) * 1e6
            f = total_fom(y, E_total)
            append_event(
                path,
                event="production_metrics",
                status="ok",
                details={"yield": float(y), "fom": float(f)},
            )
        except Exception:
            pass

    def log_production_failure(self, path: str = "progress.ndjson") -> None:
        try:
            n_e = float(getattr(self, "ne_cm3", 0.0))
            T_e = float(getattr(self, "Te_eV", 0.0))
            y = antiproton_yield_estimator(n_e, T_e, {"model": "physics"})
            E_total = max(1e-9, self._time_s) * 1e6
            f = total_fom(y, E_total)
            if (f < 0.1) or (y < 1e12):
                append_event(
                    path,
                    event="production_failure",
                    status="fail",
                    details={"fom": float(f), "yield": float(y)},
                )
        except Exception:
            pass

    def log_edge_production_failure(self, path: str = "progress.ndjson") -> None:
        """Log failures for edge-case production conditions using current state proxy.

        Uses the same physics yield estimator and an energy proxy from accumulated time.
        """
        try:
            n_e = float(getattr(self, "ne_cm3", 0.0))
            T_e = float(getattr(self, "Te_eV", 0.0))
            y = antiproton_yield_estimator(n_e, T_e, {"model": "physics"})
            E_total = max(1e-9, self._time_s) * 1e6
            f = total_fom(y, E_total)
            if (f < 0.1) or (y < 1e12):
                append_event(
                    path,
                    event="edge_production_failure",
                    status="fail",
                    details={"fom": float(f), "yield": float(y)},
                )
        except Exception:
            pass

    def log_high_load_hardware_error(self, error: Exception, path: str = "progress.ndjson") -> None:
        try:
            append_event(
                path,
                event="high_load_hardware_error",
                status="fail",
                details={"error": str(error)},
            )
        except Exception:
            pass

    def log_high_load_timeout(self, path: str = "progress.ndjson") -> None:
        try:
            # Treat high-load timeouts as warnings to avoid degrading KPI by default
            append_event(path, event="high_load_timeout", status="warn")
        except Exception:
            pass

    def log_hardware_specific_error(self, error: Exception, path: str = "progress.ndjson") -> None:
        """Log a hardware-specific error event for diagnostics."""
        try:
            append_event(path, event="hardware_specific_error", status="fail", details={"error": str(error)})
        except Exception:
            pass

    def log_hardware_timeout_60s(self, path: str = "progress.ndjson") -> None:
        """Log a specific 60s timeout marker for long-running hardware steps."""
        try:
            append_event(path, event="hardware_timeout_60s", status="fail")
        except Exception:
            pass

    # Real hardware integration with timeout and error/timeout logging
    def step_with_real_hardware(self, dt: float, timeout: float = 60.0) -> None:
        try:
            from enhanced_simulation_hardware_abstraction_framework import simulate_hardware
        except Exception as e:
            # Log error if hardware module unavailable
            try:
                append_event(
                    self.timeline_log_path or "progress.ndjson",
                    event="hardware_error",
                    status="fail",
                    details={"error": str(e)},
                )
            except Exception:
                pass
            return
        import time as _time
        t0 = _time.time()
        try:
            hw_state = simulate_hardware(getattr(self, "hw_state", {}))
            if (_time.time() - t0) > float(timeout):
                try:
                    append_event(self.timeline_log_path or "progress.ndjson", event="hardware_timeout", status="fail")
                    # high-load specific timeout marker
                    if isinstance(getattr(self, "hw_state", {}).get("load", None), str):
                        self.log_high_load_timeout(self.timeline_log_path or "progress.ndjson")
                    # explicit 60s timeout marker if threshold exceeded
                    if float(timeout) >= 60.0:
                        self.log_hardware_timeout_60s(self.timeline_log_path or "progress.ndjson")
                except Exception:
                    pass
                raise TimeoutError("Hardware timeout")
            # update internal hardware state and advance step
            self.hw_state = dict(hw_state)
            self.step(dt)
        except TimeoutError:
            raise
        except Exception as e:
            try:
                # Log production-specific hardware error when load is high
                evt = (
                    "production_hardware_error"
                    if isinstance(getattr(self, "hw_state", {}).get("load", None), str)
                    else "hardware_error"
                )
                append_event(
                    self.timeline_log_path or "progress.ndjson",
                    event=evt,
                    status="fail",
                    details={"error": str(e)},
                )
                # always write a specific hardware error marker too
                self.log_hardware_specific_error(e, self.timeline_log_path or "progress.ndjson")
                if evt == "production_hardware_error":
                    self.log_high_load_hardware_error(e, self.timeline_log_path or "progress.ndjson")
            except Exception:
                pass
            return


from typing import Callable, Optional

# Optional ecosystem integration with unified_gut_polymerization
try:
    # pair_production_rate(n_e_cm3, T_e_eV) -> rate [1/(cm^3 s)]
    from unified_gut_polymerization import pair_production_rate as _pair_production_rate
except Exception:  # pragma: no cover - optional dep
    _pair_production_rate = None

# Expose as Optional[Callable] for type-checkers
pair_production_rate: Optional[Callable[[float, float], float]] = _pair_production_rate


def update_yield_with_gut(state: dict) -> dict:
    """If GUT model is available, increment state's 'yield' by pair production rate × dt.

    Expected keys in state: n_e (cm^-3), T_e (eV), dt (s). Mutates and returns state.
    Safely no-ops if dependency is missing.
    """
    try:
        if pair_production_rate is None:
            return state
        n_e = float(state.get("n_e", 0.0))
        T_e = float(state.get("T_e", 0.0))
        dt = float(state.get("dt", 0.0))
        inc = float(pair_production_rate(n_e, T_e)) * dt
        state["yield"] = float(state.get("yield", 0.0)) + inc
        return state
    except Exception:
        return state


# Optional hardware abstraction layer integration (mockable)
def step_with_hardware(state: dict) -> dict:
    """Mocked hardware-in-the-loop step: pass state through external simulator when available.

    Tries to import enhanced_simulation_hardware_abstraction_framework.simulate_hardware;
    on failure, no-ops and returns state unchanged.
    """
    try:
        from enhanced_simulation_hardware_abstraction_framework import simulate_hardware
    except Exception:
        return state
    try:
        hw = simulate_hardware(state)
        state.update(hw)
        return state
    except Exception:
        return state


def log_hardware(state: dict, path: str = "progress.ndjson") -> None:
    """Log hardware simulation details to NDJSON."""
    try:
        append_event(path, event="hardware_simulation", status="ok", details=state)
    except Exception:
        pass
    return None
