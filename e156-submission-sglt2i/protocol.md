# SGLT2i-HFpEF E156 Benchmark Demo — Prespecification

Date locked: 2026-04-15
Author: Mahmood Ahmad

## Question

Does ma-workbench, run in a browser on published aggregate-data inputs,
reproduce the Vaduganathan 2022 Lancet pooled hazard ratio for SGLT2
inhibitors vs placebo on the primary composite endpoint in HFpEF?

## Population

HFpEF (ejection fraction > 40%); two RCTs pooled:

- EMPEROR-Preserved (empagliflozin, n=5988)
- DELIVER (dapagliflozin, n=6263)

## Intervention / Comparator

Any SGLT2 inhibitor (empagliflozin or dapagliflozin) vs placebo.

## Outcome (Primary Estimand)

Trial-defined primary composite endpoint:

- EMPEROR-Preserved: CV death + HF hospitalisation
- DELIVER: CV death + worsening HF (includes hospitalisation + urgent HF visits)

Pooled on the log-hazard-ratio scale using generic inverse-variance.

## Inputs (frozen)

| Trial | HR | 95% CI | Source |
|---|---|---|---|
| EMPEROR-Preserved | 0.79 | (0.69, 0.90) | Anker NEJM 2021;385:1451, Table 2 |
| DELIVER | 0.82 | (0.73, 0.92) | Solomon NEJM 2022;387:1089, Table 2 |

## Benchmark (frozen)

- Citation: Vaduganathan M et al. Lancet 2022;400:757-767
- DOI: 10.1016/S0140-6736(22)01429-5
- Pool type: aggregate (fixed-effects meta-analysis per published abstract)
- Reported HR: 0.80 (95% CI 0.73-0.87)

## Pooling Method (frozen, primary)

REML random-effects, generic inverse-variance on log-HR scale.

## Sensitivity Estimators (frozen)

- Fixed-effect (IVhet)
- Paule-Mandel random-effects
- HKSJ-adjusted with floor `max(1, Q/(k-1))` and `qt(alpha/2, k-1)`

DerSimonian-Laird is excluded per the k<10 rule and will be displayed
greyed on the method-comparison panel with reason string "k<10".

## Decision Rule (frozen)

### Primary decision

applied_delta = 0.005 (benchmark is aggregate-data pool; this is the
tight branch of the adaptive rule. The 0.02 IPD branch does not apply).

PASS iff both:

1. |pooled_hr - 0.80| <= 0.005
2. pooled 95% CI overlaps benchmark 95% CI (0.73, 0.87) — non-empty intersection

Otherwise FAIL.

### Method-range decision

Across the four live estimators (FE, REML, PM, HKSJ-floored), the
absolute HR range (max HR - min HR) must be <= 0.03.

## Paper Branches (frozen)

PASS branch and FAIL branch wording both committed to paper.md ahead
of compute. Only the S4/S6/S7 fill-ins change between branches; the
seven-sentence structure is identical.

## What is NOT Decided Here

- The pooled HR, CI, tau-squared, I-squared, Q-p values (computed by the workbench).
- Which paper branch ships (driven by the decision rule above).
- Whether SUBMITTED is toggled (gated additionally by Overmind PASS).
