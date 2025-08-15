from __future__ import annotations

import json
from typing import Any, Dict


def write_economic_report(
    path: str,
    energy_J: float,
    n_pbar: float,
    price_per_unit: float,
    overhead_cost: float,
) -> Dict[str, Any]:
    revenue = n_pbar * price_per_unit
    cost = overhead_cost + energy_J
    fom = (revenue / cost) if cost > 0 else float('inf')
    payload = {
        "energy_J": energy_J,
        "n_pbar": n_pbar,
        "price_per_unit": price_per_unit,
        "overhead_cost": overhead_cost,
        "revenue": revenue,
        "total_cost": cost,
        "FOM": fom,
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
    return payload
