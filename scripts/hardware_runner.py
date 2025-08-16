#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path
import os, sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

try:
    from reactor.core import Reactor
except Exception:
    Reactor = None  # type: ignore


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=100)
    ap.add_argument("--dt", type=float, default=1e-3)
    ap.add_argument("--timeout", type=float, default=0.05)
    ap.add_argument("--simulate", action="store_true", help="Use a built-in simulated hardware function")
    ap.add_argument("--out", default="hardware_run.json")
    args = ap.parse_args()

    if Reactor is None:
        Path(args.out).write_text(json.dumps({"ok": False, "reason": "reactor not importable"}))
        return

    if args.simulate:
        import types, sys as _sys
        def _fake_sim(state):
            state = dict(state)
            state["hw"] = True
            state["i"] = state.get("i", 0) + 1
            return state
        # Create a proper module object for sys.modules
        mod = types.ModuleType('enhanced_simulation_hardware_abstraction_framework')
        setattr(mod, 'simulate_hardware', _fake_sim)
        _sys.modules['enhanced_simulation_hardware_abstraction_framework'] = mod

    R = Reactor(grid=(16, 16), nu=1e-3)
    R.hw_state = {"i": 0}
    stats = {"ok": True, "steps": 0, "timeouts": 0, "errors": 0}
    t0 = time.perf_counter()
    for _ in range(args.steps):
        try:
            R.step_with_real_hardware(dt=args.dt, timeout=args.timeout)
            stats["steps"] += 1
        except TimeoutError:
            stats["timeouts"] += 1
        except Exception:
            stats["errors"] += 1
    stats["elapsed_s"] = time.perf_counter() - t0
    Path(args.out).write_text(json.dumps(stats))
    print(json.dumps(stats))

if __name__ == "__main__":
    main()
