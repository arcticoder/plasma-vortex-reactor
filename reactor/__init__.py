"""
Bridge package to make `reactor` importable without installation.

This package sets its search path to the real sources under `src/reactor` so
that both `python -m reactor.cli` and imports from scripts work reliably in
development without requiring an editable install or PYTHONPATH tweaks.
"""

from __future__ import annotations

import os

# Determine the repository root and the actual package directory.
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_pkg_dir = os.path.join(_root, "src", "reactor")

# Instruct Python to look for submodules under the real package directory.
__path__ = [_pkg_dir]
