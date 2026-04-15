"""Monte Carlo simulation of the aggregate-data reproduction precision floor.

For each replication:
  1. Draw a true log-HR uniformly from log-HR space
  2. Draw two per-trial log-HRs with sampling noise
  3. Compute the unrounded pooled HR (ground truth for this replication)
  4. For each dp: round both HR and CI, re-derive SE, re-pool
  5. Record |reproduced_hr - true_pooled_hr| per dp

Implementation is stdlib-only for byte-identical determinism. The
browser JS mirrors this algorithm exactly.
"""
from __future__ import annotations

import math
from typing import TypedDict

from precision_sweep.xoshiro import Xoshiro128SS


class PerDpStats(TypedDict):
    median: float
    p95: float
    max: float
    frac_gt_0p001: float
    frac_gt_0p005: float
    frac_gt_0p01: float
    frac_gt_0p02: float


def _iv_pool_log(log_hrs: list[float], ses: list[float]) -> tuple[float, float]:
    """Fixed-effects inverse-variance pool on log-HR scale.

    Returns (pooled_log_hr, pooled_se).
    """
    sw = 0.0
    swy = 0.0
    for logh, se in zip(log_hrs, ses):
        w = 1.0 / (se * se)
        sw += w
        swy += w * logh
    mu = swy / sw
    se_pooled = math.sqrt(1.0 / sw)
    return mu, se_pooled


def _round_trial_at_dp(
    hr: float, log_hr: float, se_log_hr: float, dp: int
) -> tuple[float, float]:
    """Return (rounded_log_hr, rounded_se) for a trial at dp precision.

    Rounding mimics published-paper extraction: HR reported at dp,
    95% CI bounds reported at dp. SE is re-derived from the rounded
    CI bounds, not preserved from the unrounded input.
    """
    # Original CI bounds from the unrounded trial
    ci_low = math.exp(log_hr - 1.96 * se_log_hr)
    ci_high = math.exp(log_hr + 1.96 * se_log_hr)
    # Round HR + CI at dp
    hr_r = round(hr, dp)
    lo_r = round(ci_low, dp)
    hi_r = round(ci_high, dp)
    # Guard against round-to-zero on small CI bounds at low dp
    if lo_r <= 0 or hi_r <= 0 or lo_r >= hi_r:
        # Fall back: use rounded HR + a minimum SE (10^-dp symmetric)
        return math.log(max(hr_r, 10 ** (-dp))), 10 ** (-dp)
    log_hr_r = math.log(hr_r) if hr_r > 0 else math.log(10 ** (-dp))
    se_r = (math.log(hi_r) - math.log(lo_r)) / (2 * 1.96)
    return log_hr_r, se_r


def run_simulation(
    seed: int,
    n_replications: int,
    true_hr_range: tuple[float, float],
    se_range: tuple[float, float],
    dp_levels: list[int],
) -> dict[str, PerDpStats | list]:
    """Run the MC and return per-dp stats plus first-10 audit draws."""
    rng = Xoshiro128SS(seed)
    log_range_lo = math.log(true_hr_range[0])
    log_range_hi = math.log(true_hr_range[1])
    se_lo, se_hi = se_range

    # deltas[dp] = list of |reproduced_hr - true_pooled_hr| per replication
    deltas: dict[int, list[float]] = {dp: [] for dp in dp_levels}
    audit_first_10: list[dict] = []

    for i in range(n_replications):
        true_log_hr = rng.uniform(log_range_lo, log_range_hi)
        se1 = rng.uniform(se_lo, se_hi)
        se2 = rng.uniform(se_lo, se_hi)
        # sample two trial log-HRs around the true
        log_hr_1 = true_log_hr + rng.normal(0.0, se1)
        log_hr_2 = true_log_hr + rng.normal(0.0, se2)

        hr_1 = math.exp(log_hr_1)
        hr_2 = math.exp(log_hr_2)

        # Unrounded pool (ground truth for this replication)
        true_pool_log, _ = _iv_pool_log([log_hr_1, log_hr_2], [se1, se2])
        true_pool_hr = math.exp(true_pool_log)

        if i < 10:
            audit_first_10.append({
                "true_log_hr": round(true_log_hr, 6),
                "hr_1": round(hr_1, 6),
                "hr_2": round(hr_2, 6),
                "se_1": round(se1, 6),
                "se_2": round(se2, 6),
                "true_pool_hr": round(true_pool_hr, 6),
            })

        for dp in dp_levels:
            log_hr_1_r, se_1_r = _round_trial_at_dp(hr_1, log_hr_1, se1, dp)
            log_hr_2_r, se_2_r = _round_trial_at_dp(hr_2, log_hr_2, se2, dp)
            pool_log_r, _ = _iv_pool_log(
                [log_hr_1_r, log_hr_2_r], [se_1_r, se_2_r]
            )
            pool_hr_r = math.exp(pool_log_r)
            deltas[dp].append(abs(pool_hr_r - true_pool_hr))

    per_dp: dict[str, PerDpStats] = {}
    for dp in dp_levels:
        vals = sorted(deltas[dp])
        n = len(vals)
        median = vals[n // 2]
        p95 = vals[int(0.95 * n)]
        mx = vals[-1]
        per_dp[str(dp)] = {
            "median": round(median, 6),
            "p95": round(p95, 6),
            "max": round(mx, 6),
            "frac_gt_0p001": round(sum(1 for v in vals if v > 0.001) / n, 4),
            "frac_gt_0p005": round(sum(1 for v in vals if v > 0.005) / n, 4),
            "frac_gt_0p01": round(sum(1 for v in vals if v > 0.01) / n, 4),
            "frac_gt_0p02": round(sum(1 for v in vals if v > 0.02) / n, 4),
        }

    return {
        "per_dp": per_dp,
        "audit_first_10": audit_first_10,
    }
