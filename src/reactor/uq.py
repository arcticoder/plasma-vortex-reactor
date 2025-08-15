from __future__ import annotations
import json
import random
from typing import Callable, Dict, Tuple, List, Any


def sample_uniform(a: float, b: float, rng: random.Random) -> float:
    return rng.uniform(float(a), float(b))


def run_uq_sampling(n_samples: int, seed: int, param_ranges: Dict[str, Tuple[float, float]],
                    eval_fn: Callable[[Dict[str, float]], Dict[str, float]]) -> Dict[str, Any]:
    """Run a simple Monte Carlo sweep and return aggregated stats."""
    rng = random.Random(int(seed))
    results: List[Dict[str, float]] = []
    for _ in range(int(n_samples)):
        params = {k: sample_uniform(v[0], v[1], rng) for k, v in param_ranges.items()}
        out = eval_fn(params)
        results.append(out)
    keys = results[0].keys() if results else []
    means = {k: sum(r[k] for r in results) / len(results) for k in keys} if results else {}
    return {"n_samples": n_samples, "means": means, "results": results}


def save_results(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
