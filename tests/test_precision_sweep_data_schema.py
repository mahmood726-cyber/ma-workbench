"""Contract test for precision-sweep-demo/data.json."""
import json
from pathlib import Path

DATA = Path("precision-sweep-demo/data.json")

REQUIRED_KEYS = {
    "schema_version", "seed", "generator", "n_replications",
    "true_hr_range", "se_range", "dp_levels", "pool_method",
}


def load():
    assert DATA.exists(), f"{DATA} missing"
    return json.loads(DATA.read_text(encoding="utf-8"))


def test_schema_version():
    assert load()["schema_version"] == "1.0"


def test_all_required_keys():
    missing = REQUIRED_KEYS - load().keys()
    assert not missing, f"missing: {missing}"


def test_generator_is_xoshiro():
    assert load()["generator"] == "xoshiro128**"


def test_seed_is_fixed_integer():
    seed = load()["seed"]
    assert isinstance(seed, int) and seed == 20260415


def test_n_replications_ten_thousand():
    assert load()["n_replications"] == 10000


def test_dp_levels_cover_1_to_4():
    assert load()["dp_levels"] == [1, 2, 3, 4]


def test_true_hr_range_valid():
    lo, hi = load()["true_hr_range"]
    assert 0 < lo < hi


def test_se_range_valid():
    lo, hi = load()["se_range"]
    assert 0 < lo < hi
