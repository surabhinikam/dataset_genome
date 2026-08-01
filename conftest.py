"""
conftest.py — Repository-root pytest configuration.

This file serves two purposes:
1. It marks the repository root as pytest's rootdir (by being the highest
   conftest.py that pytest finds during upward traversal).
2. It injects backend/ into sys.path as a belt-and-suspenders complement to
   the `pythonpath = backend` directive in pytest.ini, ensuring compatibility
   with pytest < 7.0 and any tooling that invokes pytest without reading
   pytest.ini (e.g., some IDE test runners).

Root cause of the regression:
    backend/__init__.py made pytest treat backend/ as a *package* rather than
    a source root. Without an explicit pythonpath or sys.path injection,
    pytest resolved `from main import app` against the repo root, not backend/,
    producing ModuleNotFoundError for 'main', 'app', and 'services'.
"""

import sys
from pathlib import Path

# Prepend backend/ to sys.path so all test imports resolve correctly:
#   from main import app
#   from app.<module> import ...
#   from services.<module> import ...
_backend = Path(__file__).parent / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))
