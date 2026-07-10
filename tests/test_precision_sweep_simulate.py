"""Correctness + determinism tests for the precision-sweep MC."""
import math

import pytest

from precision_sweep.simulate import (
    _iv_pool_log,
    _round_trial_at_dp,
    run_simulation,
)
from precision_sweep.xoshiro import Xoshiro128SS


def test_xoshiro_deterministic():
    """Same seed → same sequence."""
    r1 = Xoshiro128SS(42)
    r2 = Xoshiro128SS(42)
    for _ in range(1000):
        assert r1.next_uint32() == r2.next_uint32()


def test_xoshiro_range():
    """random() in [0, 1)."""
    rng = Xoshiro128SS(20260415)
    for _ in range(1000):
        x = rng.random()
        assert 0.0 <= x < 1.0


def test_iv_pool_fe_two_equal_studies():
    """Two equal studies, equal SE → pool = the point estimate."""
    mu, se = _iv_pool_log([-0.223, -0.223], [0.05, 0.05])
    assert abs(mu - (-0.223)) < 1e-12
    # Pooled SE = 1 / sqrt(2 * 1/0.05^2) = 0.05 / sqrt(2)
    assert abs(se - 0.05 / math.sqrt(2)) < 1e-12


def test_round_trial_at_dp_2():
    """Round HR 0.79 + CI (0.69, 0.90) at dp=2 → same values."""
    log_hr = math.log(0.79)
    se = (math.log(0.90) - math.log(0.69)) / (2 * 1.96)
    log_hr_r, se_r = _round_trial_at_dp(0.79, log_hr, se, 2)
    assert abs(log_hr_r - log_hr) < 1e-10
    assert abs(se_r - se) < 1e-10


def test_round_trial_at_dp_1_looses_precision():
    """At dp=1, HR 0.79 becomes 0.8 and SE changes."""
    log_hr = math.log(0.79)
    se = (math.log(0.90) - math.log(0.69)) / (2 * 1.96)
    log_hr_r, _ = _round_trial_at_dp(0.79, log_hr, se, 1)
    assert abs(log_hr_r - math.log(0.8)) < 1e-10


def test_simulation_rejects_zero_replications():
    """n_replications=0 must fail closed with ValueError, not IndexError."""
    with pytest.raises(ValueError):
        run_simulation(
            seed=1,
            n_replications=0,
            true_hr_range=(0.5, 1.5),
            se_range=(0.05, 0.2),
            dp_levels=[2],
        )


def test_simulation_rejects_empty_dp_levels():
    """dp_levels=[] must fail closed with ValueError."""
    with pytest.raises(ValueError):
        run_simulation(
            seed=1,
            n_replications=10,
            true_hr_range=(0.5, 1.5),
            se_range=(0.05, 0.2),
            dp_levels=[],
        )


def test_simulation_deterministic():
    """Same inputs → byte-identical outputs."""
    args = dict(
        seed=20260415,
        n_replications=100,
        true_hr_range=(0.6, 1.3),
        se_range=(0.04, 0.08),
        dp_levels=[1, 2, 3, 4],
    )
    r1 = run_simulation(**args)
    r2 = run_simulation(**args)
    assert r1 == r2


def test_simulation_monotonic_in_dp():
    """Higher dp → tighter median |Δ|."""
    result = run_simulation(
        seed=20260415,
        n_replications=500,
        true_hr_range=(0.6, 1.3),
        se_range=(0.04, 0.08),
        dp_levels=[1, 2, 3, 4],
    )
    m1 = result["per_dp"]["1"]["median"]
    m2 = result["per_dp"]["2"]["median"]
    m3 = result["per_dp"]["3"]["median"]
    m4 = result["per_dp"]["4"]["median"]
    assert m1 >= m2 >= m3 >= m4, (
        f"non-monotonic: {m1} {m2} {m3} {m4}"
    )


def test_simulation_scale_with_dp():
    """Median |Δ| at dp=k roughly on the order of 10^-k (within 3x)."""
    result = run_simulation(
        seed=20260415,
        n_replications=1000,
        true_hr_range=(0.6, 1.3),
        se_range=(0.04, 0.08),
        dp_levels=[1, 2, 3, 4],
    )
    for dp in [1, 2, 3, 4]:
        m = result["per_dp"][str(dp)]["median"]
        expected = 10 ** (-dp)
        assert m <= expected * 3, (
            f"dp={dp} median={m} exceeds 3x of 10^-{dp}"
        )
