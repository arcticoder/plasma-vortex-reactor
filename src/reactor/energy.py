from __future__ import annotations


class EnergyLedger:
    """Accumulate energy input and compute energy per antiproton."""

    def __init__(self) -> None:
        self._energy_j = 0.0
        self._n_pbar = 0.0
        self._channels = {}
        # Enhancement factor (>1 means achieved total is reduced relative to raw)
        self._enhancement = 1.0

    def add_power_sample(self, power_w: float, dt_s: float) -> None:
        self._energy_j += float(power_w) * float(dt_s)

    def total_energy(self) -> float:
        return self._energy_j / max(self._enhancement, 1e-12)

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
            "total_energy_J": self.total_energy(),
            "channels": self._channels,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def apply_enhancement(self, factor: float) -> None:
        """Apply an energy reduction enhancement factor (>1 reduces total)."""
        self._enhancement = max(1.0, float(factor))

    @staticmethod
    def total_energy_reduction(baseline_J: float, achieved_J: float) -> float:
        """Compute reduction ratio baseline/achieved (>=1)."""
        bj = max(1e-12, float(baseline_J))
        aj = max(1e-12, float(achieved_J))
        return bj / aj


def fom(conversion: float, price: float, total_cost: float) -> float:
    """Figure of Merit = (Conversion * Price) / Total Cost."""
    if total_cost == 0:
        return float("inf")
    return float(conversion) * float(price) / float(total_cost)


def lg_mode_enhancement(power_W: float, l_index: int, coupling_params: dict | None = None) -> float:
    """Toy LG OAM-derived enhancement factor.

    Increases with |l| and available power; returns factor>=1.
    factor = 1 + c0 * |l|^beta * (power_W ^ alpha)
    Defaults: c0=1e-4, alpha=0.25, beta=0.5
    """
    p = coupling_params or {}
    c0 = float(p.get("c0", 1e-4))
    alpha = float(p.get("alpha", 0.25))
    beta = float(p.get("beta", 0.5))
    val = 1.0 + c0 * (abs(int(l_index)) ** beta) * (max(0.0, float(power_W)) ** alpha)
    return max(1.0, float(val))


class apply_lg_enhancement:
    """Context manager to apply LG enhancement to an EnergyLedger temporarily."""

    def __init__(self, ledger: EnergyLedger, power_W: float, l_index: int, coupling_params: dict | None = None):
        self.ledger = ledger
        self.factor = lg_mode_enhancement(power_W, l_index, coupling_params)
        self._prev = None

    def __enter__(self):
        self._prev = self.ledger._enhancement
        self.ledger.apply_enhancement(self.factor)
        return self

    def __exit__(self, exc_type, exc, tb):
        # restore previous enhancement
        self.ledger._enhancement = self._prev if self._prev is not None else 1.0
        return False


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


def optimize_lg_enhancement(E_base: float, gamma: float = 150.0, l_index: int = 2) -> float:
    """Toy optimization target: E_reduced = E_base / (1 + gamma^2 * l_index)."""
    factor = 1.0 + (float(gamma) ** 2) * float(l_index)
    return float(E_base) / float(factor)


from typing import Sequence


def plot_energy_reduction(time_ms: Sequence[float], energies_J: Sequence[float], out_png: str) -> None:
    from .plotting import _mpl

    plt = _mpl()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(time_ms, energies_J, color="teal")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Energy (J)")
    ax.set_title("Energy Reduction Over Time")
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
