from __future__ import annotations

from typing import Optional

import numpy as np

_GLOBAL_RNG: Optional[np.random.Generator] = None


def set_seed(seed: int) -> None:
    global _GLOBAL_RNG
    _GLOBAL_RNG = np.random.default_rng(int(seed))


def get_rng() -> np.random.Generator:
    global _GLOBAL_RNG
    if _GLOBAL_RNG is None:
        _GLOBAL_RNG = np.random.default_rng(0)
    return _GLOBAL_RNG
