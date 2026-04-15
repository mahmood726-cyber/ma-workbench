"""Contract test for sglt2i-hfpef-demo/expected.json.

Ensures the benchmark block is fully populated, pool_type is a known
value, and applied_delta matches the prespecified rule from protocol.md.
"""
import json
from pathlib import Path

EXPECTED_PATH = Path("sglt2i-hfpef-demo/expected.json")

REQUIRED_BENCHMARK_KEYS = {
    "source", "doi", "pool_type", "hr", "ci_low", "ci_high", "accessed",
}
REQUIRED_TOLERANCE_KEYS = {
    "delta_hr_ipd_branch", "delta_hr_aggregate_branch", "applied_delta",
    "applied_delta_source", "method", "decision_rule",
}
VALID_POOL_TYPES = {"ipd", "aggregate"}


def load():
    assert EXPECTED_PATH.exists(), f"{EXPECTED_PATH} missing"
    return json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))


def test_schema_version():
    assert load()["schema_version"] == "1.0"


def test_benchmark_keys():
    b = load()["benchmark"]
    assert REQUIRED_BENCHMARK_KEYS <= b.keys()


def test_benchmark_non_empty():
    b = load()["benchmark"]
    for k in ("source", "doi", "accessed"):
        assert b[k] not in (None, ""), f"benchmark.{k} empty"
    for k in ("hr", "ci_low", "ci_high"):
        assert b[k] > 0, f"benchmark.{k} not positive"


def test_pool_type_valid():
    pool_type = load()["benchmark"]["pool_type"]
    assert pool_type in VALID_POOL_TYPES, (
        f"pool_type={pool_type!r} not in {VALID_POOL_TYPES}"
    )


def test_tolerance_keys():
    t = load()["tolerance"]
    assert REQUIRED_TOLERANCE_KEYS <= t.keys()


def test_applied_delta_matches_pool_type():
    d = load()
    pool_type = d["benchmark"]["pool_type"]
    t = d["tolerance"]
    if pool_type == "ipd":
        assert t["applied_delta"] == t["delta_hr_ipd_branch"] == 0.02
    else:
        assert t["applied_delta"] == t["delta_hr_aggregate_branch"] == 0.005


def test_benchmark_ci_ordering():
    b = load()["benchmark"]
    assert b["ci_low"] < b["hr"] < b["ci_high"]
