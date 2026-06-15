"""
harness.py — Truth-recovery harness for ma-workbench.

Wires ma-workbench's OWN core pooling engine (golden/generate_references.py::pool,
the Paule-Mandel random-effects estimator the 14 browser tools mirror in JS)
against a known-truth DGP (the shared truth-recovery kit dgp.py).

CENTRAL QUESTION (coverage of true mu):
  The engine reports the RE-PM pooled estimate with a WALD 95% CI (mu +/- 1.96*se).
  With few studies and real heterogeneity, the Wald interval is known to be
  ANTI-CONSERVATIVE: it ignores the uncertainty in the tau2 estimate and uses a
  normal (not t) critical value. The Hartung-Knapp-Sidik-Jonkman (HKSJ) variance
  with a t_{k-1} critical value is the recommended fix.

  We measure, against known (mu, tau2):
    - coverage of true mu by the engine's PM + Wald 95% CI  (as shipped)
    - coverage by PM + HKSJ t_{k-1} 95% CI                  (recommended)
  across small k and a range of true tau2. Under-coverage of the shipped Wald
  CI demonstrates the hazard; HKSJ should restore ~95%.

Run:  python truth-recovery/harness.py
"""
import sys
import math
from pathlib import Path

import numpy as np

# ma-workbench's OWN engine
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "golden"))
from generate_references import pool, weighted_sums, tau2_pm  # noqa: E402

# shared known-truth DGP kit (vendored copy first, kit fallback)
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from dgp_kit import generate  # vendored, self-contained  # noqa: E402
except ImportError:  # pragma: no cover
    sys.path.insert(0, r"C:\Projects\truth-recovery-sweep\_kit")
    from dgp import generate  # noqa: E402


def _t_quantile_975(df):
    """t_{0.975, df} via a small table + interpolation (mirrors engine table)."""
    table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447,
             7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179,
             13: 2.160, 14: 2.145, 15: 2.131, 20: 2.086, 30: 2.042, 60: 2.000}
    if df <= 0:
        return float("nan")
    if df in table:
        return table[df]
    if df > 60:
        return 1.96
    keys = sorted(table)
    for k1, k2 in zip(keys, keys[1:]):
        if k1 <= df <= k2:
            w = (df - k1) / (k2 - k1)
            return table[k1] + w * (table[k2] - table[k1])
    return 1.96


def hksj_ci(studies, mu, tau2):
    """
    PM point estimate + HKSJ (Knapp-Hartung) variance with t_{k-1}.
    q_gen = (1/(k-1)) * sum w*_i (y_i - mu)^2 ; se_hksj = sqrt(q_gen / sum w*_i).
    Floor q_gen at 1 (per advanced-stats rule: HKSJ narrows below DL if Q<k-1).
    """
    k = len(studies)
    if k < 2:
        return (float("nan"), float("nan"))
    sw = 0.0
    num = 0.0
    for s in studies:
        w = 1.0 / (s["se"] ** 2 + tau2)
        sw += w
        num += w * (s["est"] - mu) ** 2
    q_gen = num / (k - 1)
    q_gen = max(1.0, q_gen)  # HKSJ floor
    se_hksj = math.sqrt(q_gen / sw)
    tcrit = _t_quantile_975(k - 1)
    return (mu - tcrit * se_hksj, mu + tcrit * se_hksj)


def run_coverage(mu_true=0.30, tau2_true=0.05, k=6, n_sim=3000, seed0=2000):
    """Monte-Carlo coverage of true mu: engine Wald vs HKSJ t_{k-1}."""
    cov_wald = 0
    cov_hksj = 0
    width_wald = 0.0
    width_hksj = 0.0
    bias = 0.0
    for s in range(n_sim):
        rng = np.random.default_rng(seed0 + s)
        yi, vi, info = generate(mu_true, tau2_true, k, "none", rng)
        studies = [{"label": str(i), "est": float(yi[i]), "se": float(math.sqrt(vi[i]))}
                   for i in range(k)]
        res = pool(studies)
        re = res["re_pm"]
        mu_hat = re["estimate"]
        # engine's shipped Wald CI
        lb, ub = re["ci_lb"], re["ci_ub"]
        if lb <= mu_true <= ub:
            cov_wald += 1
        width_wald += (ub - lb)
        bias += mu_hat - mu_true
        # HKSJ recommended CI (same PM point + tau2)
        hlb, hub = hksj_ci(studies, mu_hat, re["tau2"])
        if hlb <= mu_true <= hub:
            cov_hksj += 1
        width_hksj += (hub - hlb)
    return {
        "mu_true": mu_true, "tau2_true": tau2_true, "k": k, "n_sim": n_sim,
        "coverage_engine_wald": cov_wald / n_sim,
        "coverage_hksj_t": cov_hksj / n_sim,
        "mean_width_wald": width_wald / n_sim,
        "mean_width_hksj": width_hksj / n_sim,
        "mean_bias": bias / n_sim,
    }


if __name__ == "__main__":
    print("=" * 78)
    print("ma-workbench truth-recovery: coverage of true mu (PM Wald vs HKSJ t)")
    print("Engine = golden/generate_references.py::pool (the shipped RE-PM pooler)")
    print("=" * 78)
    grid = [
        (0.30, 0.00, 5), (0.30, 0.00, 10),
        (0.30, 0.05, 5), (0.30, 0.05, 10),
        (0.30, 0.15, 5), (0.30, 0.15, 8), (0.30, 0.15, 15),
    ]
    print(f"\n{'mu':>5} {'tau2':>6} {'k':>4} | {'cov_Wald':>9} {'cov_HKSJ':>9} "
          f"{'w_Wald':>8} {'w_HKSJ':>8} {'bias':>8}")
    print("-" * 78)
    for mu_t, t2, k in grid:
        r = run_coverage(mu_true=mu_t, tau2_true=t2, k=k, n_sim=3000)
        print(f"{mu_t:5.2f} {t2:6.2f} {k:4d} | "
              f"{r['coverage_engine_wald']:9.3f} {r['coverage_hksj_t']:9.3f} "
              f"{r['mean_width_wald']:8.3f} {r['mean_width_hksj']:8.3f} {r['mean_bias']:8.4f}")
    print("\nDone.")
