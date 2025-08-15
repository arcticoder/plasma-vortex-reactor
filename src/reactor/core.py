from __future__ import annotations
import numpy as np
from .models import vorticity_evolution, drift_poisson_step


class Reactor:
    """Minimal reactor state and stepper glue for integration testing."""
    def __init__(self, grid=(64, 64), nu: float = 1e-3):
        self.grid = grid
        self.nu = nu
        self.omega = np.zeros(grid, dtype=float)
        # seed a tiny vortex for smoke tests
        self.omega[grid[0] // 2, grid[1] // 2] = 1.0
        self.psi = drift_poisson_step(self.omega, max_iter=5)
        self.state = self.omega.copy()

    def step(self, dt: float = 1e-3):
        self.omega = vorticity_evolution(self.omega, self.psi, self.nu, dt, forcing=None)
        self.psi = drift_poisson_step(self.omega, max_iter=3)
        self.state = self.omega.copy()
        return self.state
