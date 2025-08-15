"""
Ensure the local "src/" folder is on sys.path when running Python commands
from this repository (including subprocess calls in tests).

Python automatically imports a module named "sitecustomize" on startup if it
is importable from sys.path. Since the project root is on sys.path by default
when running from this directory, placing this file here makes imports like
"import reactor" (located under src/reactor) work without requiring
PYTHONPATH tweaks or editable installs.
"""

from __future__ import annotations

import os
import sys


def _ensure_src_on_path() -> None:
    root = os.path.dirname(__file__)
    src = os.path.join(root, "src")
    if os.path.isdir(src) and src not in sys.path:
        # Prepend to prioritize local sources over globally installed packages.
        sys.path.insert(0, src)


_ensure_src_on_path()
