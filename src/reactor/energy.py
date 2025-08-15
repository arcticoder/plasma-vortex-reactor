from __future__ import annotations


class EnergyLedger:
    """Accumulate energy input and compute energy per antiproton."""

    def __init__(self) -> None:
        self._energy_j = 0.0
        self._n_pbar = 0.0
        self._channels = {}

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

    def add_channel_energy(self, channel: str, power_w: float, dt_s: float) -> None:
        e = float(power_w) * float(dt_s)
        self._energy_j += e
        self._channels[channel] = self._channels.get(channel, 0.0) + e

    def channels(self):
        return dict(self._channels)

    def write_channel_report(self, path: str) -> None:
        import json
        payload = {
            "total_energy_J": self._energy_j,
            "channels": self._channels,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)


def fom(conversion: float, price: float, total_cost: float) -> float:
    """Figure of Merit = (Conversion * Price) / Total Cost."""
    if total_cost == 0:
        return float("inf")
    return float(conversion) * float(price) / float(total_cost)


class energy_interval:
    """Context manager to accumulate power over an interval.

    with energy_interval(ledger, power_w, dt_s):
        ...  # do work
    """

    def __init__(self, ledger: EnergyLedger, power_w: float, dt_s: float):
        self.ledger = ledger
        self.power_w = float(power_w)
        self.dt_s = float(dt_s)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.ledger.add_power_sample(self.power_w, self.dt_s)
        return False


def merge_ledgers(*ledgers: EnergyLedger) -> EnergyLedger:
    out = EnergyLedger()
    for L in ledgers:
        out._energy_j += L._energy_j
        out._n_pbar += L._n_pbar
        for k, v in L._channels.items():
            out._channels[k] = out._channels.get(k, 0.0) + v
    return out
