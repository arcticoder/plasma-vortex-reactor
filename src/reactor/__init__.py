"""
Plasma Vortex Reactor - core package
Lightweight, testable stubs modeling vorticity, equilibria, kinetics, EM and control glue.
"""
__version__ = "0.2.0"
__author__ = "arcticoder"

from .core import Reactor
from .models import (
    adiabatic_mu,
    bennett_profile,
    drift_poisson_step,
    kinetics_update,
    lg_mode,
    microwave_maxwell,
    vorticity_evolution,
)

__all__ = [
    "Reactor",
    "bennett_profile",
    "vorticity_evolution",
    "drift_poisson_step",
    "microwave_maxwell",
    "lg_mode",
    "kinetics_update",
    "adiabatic_mu",
]
