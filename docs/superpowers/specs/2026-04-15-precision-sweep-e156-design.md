# Precision-Sweep E156 (Follow-up to SGLT2i-HFpEF FAIL) — Design

Date: 2026-04-15
Workspace: `C:\Users\user\ma-workbench`
Owner: Mahmood Ahmad / mahmood726-cyber
Status: design, awaiting implementation plan
Predecessor: `2026-04-15-sglt2i-hfpef-e156-demo-design.md` (FAIL-branch paper shipped)

## Goal

Ship one E156 micro-paper plus a companion HTML page in `ma-workbench`
that characterises the **aggregate-data reproduction precision floor**
for 2-trial fixed-effects inverse-variance pools. The SGLT2i paper
revealed a real constraint — |Δ| = 0.007 against a benchmark published
at 2-dp input precision — but did not quantify the floor. This paper
does.

The claim is methodological, not clinical:

> When two trial HRs are reported at `dp` decimal places and pooled
> by aggregate-data fixed-effects inverse-variance, the distribution
> of |computed HR − true pooled HR| has a characteristic floor that
> scales with 10⁻ᵈᵖ. Any benchmark-reproduction tolerance set
> tighter than that floor will FAIL on the input precision alone,
> independent of implementation correctness.

This converts the SGLT2i FAIL finding into a generalisable rule:
*aggregate-data reproduction requires δ ≥ f(dp)*, where f is quantified
empirically here.

## Non-Goals

- ✗ Not a benchmark reproduction. No external pool citation; no
  `expected.json` pointing at a published paper.
- ✗ Not new clinical evidence. No real trial data.
- ✗ Not IPD, Bayesian, or random-effects tau² analysis. This is about
  the arithmetic precision of fixed-effects inverse-variance pooling.
- ✗ Not a replacement for the SGLT2i FAIL paper. Both ship as separate
  E156 entries; this one builds on the first.
- ✗ Does not alter any of the 16 existing apps or the 6 golden datasets.
  Adds `G07-precision-sweep` as a 7th golden dataset.
- ✗ No dependency on the SGLT2i demo infrastructure — each E156 is
  self-contained per workbench convention.

## Experimental Design

### Population (synthetic)

10 000 Monte Carlo replications. Each replication constructs one
synthetic 2-trial pool:

1. Draw a "true" pooled log-HR from `Uniform(log(0.6), log(1.3))`
   — covers the clinically plausible range [0.6, 1.3] on HR scale.
2. Draw two trial log-HRs from `Normal(true_log_hr, σ)` where
   `σ² = τ² + se²` and `τ² = 0` (fixed-effects world) and `se` is
   sampled from `Uniform(0.04, 0.08)` (matches typical real-trial SE
   range for HFpEF-scale trials).
3. Compute the "true" fixed-effects inverse-variance pool from the
   unrounded trial HRs — this is the ground truth.
4. For each `dp ∈ {1, 2, 3, 4}`, round each trial HR to `dp` decimal
   places and re-pool — this is the "as-published reproduction".
5. Record `|reproduced_hr − true_pooled_hr|` per replication per `dp`.

### Deterministic seed

Fixed seed (PCG32 or xoshiro128**). Committed to `protocol.md` and
`G07` dataset. No `Math.random()` in browser; no `random.random()` in
Python. Reproducibility is a P0 feature of this paper — every run
must produce byte-identical outputs.

### Output distribution

Per `dp`, report:
- Median |Δ|
- 95th-percentile |Δ|
- Maximum |Δ| observed
- Proportion with |Δ| > 0.005 (the SGLT2i aggregate-branch tolerance)
- Proportion with |Δ| > 0.02 (the SGLT2i IPD-branch tolerance)

## File Layout (new)

```
ma-workbench/
├── precision-sweep-demo/
│   ├── index.html            # companion page, 4 panels (see below)
│   ├── data.json             # MC draw inputs (seed, N, true-HR range, SE range)
│   └── results.json          # computed distributions per dp
├── e156-submission-precision-sweep/
│   ├── paper.md              # 7 sentences, ≤156 words
│   ├── paper.json            # structured S1–S7
│   ├── protocol.md           # prespecification; committed BEFORE compute
│   └── config.json
└── golden/
    └── datasets/
        └── G07-precision-sweep.json   # 7th golden dataset
```

## `data.json` — inputs (frozen)

```json
{
  "schema_version": "1.0",
  "seed": 20260415,
  "generator": "xoshiro128**",
  "n_replications": 10000,
  "true_hr_range": [0.6, 1.3],
  "se_range": [0.04, 0.08],
  "dp_levels": [1, 2, 3, 4],
  "pool_method": "fixed-effects inverse-variance on log-HR scale",
  "comment": "Fixed-effects pool at tau2=0. 2-trial structure (k=2). SE drawn uniformly to match typical HFpEF-scale trials."
}
```

## `results.json` — outputs (computed and committed)

```json
{
  "schema_version": "1.0",
  "per_dp": {
    "1": {"median": 0.0..., "p95": 0.0..., "max": 0.0...,
          "frac_gt_0p005": 0.00, "frac_gt_0p02": 0.00},
    "2": {...},
    "3": {...},
    "4": {...}
  },
  "seed_verification": "first_10_true_hrs_to_6dp_for_audit",
  "generator_version": "C:\\Users\\user\\ma-workbench\\precision-sweep-demo\\<script_id>@<sha>"
}
```

Re-running the generator must produce byte-identical `results.json`.
The existing CI byte-for-byte gate extends to this paper automatically
because `G07` is a golden dataset.

## Statistical Analysis

Per replication, at each `dp`:
- Round HRs to `dp` decimal places: `round(hr, dp)`
- Recompute `se_log_hr = (log(ci_high) - log(ci_low)) / 3.92` from
  the rounded CIs *if* we simulate CI reporting at the same `dp`. But
  the trials report HR + CI at the same precision in practice, so
  rounding only HR and preserving exact SE would understate the floor.
  **Decision: round BOTH hr and the log-CI bounds at dp, re-derive se
  from the rounded CI.** This matches how a human re-extracts data from
  a published paper.
- Pool the rounded trials via fixed-effects inverse-variance on log-HR.
- Back-transform to HR scale.
- Compute |reproduced_hr − true_pooled_hr|.

### What the paper does NOT claim

- Random-effects or IPD precision floors (out of scope; possible future paper)
- k > 2 floors (adding trials typically reduces |Δ| because errors average; out of scope)
- Non-uniform true-HR distributions (sensitivity belongs in a future paper)

## Companion Page Layout

`precision-sweep-demo/index.html` — single HTML file, offline.

Top-to-bottom panels:

1. **Header** — title, build SHA, link back to hub
2. **Claim card** — one-line summary of the empirical floor:
   "At dp=2, median |Δ| = 0.0X, 95th %ile = 0.0X, X% of pools fail at δ=0.005."
3. **Precision-floor plot** — SVG bar chart, one bar per `dp`, showing
   median and 95th %ile |Δ|. Bus-agnostic; no `?fromBus=1` embed
   needed (this paper is self-contained).
4. **Pass-rate table** — per `dp`, fraction of pools that WOULD have
   passed at common tolerance levels (0.001, 0.005, 0.01, 0.02).
5. **Methodology expandable** — collapsed by default; shows the seed,
   generator, pool formula, round-both-HR-and-CI decision.
6. **Reference to predecessor paper** — link to the SGLT2i-HFpEF demo
   with note: "this paper's finding: the SGLT2i |Δ|=0.007 at dp=2 is
   inside the observed distribution for that precision — not an outlier."

No embedded apps. No `ma-studies-v1` bus publish. The SGLT2i demo
used `forest-plot` + `heterogeneity`; this paper is about distributional
statistics, which none of the existing 16 apps plot. The SVG plot is
bespoke, 20–30 lines of JS.

## E156 Body Skeleton

| S# | Role | Target | Draft (subject to compute) |
|---|---|---:|---|
| S1 | Question | ~22w | "At what input-precision level does aggregate-data reproduction of fixed-effects 2-trial pools become tolerance-limited by rounding alone, independent of implementation correctness?" |
| S2 | Dataset | ~20w | "Ten thousand Monte Carlo 2-trial pools: true log-HR ∼ Uniform(log 0.6, log 1.3), trial SE ∼ Uniform(0.04, 0.08), xoshiro128** seed 20260415." |
| S3 | Method | ~20w | "Each pool rounded to dp ∈ {1,2,3,4} decimal places on both HR and CI bounds, re-pooled, compared to unrounded pool." |
| S4 | Result | ~30w | "Median \|Δ\| at dp=1/2/3/4: `{{m1}}`/`{{m2}}`/`{{m3}}`/`{{m4}}`; 95th %ile: `{{p1}}`/`{{p2}}`/`{{p3}}`/`{{p4}}`; at dp=2 `{{frac2_gt_0005}}` of pools exceed δ=0.005." |
| S5 | Robustness | ~22w | "Floor scales monotonically with 10⁻ᵈᵖ; doubling Monte Carlo N to 20 000 shifts p95 by less than 10⁻⁴ at every dp level." |
| S6 | Interpretation | ~22w | "Benchmark-reproduction tolerance must exceed the precision floor at the input dp; δ=0.005 at dp=2 lies below the `{{p95_dp2}}` p95, explaining the prior SGLT2i FAIL." |
| S7 | Boundary | ~20w | "Scope restricted to k=2, fixed-effects, unimodal true-HR distribution; random-effects, k>2, and IPD precision floors remain open questions." |

Word budget: ~150 words after fills. No PASS/FAIL branches — this
paper's claim is a characterisation, not a benchmark. It *always*
ships with whatever numbers come out.

## Build Order

```
1. protocol.md                 # frozen first, committed alone
2. data.json                   # MC inputs; seed + ranges fixed
3. tests/test_precision_sweep_schema.py  # schema contract test (TDD-red)
4. precision_sweep/simulate.py # Python implementation of the MC (golden-parity mirror)
5. golden/datasets/G07-precision-sweep.json + generator extension
6. Regenerate references; CI byte-for-byte gate covers G07
7. precision-sweep-demo/index.html # companion page, reads data.json + results.json
8. tests/test_precision_sweep_paper.py # paper contract tests (7 sentences, <=156 w, no braces)
9. e156-submission-precision-sweep/paper.md  # rendered from results.json
10. hub/projects.js entry (17th)
11. .github/workflows/test.yml — 17th smoke target
12. Sentinel scan + push + CI verify + Pages
13. INDEX.md sub-note + workbook entry [482/482]
```

No Overmind / SUBMITTED branching — this paper is always shippable
(the claim is "here's the floor"; there's no PASS/FAIL decision).

## Preflight (minimal)

| # | Check | Blocker if missing |
|---|---|---|
| 1 | Repo clean on `main` | Yes |
| 2 | Existing 16-app tests green (including SGLT2i) | Yes |
| 3 | Sentinel pre-push clean | Yes |
| 4 | Python `numpy` available for MC draws (or a pure-stdlib PRNG) | Yes |
| 5 | No preflight data lookup required — this paper has no clinical inputs | — |

Much shorter preflight than the SGLT2i paper because no NEJM PDF
extraction, no benchmark-paper identification, no clinical claim to
cross-check.

## Success Criteria

Five tests. All must pass on every push (no branch-conditional
assertions needed — this paper doesn't branch).

1. `test_seed_deterministic` — regenerating `results.json` from
   `data.json` produces byte-identical output.
2. `test_monotonic_in_dp` — median |Δ| at dp=k is ≥ median |Δ| at
   dp=k+1 for k ∈ {1, 2, 3}.
3. `test_scale_with_ten_pow_minus_dp` — median |Δ| at dp=k is within
   a factor of 3 of 10⁻ᵏ (loose but directional sanity).
4. `test_sglt2i_floor_consistency` — the SGLT2i observed |Δ|=0.007 at
   dp=2 falls below the 99th percentile of the dp=2 distribution (i.e.
   not an implementation bug in the prior paper, just inside the
   expected tail).
5. `test_paper_contract` — 7 sentences, ≤156 words, no unfilled braces,
   S4 HR fill values match `results.json`.

Plus:
- `G07` byte-for-byte CI gate
- 17th per-app smoke in CI
- Hub path resolution

## Registry Integration

- `INDEX.md` row 477 sub-note: "+ precision-sweep E156 2026-04-15
  (methodological follow-up to SGLT2i FAIL)"
- `rewrite-workbook.txt` entry [482/482]: CURRENT BODY = rendered
  S1–S7, YOUR REWRITE blank, SUBMITTED [ ]
- `reconcile_counts.py` must remain OK

## Licence

MIT for the demo page. No clinical data involved; the synthetic Monte
Carlo outputs are factual by construction and not copyrightable.

## Out of Scope for This Spec (Deferred to Future Papers)

- Random-effects precision floor (τ² > 0 changes the floor structure)
- k > 2 precision floor (more trials → averaging reduces |Δ|)
- IPD-equivalent precision floor (IPD has no aggregate-rounding stage)
- Sensitivity to non-uniform true-HR distributions
- Alternative SE-to-CI conversion methods

## Open Questions (Resolved in Planning)

- **Browser-side MC vs Python-only MC.** Browser MC with xoshiro128**
  is deterministic and audit-friendly; Python is easier to test
  directly. **Decision at plan time**: both, with mutual cross-check
  at 6 dp tolerance — Python generates the committed `G07` reference,
  browser regenerates client-side and asserts match. This mirrors the
  existing WebR-validator pattern.
- **Plot type.** Currently specified as a bar chart (median + 95th %ile
  per dp). Alternative: violin plot or CDF curves. Bar chart is most
  readable at 4 bars; violins would add more info at the cost of 40
  extra lines of SVG. **Default: bars; revisit if the paper's reviewer
  asks for more distributional detail.**

## Predecessor Note

This paper is a scientific CHILD of the SGLT2i-HFpEF FAIL paper, not
a replacement. The SGLT2i FAIL stands as a real-data demonstration;
this paper quantifies the methodological finding it exposed. The
workbench now ships both: one benchmark reproduction with an honest
FAIL outcome, and one synthetic precision-sweep that explains why
that outcome was expected.
