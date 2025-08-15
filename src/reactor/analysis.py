from __future__ import annotations

# Re-export split submodules for backward compatibility
from .analysis_stat import stability_variance, windowed_gamma  # noqa: F401
from .analysis_fields import (
    simulate_b_field_ripple,
    b_field_rms_fluctuation,
    estimate_density_from_em,
)  # noqa: F401
from .analysis_econ import write_economic_report  # noqa: F401
