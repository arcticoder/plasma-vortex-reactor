from __future__ import annotations

import json
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


def thresholds_from_json(path: str) -> Thresholds:
    """Construct Thresholds from a metrics.json file.

    The JSON should map threshold names to values; unknown keys are ignored.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # filter only known fields
    fields = {f.name for f in Thresholds.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    kwargs = {k: v for k, v in data.items() if k in fields}
    return Thresholds(**kwargs)  # type: ignore[arg-type]
