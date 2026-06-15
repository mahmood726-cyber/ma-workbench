"""
dgp.py -- Known-truth data-generating process for meta-analyses, with a
parameterised PUBLICATION-SELECTION mechanism on top of a known (mu, tau^2).
Seeded -> fully reproducible.

Ported from the allmeta truth-recovery yardstick (F:\\allmeta, branch
truth-recovery-unified-estimator) and the JS port dgp.mjs used across the
truth-recovery-* sweep. Standalone -- depends only on numpy.

A "meta-analysis" is the set of PUBLISHED studies a reviewer sees. Studies are
drawn from the true random-effects model; a selection rule decides which get
published; we oversample until k published studies are collected. So k is the
observed (published) count while the true mu is the unconditional mean any
honest method must recover.

Truth-first: every number a harness reports is produced from this seeded
process. Nothing is hand-entered.
"""
from __future__ import annotations
import numpy as np

SCENARIOS = ["none", "step_weak", "step_strong", "copas_weak", "copas_strong"]

_STEP_CUTS = np.array([0.025, 0.05])
_STEP_WEIGHTS = {"weak": np.array([1.0, 0.75, 0.55]),
                 "strong": np.array([1.0, 0.35, 0.10])}
_COPAS = {"weak": {"g0": -0.10, "g1": 0.12, "rho": 0.50},
          "strong": {"g0": -0.20, "g1": 0.12, "rho": 0.90}}


def _step_weight(p_one, weights):
    if p_one < _STEP_CUTS[0]:
        return weights[0]
    if p_one < _STEP_CUTS[1]:
        return weights[1]
    return weights[2]


def _draw_se(rng, k, se_lo, se_hi):
    lo, hi = np.log(se_lo), np.log(se_hi)
    return np.exp(lo + (hi - lo) * rng.random(k))


def generate(mu, tau2, k, scenario, rng, se_lo=0.10, se_hi=0.70, max_factor=400):
    """Return (yi, vi, info) for one published meta-analysis of observed size k.

    rng must be a numpy Generator (np.random.default_rng(seed)).
    """
    sd = np.sqrt(tau2)
    if scenario == "none":
        se = _draw_se(rng, k, se_lo, se_hi)
        yi = mu + sd * rng.standard_normal(k) + se * rng.standard_normal(k)
        return yi, se ** 2, {"nExamined": k, "k": k, "selFrac": 1.0, "degenerate": False}

    kind = "weak" if scenario.endswith("weak") else "strong"
    is_step = scenario.startswith("step")
    weights = _STEP_WEIGHTS[kind] if is_step else None
    cp = None if is_step else _COPAS[kind]

    keep_y, keep_se = [], []
    n_examined = 0
    cap = max_factor * k
    while len(keep_y) < k and n_examined < cap:
        b = max(k, 64)
        se = _draw_se(rng, b, se_lo, se_hi)
        for i in range(b):
            eps = rng.standard_normal()
            theta = mu + sd * rng.standard_normal()
            y = theta + se[i] * eps
            if is_step:
                from scipy.stats import norm
                p_one = 1.0 - norm.cdf(y / se[i])
                publish = rng.random() < _step_weight(p_one, weights)
            else:
                d = cp["rho"] * eps + np.sqrt(1 - cp["rho"] ** 2) * rng.standard_normal()
                z = cp["g0"] + cp["g1"] / se[i] + d
                publish = z > 0
            n_examined += 1
            if publish:
                keep_y.append(y)
                keep_se.append(se[i])
                if len(keep_y) >= k:
                    break

    degenerate = len(keep_y) < k
    while len(keep_y) < k:  # top up so downstream always sees k
        s = float(np.exp(np.log(se_lo) + (np.log(se_hi) - np.log(se_lo)) * rng.random()))
        keep_y.append(mu + sd * rng.standard_normal() + s * rng.standard_normal())
        keep_se.append(s)

    yi = np.array(keep_y[:k])
    se = np.array(keep_se[:k])
    return yi, se ** 2, {"nExamined": n_examined, "k": k,
                         "selFrac": k / max(1, n_examined), "degenerate": degenerate}
