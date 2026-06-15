# ma-workbench — Truth-Recovery Validation

**Repo:** mahmood726-cyber/ma-workbench
**Engine under test:** golden/generate_references.py::pool — the Paule-Mandel random-effects pooler that the 14 browser tools mirror in JS (FE + RE-PM, tau2 by PM bisection, I2, Q, PI). Imported VERBATIM, not reimplemented.
**Date:** 2026-06-15

## What ma-workbench does
A suite of 14 meta-analysis browser tools (forest, funnel, heterogeneity, meta-regression, NMA, TSA, DTA-SROC, GRADE, PRISMA, etc.). The shared pooling core computes a random-effects pool via Paule-Mandel tau2 and reports a 95% CI as mu +/- 1.96*se (WALD, normal critical value). A golden/ harness already validates the point estimates against metafor to 1e-8.

## The danger: coverage of true mu
The shipped RE CI is Wald (normal z=1.96) and ignores the uncertainty in the estimated tau2. With small k and real heterogeneity this is known to be ANTI-CONSERVATIVE. The recommended fix is the Hartung-Knapp-Sidik-Jonkman (HKSJ) variance with a t_{k-1} critical value. We measured both against known truth.

## Method
- Known-truth DGP (shared kit dgp.py, scenario "none"): draw from true (mu=0.30, tau2) random-effects model, k studies, vi = se^2. 3000 Monte-Carlo reps per cell.
- Wire the engine's pool(); compare its shipped Wald CI vs a PM+HKSJ t_{k-1} CI (same PM point + tau2, HKSJ floor max(1, .) per Cochrane).
- Coverage = fraction of 95% CIs containing the true mu.

## Results (3000 reps/cell)
| mu | tau2 | k | cov_Wald (shipped) | cov_HKSJ (fix) | width_Wald | width_HKSJ | bias |
|---|---|---|---|---|---|---|---|
| 0.30 | 0.00 | 5  | 0.967 | 0.996 | 0.474 | 0.672 | +0.0010 |
| 0.30 | 0.00 | 10 | 0.961 | 0.979 | 0.305 | 0.352 | +0.0017 |
| 0.30 | 0.05 | 5  | **0.876** | 0.957 | 0.605 | 0.857 | +0.0033 |
| 0.30 | 0.05 | 10 | **0.906** | 0.939 | 0.416 | 0.481 | +0.0012 |
| 0.30 | 0.15 | 5  | **0.866** | 0.942 | 0.811 | 1.148 | +0.0051 |
| 0.30 | 0.15 | 8  | **0.895** | 0.943 | 0.650 | 0.784 | +0.0010 |
| 0.30 | 0.15 | 15 | 0.920 | 0.942 | 0.481 | 0.527 | +0.0020 |

## Verdict: HONEST-NEGATIVE (confirmed, textbook) + IMPROVEMENT
- Engine math correct: point estimate is unbiased (|bias| <= 0.005 throughout) and matches metafor (golden parity 1e-8).
- **Confirmed anti-conservative coverage of the shipped Wald RE CI under heterogeneity + small k**: as low as 0.866 (tau2=0.15, k=5) and 0.876 (tau2=0.05, k=5), i.e. ~8-9 coverage-points below nominal. The defect is in the INTERVAL, not the estimate.
- HKSJ t_{k-1} restores ~0.94-0.96 coverage (wider intervals).
- When tau2_true=0 (homogeneous), the Wald CI is approximately valid (0.96-0.97) — no false alarm.

## Recommendation
For the random-effects tools, offer (and default to, when k is modest) the HKSJ / Knapp-Hartung CI with a t_{k-1} critical value and the max(1, .) floor, rather than the bare Wald mu +/- 1.96*se. At minimum, surface a small-k heterogeneity warning that the Wald RE CI is anti-conservative. (Separately noted: the prediction interval uses t_{k-2}; the allmeta house standard is t_{k-1} per Cochrane v6.5 — worth aligning, but outside this coverage finding.)
