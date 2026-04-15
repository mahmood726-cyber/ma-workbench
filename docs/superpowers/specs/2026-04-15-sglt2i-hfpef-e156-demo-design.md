# SGLT2i-HFpEF E156 Benchmark Demo — Design

Date: 2026-04-15
Workspace: `C:\Users\user\ma-workbench`
Owner: Mahmood Ahmad / mahmood726-cyber
Status: design approved, awaiting implementation plan

## Goal

Ship one E156 micro-paper (≤156 words, 7 sentences) plus one companion HTML page
inside `ma-workbench` that reproduces a published SGLT2i-HFpEF 2-trial pooled
hazard ratio (EMPEROR-Preserved + DELIVER), using only the browser-native apps
already shipping in `ma-workbench`.

The paper's claim is not clinical — it is tooling-reproducibility:

> Aggregate-data meta-analysis of the two trials, run in a browser via
> `ma-workbench`, lands within δ of a named published 2-trial pool.

Both the δ tolerance and the pooling method are frozen in `protocol.md`
before any computation runs. The paper ships in both PASS and FAIL branches
— a failed benchmark honestly reported is a valid E156; silently re-tuning
until it passes is not.

### Benchmark source — resolved at preflight, not in this spec

This spec deliberately does NOT name the specific benchmark paper, because
my best-effort recall produced an incorrect citation (Jhund 2022 *Nat Med*
pools DAPA-HF + DELIVER, not EMPEROR-Preserved + DELIVER). Preflight step 5
(below) requires verifying the actual HFpEF 2-trial pool citation from a
paper in hand and populating `expected.json` with:

- citation and DOI
- whether the benchmark pool is IPD-level or aggregate-data
- the reported HR + 95% CI (source of truth for `expected.json`)

δ is adaptive to pool type:

- **IPD benchmark** → δ = 0.02 (allows for aggregate-vs-IPD harmonisation drift)
- **Aggregate-data benchmark** → δ = 0.005 (no harmonisation gap; numbers should
  match to rounding)

The adaptive δ rule is itself prespecified in `protocol.md` so the decision
rule is fixed before compute — what's open is which branch of the rule applies.

## Non-Goals

- ✗ Not IPD re-analysis. No Cox refits, no person-years.
- ✗ Not a clinical synthesis adding new trials (PRESERVED-HF, CHIEF-HF stay out).
- ✗ Not a full journal paper. No PRISMA, no ROB traffic-light, no GRADE-SoF.
- ✗ Not a novel effect-size claim. The only claim is reproduction within the prespecified δ.
- ✗ Not a subgroup analysis. No EF strata, no eGFR strata, no demographics.
- ✗ Not a network meta-analysis. Two trials, one comparison.
- ✗ Does not alter the existing 15 apps. All 15 app tests must still pass
  byte-for-byte. This is a *consumer* of the workbench, not a change to it.
- ✗ Does not change the existing `e156-submission/` paper. New paper lives in
  `e156-submission-sglt2i/`.

## Benchmark Reference

**Status: to be confirmed at preflight.** This spec was drafted without
the benchmark paper in hand and an incorrect citation was caught at
self-review. The implementation plan MUST NOT proceed past preflight
step 5 without:

1. A named paper that reports an aggregate or IPD pooled HR for
   EMPEROR-Preserved + DELIVER on the primary composite endpoint,
   HFpEF population.
2. The reported HR and 95% CI (to populate `expected.json`).
3. DOI and journal reference (to populate `expected.json.benchmark.source`).
4. Pool type (IPD vs aggregate) — drives the δ branch in `protocol.md`.

### Candidate sources (verify, don't assume)

Candidates the user or the planner should check at preflight (this list is
not authoritative — any one of these, or another, could be the correct
benchmark):

- Vaduganathan M et al. *Lancet* 2022 — full-EF-spectrum 5-trial pool (may
  or may not report a HFpEF-restricted sub-analysis of the 2-trial kind).
- Accompanying editorial or meta-analysis letter published alongside
  DELIVER in *NEJM* 2022 that reported a fixed-effect pool of the two
  trials.
- Any subsequent Cochrane or ESC Heart Failure review that names the
  2-trial HFpEF pool.

### Expected shape of the benchmark number

Regardless of which paper turns out to be the benchmark, the ballpark
arithmetic is fixed: pooling HR 0.79 (EMPEROR-Preserved) and HR 0.82
(DELIVER) with I² ≈ 0 yields HR ≈ 0.80 with a 95% CI inside roughly
[0.73, 0.88]. Any benchmark paper reporting a 2-trial HFpEF composite
pool should land in that range. If the verified benchmark is outside
that range, flag as a red signal that the wrong paper or the wrong
endpoint has been selected.

## File Layout (new)

```
ma-workbench/
├── sglt2i-hfpef-demo/
│   ├── index.html            # companion page, 4 live panels + 4 greyed cards
│   ├── data.json             # trial inputs + full provenance
│   └── expected.json         # benchmark-pool numbers + provenance (source TBD)
├── e156-submission-sglt2i/
│   ├── paper.md              # 7 sentences, ≤156 words, rendered post-compute
│   ├── paper.json            # structured S1–S7 with word-count validation
│   ├── protocol.md           # prespecification; committed BEFORE compute
│   └── config.json
└── golden/
    └── datasets/
        └── G06-sglt2i-hfpef-benchmark.json   # 6th golden dataset
```

Two new top-level directories (not one) to separate the demo (the page
rendering the workbench on real data) from the paper (the text artefact
for the E156 stream). Each can ship or retract independently. The paper
can be tested without parsing HTML; the demo can be tested without
parsing Markdown.

## Data Inputs

Two log-HRs with standard errors, derived from the published NEJM primary
reports.

| Trial | Citation | Composite | HR (95% CI) | N | Source |
|---|---|---|---|---|---|
| EMPEROR-Preserved | Anker *NEJM* 2021;385:1451 | CV death + HF hosp | 0.79 (0.69–0.90) | 5988 | Table 2, p1455 |
| DELIVER | Solomon *NEJM* 2022;387:1089 | CV death + worsening HF | 0.82 (0.73–0.92) | 6263 | Table 2, p1092 |

Composite definitions differ — DELIVER includes urgent unplanned HF visits;
EMPEROR-Preserved does not. If the benchmark paper harmonised at IPD
level, we cannot replicate that harmonisation from aggregate data, which
is the reason δ = 0.02 under the IPD branch. If the benchmark paper is
aggregate-data, no harmonisation happened there either, so the δ = 0.005
branch applies. S7 of the E156 names this gap explicitly in both branches.

### `data.json` shape

```json
{
  "schema_version": "1.0",
  "trials": [
    {
      "id": "EMPEROR-Preserved",
      "hr": 0.79, "ci_low": 0.69, "ci_high": 0.90,
      "n_total": 5988, "n_events_total": null,
      "log_hr": -0.2357, "se_log_hr": 0.0675,
      "source": {
        "citation": "Anker SD et al. NEJM 2021;385:1451-61",
        "doi": "10.1056/NEJMoa2107038",
        "table": "Table 2, row 'Primary composite outcome'",
        "page": 1455,
        "accessed": "2026-04-15"
      }
    },
    { "id": "DELIVER", "...": "..." }
  ]
}
```

`log_hr` and `se_log_hr` are **derived** fields included for audit, not the
source of truth. `se_log_hr = (log(ci_high) - log(ci_low)) / (2 × 1.96)`.
Contract test: recomputing these from `hr`/`ci_low`/`ci_high` must match
the stored values to 4 decimal places.

`n_events_total` may be `null` if not reported in the primary table;
optional for weighting display, not required for GIV pooling.

### `expected.json` shape

```json
{
  "schema_version": "1.0",
  "benchmark": {
    "source": "<citation TBD at preflight>",
    "doi": "<DOI TBD at preflight>",
    "pool_type": "<ipd | aggregate>",
    "hr": 0.00, "ci_low": 0.00, "ci_high": 0.00,
    "accessed": "<YYYY-MM-DD, fixed at file creation>"
  },
  "tolerance": {
    "delta_hr_ipd_branch": 0.02,
    "delta_hr_aggregate_branch": 0.005,
    "applied_delta": 0.00,
    "applied_delta_source": "derived from benchmark.pool_type",
    "method": "REML random-effects, GIV on log-HR",
    "decision_rule": "|pooled_hr - benchmark.hr| <= applied_delta AND pooled 95% CI overlaps benchmark 95% CI"
  }
}
```

`accessed` is a human-authored content field (the ISO date the human
extracted the benchmark numbers from the source PDF) and is frozen at file
creation. It is NOT a build-time timestamp and does NOT re-stamp on
regeneration. Determinism gate stays clean.

`applied_delta` is computed once by `protocol.md`'s prespecification rule
from `pool_type` and then frozen. The plan must not compute it at each
test run (would be recomputed non-determinism).

### Fail-closed on inputs

If `data.json` or `expected.json` is missing, malformed, or any `source.*`
field is empty, the companion page refuses to render and prints an error
card. Mirrors the fail-closed non-negotiable in `CLAUDE.md`. The worst
outcome is a blank HR; never a wrong HR.

## Statistical Methods

Generic inverse-variance pool on log-HR scale; back-transform after.
Pre-determined by the estimand per `advanced-stats.md`: "Log scale: Always
pool logRR/logOR/logHR, back-transform after."

### Estimator matrix

| Method | Status | Reason |
|---|---|---|
| Fixed-effect (IVhet) | ✓ reported | Baseline; at I² ≈ 0 matches RE |
| REML random-effects | ✓ primary | Default for small k |
| Paule-Mandel RE | ✓ reported | Alternative τ² estimator; sanity check |
| DerSimonian-Laird | ✗ excluded | Banned at k<10 per `advanced-stats.md` |
| HKSJ-adjusted | ✓ reported, pre + post floor | `max(1, Q/(k-1))` floor; `qt(α/2, k-1)` not `qnorm` |

Five rows displayed in the method-comparison panel, one of them explicitly
✗ with reason. The DL exclusion is the teaching payload.

### Heterogeneity

Report τ², I², Q-stat, Q p-value together. Never I² without τ² (rule:
"I² ≠ magnitude. Measures proportion, not amount."). At k=2 with
matched-direction HRs, expected: τ² ≈ 0, I² ≈ 0, Q small.

### Explicitly not computed

Four greyed-out cards on the page with one-line reasons each:

- **Prediction interval** — "undefined at k<3; requires t_{k-2}"
- **Funnel plot / Egger** — "needs k ≥ 10 for meaningful asymmetry"
- **Trim-and-fill** — "sensitivity analysis; primary use requires larger k"
- **TSA** — "2 trials, already well-powered (n ≈ 12,000)"

These cards are the page's honesty contract: a reader who knows meta-analysis
will look for these outputs. Silently omitting them looks sketchy; greying
them with reason strings looks disciplined.

### Numerical implementation

All computation lives in the existing `forest-plot` and `heterogeneity`
apps (already shipping, already tested). The companion page embeds them
via `?fromBus=1` + postMessage. No new estimator code. If REML needs
small-k-safe initialisation, that belongs in `heterogeneity/` with its
own test, not in the demo page.

## Companion Page Layout

`sglt2i-hfpef-demo/index.html` — single HTML file, offline (no external
CDN per `html-apps.md`). Fetches `data.json` and `expected.json` on load.

Top-to-bottom read order:

1. Header — title, back-to-hub link, build SHA, regen date
2. **Claim card** — benchmark HR / workbench REML HR / δ / PASS or FAIL badge
3. Forest plot (embedded `forest-plot` app, `?fromBus=1`)
4. Method comparison table — 5 live rows + 1 ✗ row
5. Heterogeneity panel (embedded `heterogeneity` app)
6. Four greyed "not computed" cards
7. Input provenance (collapsed by default)
8. Paper card — links to the E156 paper and `protocol.md`

The **claim card is load-bearing**. It is the only card above the fold on
1080p. A reader who looks at nothing else sees the side-by-side HRs and
the PASS/FAIL badge and can close the tab.

### Determinism

No `Date.now()`, no `new Date().toISOString()` in rendered output. The
build string is wired to the git SHA at page-load (already the hub
pattern). No timestamps in `expected.json`, `data.json` (except the
fixed `accessed` field), or any generated reference. CI byte-check
remains clean.

### Storage

Demo page is read-only — it renders `data.json` and never stores user
edits. No `localStorage` usage at all. No collision surface with the 15
tool apps.

### Accessibility

- Claim card `aria-live="polite"` (PASS/FAIL badge appears after compute)
- Greyed cards `aria-disabled="true"` with visible reason text (not
  colour-only — colour alone conveys nothing to a screenreader)

### Mobile

Single-column stack at ≤ 640px. Forest plot and method table go
full-width. One viewport assertion at 375 px in the smoke test.

## E156 Body Skeleton

Seven sentences, one paragraph, ≤ 156 words total. Target word counts per
the E156 spec. Numbers in `{{braces}}` are filled from the `G06` references
at build time, not written by hand.

| S# | Role | Target | Draft |
|---|---|---:|---|
| S1 | Question | ~22w | "Does a browser-only meta-analysis workbench reproduce the published IPD-pooled hazard ratio for SGLT2 inhibitors on the primary composite endpoint in HFpEF?" |
| S2 | Dataset | ~20w | "Two trials, n=12,251: EMPEROR-Preserved (empagliflozin, 5988) and DELIVER (dapagliflozin, 6263), primary composite hazard ratios taken from published NEJM tables." |
| S3 | Method | ~20w | "Generic inverse-variance pooling on the log-hazard-ratio scale using REML random-effects, with fixed-effect, Paule-Mandel, and HKSJ-with-floor as sensitivity estimators." |
| S4 | Result | ~30w | "REML pool: HR `{{hr}}` (95% CI `{{lo}}`–`{{hi}}`), within δ=`{{delta}}` of the `{{benchmark_name}}` pool HR `{{bench_hr}}` (`{{bench_lo}}`–`{{bench_hi}}`); heterogeneity τ²=`{{tau2}}`, I²=`{{i2}}`%, Q-p=`{{qp}}`." |
| S5 | Robustness | ~22w | "Across four estimators the pooled HR spans `{{hr_lo}}`–`{{hr_hi}}` (range ≤0.03); DerSimonian-Laird is not reported because it is inappropriate at k<10." |
| S6 | Interpretation | ~22w | "Aggregate-data reproduction of the IPD pool within the prespecified tolerance supports the workbench as a credible browser-native re-analysis engine for small-k cardiovascular evidence." |
| S7 | Boundary | ~20w | "The pool uses as-published HRs without IPD-level harmonisation of composite definitions; prediction intervals, funnel plots, and trim-and-fill are undefined at k=2." |

### PASS and FAIL branches

Both drafts are committed to `paper.md`, gated by the computed `{{delta}}`:

- **PASS** (δ ≤ 0.02 AND CI overlap): S4/S6/S7 as above.
- **FAIL** (δ > 0.02 OR CI non-overlap): S4 reports the divergence; S6
  becomes a reason-for-divergence explanation; S7 lists suspected
  mechanisms (composite-definition drift, transcription error,
  estimator mis-spec).

Designing both branches up-front prevents post-hoc tuning. A FAIL is an
acceptable outcome; a retroactively-edited "benchmark" is not.

## Build Order

```
 1. protocol.md              # frozen first, committed alone
 2. data.json                # NEJM extractions + provenance
 3. expected.json            # benchmark numbers + provenance (source TBD)
 4. tests/test_sglt2i_benchmark.py   # 5 tests, TDD-style, red
 5. sglt2i-hfpef-demo/index.html     # orchestrator + 4 live + 4 greyed
 6. golden/datasets/G06-*.json + regeneration → tests green
 7. e156-submission-sglt2i/paper.md  # numbers filled from G06 refs
 8. hub/projects.js entry            # path-resolution test green
 9. Sentinel pre-push scan clean     # no new BLOCKs
10. CI verified green on push
11. Overmind nightly PASS for ma-workbench
12. INDEX.md row + rewrite-workbook.txt entry (SUBMITTED left blank)
13. E156 submission toggle (PASS branch AND Overmind PASS only)
```

Steps 1–2 are pre-registration. Each step lands in its own commit — no
mega-commit at the end.

## Preflight

Run BEFORE step 1. Any failure halts the plan and surfaces the specific
blocker to the user.

| # | Check | Command | Blocker if missing |
|---|---|---|---|
| 1 | Repo clean, on `master` | `git -C C:\Users\user\ma-workbench status` | Yes |
| 2 | Existing 15-app tests green | CI green on `master` HEAD | Yes |
| 3 | EMPEROR-Preserved NEJM Table 2 accessible | DOI 10.1056/NEJMoa2107038 | Yes |
| 4 | DELIVER NEJM Table 2 accessible | DOI 10.1056/NEJMoa2206286 | Yes |
| 5 | **Benchmark paper identified and HR verified from PDF** | citation + DOI + pool_type (ipd/aggregate) + HR + CI in hand | **Yes — this is the self-review hole** |
| 6 | Sentinel pre-push hook status for ma-workbench | `python -m sentinel scan --repo C:\Users\user\ma-workbench` | Yes — resolve existing BLOCKs before adding new work |
| 7 | Workbook + INDEX update plan confirmed | this spec approved | Yes |

## Success Criteria

Five tests in `tests/test_sglt2i_benchmark.py`, all running in CI on
every push. All five must pass for the E156 submission toggle.

1. `test_main_hr_within_tolerance` — `|pooled_hr − expected.json.benchmark.hr| ≤ expected.json.tolerance.applied_delta`.
2. `test_ci_overlaps_published` — workbench 95% CI overlaps benchmark 95% CI (non-empty intersection).
3. `test_methods_agree` — **absolute HR range** (max HR − min HR) across the four live estimators (FE, REML, PM, HKSJ-floored) is ≤ 0.03.
4. `test_dl_excluded` — method panel shows DL unavailable with reason string containing "k<10".
5. `test_undefined_panels` — PI, funnel, trim, TSA cards each emit the expected reason string (asserted verbatim per `advanced-stats.md` language).

Plus the existing CI gates extend automatically:

- `G06` golden-parity byte-for-byte check
- Per-app smoke (demo page becomes the 16th app in the matrix)
- `hub/projects.js` path resolution (new entry resolves)

## Failure Handling

Three distinct failure modes, each with a different response:

### Benchmark FAIL (δ exceeded or CI non-overlap)

- Workbench output goes into `paper.md` as-is. S4/S6/S7 switch branches.
- Demo page shows a diagnostic card listing three candidate causes:
  (1) transcription error in `data.json`,
  (2) composite-definition divergence larger than estimated,
  (3) estimator mis-spec.
- Does **not** block CI, push, INDEX update, or workbook entry. Blocks
  **only** the `SUBMITTED: [x]` toggle. Paper stays unsubmitted until
  the divergence is resolved or explicitly accepted as a finding.

### Sentinel BLOCK on pre-push

- `STUCK_FAILURES.md` / `.jsonl` appended with the specific rule violation.
- Do **not** bypass with `SENTINEL_BYPASS=1`. Fix the underlying
  violation — the rule encodes a past-incident lesson. Per the repo-root
  `STUCK_FAILURES.md` already visible in `ma-workbench`, Sentinel is live
  on this repo.
- Expected BLOCK surfaces for this work: hardcoded `C:\` paths in the
  demo page, committed `.claude/` configs, placeholder HMAC, or silent-
  failure sentinels. Design already forbids all four, so BLOCKs should
  not fire — if one does, the design has drifted.

### Overmind nightly FAIL

- Per `workflow.md` "Lifecycle evidence" rule: do not promote the project
  to CERTIFIED / Submission-ready without a recent Overmind PASS.
- Overmind FAIL blocks step 11 (E156 submission toggle) independently of
  the benchmark PASS/FAIL. Both gates must open.
- If Overmind FAILs but the benchmark PASSes: paper is ready, submission
  blocked until Overmind is resolved. Update workbook with CURRENT BODY
  but leave SUBMITTED unchecked.

## Registry Integration

- `C:\ProjectIndex\INDEX.md` — append sub-note "+ SGLT2i-HFpEF benchmark
  demo" to the existing `ma-workbench` row. Not a new row.
- `C:\E156\rewrite-workbook.txt` — new entry with **CURRENT BODY** =
  rendered S1–S7, **YOUR REWRITE** blank (workbook protection rule),
  **SUBMITTED: [ ]**, header total-count bumped by 1.
- `python C:\ProjectIndex\reconcile_counts.py` must remain green after
  the workbook update. If it fails, stop and surface the drift.
- **Overmind nightly** must show a recent PASS for `ma-workbench` before
  the `SUBMITTED` toggle flips per the lifecycle gate in `workflow.md`.
  If no recent Overmind verdict exists, trigger one; if it FAILs, resolve
  before toggling.

## Licence

- Demo page: MIT (same as `ma-workbench`).
- NEJM HR/CI values: factual, not copyrightable. Provenance citations
  required for attribution, no licence obligation.
- Benchmark-paper HR/CI values: factual, same as above.

## Out of Scope for This Spec (Deferred)

- SGLT2i-HFmrEF extension if the identified benchmark paper reports the
  EF 40–49% subset; would be a future E156.
- Secondary endpoints (CV death alone, HF hosp alone, KCCQ). One E156 per
  claim; this one is the composite.
- Bayesian re-pool with informative prior from HFrEF. Possible future
  paper, not this one.

## Open Questions (Resolved in Planning)

- **Benchmark paper identity and `expected.json` contents** — spec
  deliberately leaves the citation blank. Preflight step 5 resolves it.
  Until resolved, no code is written and no test runs.
- **HKSJ-pre-floor display** — spec shows both pre and post. Implementation
  plan may simplify to post-only if panel gets crowded; decide at
  `index.html` layout time.
- **Overmind trigger cadence** — spec requires a recent PASS; what counts
  as "recent" (24h? 7d?) is set by `workflow.md`'s lifecycle rule, not
  this spec. Implementation plan confirms the cadence.
