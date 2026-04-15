"""Repo-root conftest.

Adds the repo root to sys.path so test modules can import the
sibling Python packages (e.g. precision_sweep) without an editable
install. Mirrors the layout pytest discovers automatically when
tests live under a package, but works for our flat-script layout.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
