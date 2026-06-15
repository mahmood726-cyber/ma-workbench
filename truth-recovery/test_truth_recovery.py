"""
test_truth_recovery.py — assertions for ma-workbench truth-recovery findings.

Run:  python -m pytest truth-recovery/test_truth_recovery.py -q
  or: python truth-recovery/test_truth_recovery.py
"""
import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "golden"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_references import pool  # noqa: E402
from harness import run_coverage, hksj_ci  # noqa: E402

# Cached Monte-Carlo runs (deterministic seeds)
_HET_K5 = run_coverage(mu_true=0.30, tau2_true=0.15, k=5, n_sim=3000)
_HET_K8 = run_coverage(mu_true=0.30, tau2_true=0.15, k=8, n_sim=3000)
_HOM_K10 = run_coverage(mu_true=0.30, tau2_true=0.00, k=10, n_sim=3000)


def test_engine_pool_sane():
    """Repo's pool() returns finite RE-PM estimate near truth on a clean draw."""
    studies = [{"label": "a", "est": 0.28, "se": 0.10},
               {"label": "b", "est": 0.32, "se": 0.12},
               {"label": "c", "est": 0.30, "se": 0.11}]
    r = pool(studies)["re_pm"]
    assert math.isfinite(r["estimate"]) and math.isfinite(r["se"]) and r["se"] > 0
    assert abs(r["estimate"] - 0.30) < 0.15


def test_point_estimate_is_unbiased():
    """The RE-PM point estimate is NOT the problem — bias is negligible."""
    assert abs(_HET_K5["mean_bias"]) < 0.02
    assert abs(_HET_K8["mean_bias"]) < 0.02


def test_shipped_wald_undercovers_under_heterogeneity():
    """KEY FINDING: the engine's shipped PM + Wald 95% CI under-covers true mu
    when real heterogeneity is present with small k (anti-conservative)."""
    assert _HET_K5["coverage_engine_wald"] < 0.92
    assert _HET_K8["coverage_engine_wald"] < 0.92


def test_hksj_restores_nominal_coverage():
    """HKSJ t_{k-1} CI restores coverage close to nominal 95% and is wider."""
    assert _HET_K5["coverage_hksj_t"] > _HET_K5["coverage_engine_wald"] + 0.03
    assert _HET_K8["coverage_hksj_t"] > _HET_K8["coverage_engine_wald"] + 0.03
    assert 0.93 <= _HET_K5["coverage_hksj_t"] <= 0.97
    assert _HET_K5["mean_width_hksj"] > _HET_K5["mean_width_wald"]


def test_wald_ok_when_homogeneous():
    """When tau2_true = 0, Wald is approximately valid (no spurious alarm)."""
    assert _HOM_K10["coverage_engine_wald"] >= 0.94
