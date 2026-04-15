# Precision-Sweep E156 — Prespecification

Date locked: 2026-04-15
Author: Mahmood Ahmad
Predecessor: SGLT2i-HFpEF E156 (FAIL branch shipped)

## Question

At what input-precision level does aggregate-data reproduction of
fixed-effects 2-trial pools become tolerance-limited by rounding
alone, independent of implementation correctness?

## Design (frozen)

- 10,000 Monte Carlo replications
- Each replication: one synthetic 2-trial pool
- True log-HR drawn from Uniform(log(0.6), log(1.3))
- Per-trial log-HR drawn from Normal(true_log_hr, se), se ~ Uniform(0.04, 0.08)
- Fixed-effects inverse-variance pool on log-HR scale
- Per dp in {1, 2, 3, 4}: round both HR and 95% CI bounds at dp
  decimal places, re-derive SE from rounded CI, re-pool
- Compare reproduced pooled HR to unrounded true pool HR
- Report |Δ| distribution per dp: median, 95th %ile, max, and fraction
  exceeding each of {0.001, 0.005, 0.01, 0.02}

## Deterministic seed (frozen)

- Generator: xoshiro128**
- Seed: 20260415 (single integer, committed to data.json)
- Commitment: regenerating results.json from data.json must produce
  byte-identical output, in both Python and JS implementations

## Claims (not decided here; recorded from the computation)

- Per-dp median, p95, max |Δ|
- Fraction at each tolerance threshold
- Monotonicity across dp
- Consistency check against the SGLT2i observed |Δ| = 0.007 at dp = 2
  (expect to fall below 99th percentile of the dp=2 distribution)

## Not decided here

- Random-effects, IPD, or k>2 precision floors (future papers)
- Whether to publish the Monte Carlo N = 10,000 is sufficient — sensitivity
  analysis at N = 20,000 will confirm p95 stability below 10⁻⁴ drift

## Paper Branches

None. This paper reports the empirical characterisation; it is always
shippable. No PASS/FAIL decision rule.
