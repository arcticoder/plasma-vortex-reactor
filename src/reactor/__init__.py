"""
Plasma Vortex Reactor - core package
Lightweight, testable stubs modeling vorticity, equilibria, kinetics, EM and control glue.
"""
__version__ = "0.1.0"
__author__ = "arcticoder"

from .models import (
    bennett_profile,
    vorticity_evolution,
    drift_poisson_step,
    microwave_maxwell,
    lg_mode,
    kinetics_update,
    adiabatic_mu,
)
from .core import Reactor

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
