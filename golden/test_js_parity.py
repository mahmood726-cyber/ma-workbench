"""Execute the ACTUAL shipped browser JS against the golden references.

The sibling ``test_golden_parity.py`` only proves a *Python* re-implementation
matches the committed references; it never runs the JavaScript that ships in
the apps. This test closes that gap: it invokes ``golden/js_parity.mjs``,
which extracts the real pooling engine from ``workbench/index.html`` and diffs
FE / RE / tau2 / Q for the 6 study-based golden datasets against
``golden/references/*.json`` at 1e-8. A numerical regression in the shipped
pooling JS now fails CI.

Skips (never fails) when Node is unavailable so environments without a Node
runtime keep a green suite; CI installs Node 20, so the check runs there.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "js_parity.mjs"


def test_shipped_js_matches_golden_references():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not on PATH; JS parity runs in CI where Node is installed")
    assert HARNESS.is_file(), f"missing harness: {HARNESS}"
    proc = subprocess.run(
        [node, str(HARNESS)],
        cwd=str(HERE.parent),
        capture_output=True,
        text=True,
        timeout=60,
    )
    combined = (proc.stdout or "") + (proc.stderr or "")
    assert proc.returncode == 0, f"shipped JS diverged from golden references:\n{combined}"
    assert "js_parity OK" in combined, combined
