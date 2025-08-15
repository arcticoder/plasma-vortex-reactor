from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Thresholds:
    gamma_min: float = 140.0
    gamma_duration_s: float = 0.010
    density_min_cm3: float = 1e20
    confinement_min: float = 0.94
    b_field_min_T: float = 5.0
    b_ripple_max_pct: float = 0.01
    energy_per_pbar_max_J: float = 1e12
    total_energy_reduction_min: float = 242.0
    fom_min: float = 0.1
