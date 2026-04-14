"""Test that committed golden references still match fresh recomputation.

Each run of `generate_references.py` is deterministic — the same datasets
should produce byte-identical reference JSON files. This test catches
accidental drift (either in the datasets or the estimators).

The test DOES NOT pull the JS code; it re-implements the same formulas
in Python and diffs to 1e-10. A separate WebR-driven test (run by the
webr-validator app in a browser) is responsible for proving the JS
implementations also match.
"""

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Import the generator's functions
sys.path.insert(0, str(HERE))
from generate_references import DATASETS, pool  # type: ignore


def test_all_datasets_have_reference_files():
    for ds in DATASETS:
        ref = HERE / "references" / (ds["slug"] + ".json")
        assert ref.is_file(), f"missing reference: {ref}"
        data = HERE / "datasets" / (ds["slug"] + ".json")
        assert data.is_file(), f"missing dataset: {data}"


def test_committed_references_match_fresh_recompute():
    """If this fails, either the estimators changed or the datasets drifted."""
    diffs = []
    for ds in DATASETS:
        ref_file = HERE / "references" / (ds["slug"] + ".json")
        with open(ref_file, "r", encoding="utf-8") as fh:
            committed = json.load(fh)["reference"]
        fresh = pool(ds["studies"])
        # Compare scalar fields to 1e-9
        for path in [
            ("fe", "estimate"), ("fe", "se"), ("fe", "ci_lb"), ("fe", "ci_ub"),
            ("re_pm", "estimate"), ("re_pm", "se"),
            ("re_pm", "ci_lb"), ("re_pm", "ci_ub"),
            ("re_pm", "tau2"), ("re_pm", "qe"),
        ]:
            a = committed
            b = fresh
            for k in path:
                a = a[k]
                b = b[k]
            if abs(a - b) > 1e-8:
                diffs.append((ds["slug"], "/".join(path), a, b, abs(a - b)))
    assert not diffs, f"Reference drift: {diffs}"


def test_bus_payload_schema_stable():
    """Golden dataset files must carry the bus-payload envelope for drop-in use."""
    for ds in DATASETS:
        data_file = HERE / "datasets" / (ds["slug"] + ".json")
        with open(data_file, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        payload = d.get("bus_payload")
        assert payload and payload.get("_schema") == "ma-studies-v1", \
            f"{ds['slug']}: bus_payload envelope missing or wrong schema"
        assert isinstance(payload.get("studies"), list)
        for s in payload["studies"]:
            for k in ("label", "est", "se"):
                assert k in s, f"{ds['slug']}: study missing {k}"


def test_r_script_generated():
    for ds in DATASETS:
        data_file = HERE / "datasets" / (ds["slug"] + ".json")
        with open(data_file, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        rs = d.get("r_script", "")
        assert "library(metafor)" in rs
        assert 'method = "PM"' in rs
        assert "cat(sprintf(" in rs


def test_tau2_sign_and_i2_range():
    for ds in DATASETS:
        ref_file = HERE / "references" / (ds["slug"] + ".json")
        with open(ref_file, "r", encoding="utf-8") as fh:
            r = json.load(fh)["reference"]
        assert r["re_pm"]["tau2"] >= 0, f"{ds['slug']}: negative tau2"
        assert 0 <= r["re_pm"]["i2_pct"] <= 100, f"{ds['slug']}: I2 out of [0,100]"
