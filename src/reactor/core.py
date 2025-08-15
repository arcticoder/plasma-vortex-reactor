from __future__ import annotations

import numpy as np

from .logging_utils import append_event
from .metrics import confinement_efficiency_estimator
from .models import drift_poisson_step, vorticity_evolution


class Reactor:
    """Minimal reactor state and stepper glue for integration testing.

    Optional timeline logging: set timeline_log_path to write NDJSON events.
    """
    def __init__(self, grid=(64, 64), nu: float = 1e-3,
                 timeline_log_path: str | None = None,
                 xi: float = 2.0,
                 b_field_ripple_pct: float = 0.005,
                 timeline_budget: int | None = None):
        self.grid = grid
        self.nu = nu
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

    def step(self, dt: float = 1e-3):
        self.omega = vorticity_evolution(self.omega, self.psi, self.nu, dt, forcing=None)
        self.psi = drift_poisson_step(self.omega, max_iter=3)
        self.state = self.omega.copy()
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
        return self.state

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
