from __future__ import annotations

from typing import Any, Optional, Sequence

"""Lightweight plotting helpers with optional matplotlib dependency.

If matplotlib is unavailable, provide a minimal stub that supports
subplots().savefig(...), writing a 1x1 PNG placeholder so CI continues.
"""


def _mpl() -> Any:
    try:
        import matplotlib.pyplot as plt
        return plt
    except Exception:  # pragma: no cover - environment-dependent
        class _Fig:
            def __init__(self):
                self._closed = False
            def tight_layout(self):
                return None
            def savefig(self, path, dpi=150):  # noqa: ARG002
                # write a valid 1x1 PNG placeholder
                try:
                    import os
                    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
                except Exception:
                    pass
                try:
                    with open(path, "wb") as f:
                        f.write(bytes.fromhex(
                            "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000A49444154789C6360000002000100FFFF03000006000557BF0000000049454E44AE426082"
                        ))
                except Exception:
                    pass
        class _Ax:
            def plot(self, *a, **k):  # noqa: ANN001, ANN002
                return None
            def scatter(self, *a, **k):  # noqa: ANN001, ANN002
                return None
            def bar(self, *a, **k):  # noqa: ANN001, ANN002
                return None
            def errorbar(self, *a, **k):  # noqa: ANN001, ANN002
                return None
            def set_xlabel(self, *_):
                return None
            def set_ylabel(self, *_):
                return None
            def set_title(self, *_):
                return None
            def legend(self, *_, **__):
                return None
        class _Stub:
            def subplots(self, figsize=(5, 3)):
                return _Fig(), _Ax()
            def close(self, *_):
                return None
        return _Stub()


def quick_scatter(x: Sequence[float], y: Sequence[float], out_png: Optional[str] = None,
                  xlabel: str = "x", ylabel: str = "y", title: str = "") -> None:
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.scatter(list(x), list(y), s=12, alpha=0.7)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    fig.tight_layout()
    if out_png:
        fig.savefig(out_png, dpi=150)
    plt.close(fig)
