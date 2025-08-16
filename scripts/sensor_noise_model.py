#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import numpy as np
import os, sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)
from reactor.plotting import _mpl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sensor_noise.png")
    ap.add_argument("--snr", type=float, default=20.0)
    ap.add_argument("--n", type=int, default=1000)
    args = ap.parse_args()
    rng = np.random.default_rng(123)
    t = np.linspace(0, 1, args.n)
    signal = np.sin(2 * np.pi * 5 * t)
    # SNR in dB -> noise power
    snr_lin = 10 ** (args.snr / 10)
    power_signal = np.mean(signal ** 2)
    power_noise = power_signal / snr_lin
    noise = rng.normal(0.0, np.sqrt(power_noise), size=signal.shape)
    measured = signal + noise
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(t, signal, label="signal")
    ax.plot(t, measured, label="measured", alpha=0.7)
    ax.legend(); fig.tight_layout()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=150)
    plt.close(fig)
    print(json.dumps({"snr_db": args.snr, "n": args.n, "out": args.out}))

if __name__ == "__main__":
    main()
