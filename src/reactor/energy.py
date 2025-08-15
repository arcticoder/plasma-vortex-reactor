from __future__ import annotations


class EnergyLedger:
    """Accumulate energy input and compute energy per antiproton."""
    def __init__(self) -> None:
        self._energy_j = 0.0
        self._n_pbar = 0.0

    def add_power_sample(self, power_w: float, dt_s: float) -> None:
        self._energy_j += float(power_w) * float(dt_s)

    def total_energy(self) -> float:
        return self._energy_j

    def set_yield(self, n_pbar: float) -> None:
        self._n_pbar = max(0.0, float(n_pbar))

    def energy_per_antiproton(self) -> float:
        if self._n_pbar <= 0.0:
            return float("inf")
        return self._energy_j / self._n_pbar


def fom(conversion: float, price: float, total_cost: float) -> float:
    """Figure of Merit = (Conversion * Price) / Total Cost."""
    if total_cost == 0:
        return float("inf")
    return float(conversion) * float(price) / float(total_cost)
