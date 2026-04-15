"""Contract test for sglt2i-hfpef-demo/data.json.

Ensures the trial inputs match a fixed schema and that derived fields
(log_hr, se_log_hr) are internally consistent with reported HR and CI.
"""
import json
import math
from pathlib import Path

DATA_PATH = Path("sglt2i-hfpef-demo/data.json")

REQUIRED_TRIAL_KEYS = {
    "id", "hr", "ci_low", "ci_high", "n_total", "n_events_total",
    "log_hr", "se_log_hr", "source",
}
REQUIRED_SOURCE_KEYS = {"citation", "doi", "table", "page", "accessed"}
EXPECTED_TRIAL_IDS = {"EMPEROR-Preserved", "DELIVER"}


def load():
    assert DATA_PATH.exists(), f"{DATA_PATH} missing"
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def test_schema_version():
    data = load()
    assert data["schema_version"] == "1.0"


def test_two_trials():
    data = load()
    ids = {t["id"] for t in data["trials"]}
    assert ids == EXPECTED_TRIAL_IDS


def test_trial_keys_complete():
    data = load()
    for t in data["trials"]:
        missing = REQUIRED_TRIAL_KEYS - t.keys()
        assert not missing, f"{t['id']} missing keys: {missing}"
        missing_src = REQUIRED_SOURCE_KEYS - t["source"].keys()
        assert not missing_src, f"{t['id']} source missing: {missing_src}"


def test_source_fields_non_empty():
    data = load()
    for t in data["trials"]:
        for key in REQUIRED_SOURCE_KEYS:
            v = t["source"][key]
            assert v is not None and v != "", (
                f"{t['id']}.source.{key} is empty: {v!r}"
            )


def test_log_hr_derivation():
    data = load()
    for t in data["trials"]:
        expected = math.log(t["hr"])
        assert abs(t["log_hr"] - expected) < 1e-4, (
            f"{t['id']}.log_hr = {t['log_hr']}, expected {expected:.6f}"
        )


def test_se_log_hr_derivation():
    data = load()
    for t in data["trials"]:
        expected = (math.log(t["ci_high"]) - math.log(t["ci_low"])) / (2 * 1.96)
        assert abs(t["se_log_hr"] - expected) < 1e-4, (
            f"{t['id']}.se_log_hr = {t['se_log_hr']}, expected {expected:.6f}"
        )


def test_ci_ordering():
    data = load()
    for t in data["trials"]:
        assert t["ci_low"] < t["hr"] < t["ci_high"], (
            f"{t['id']} CI ordering broken: {t['ci_low']}/{t['hr']}/{t['ci_high']}"
        )
