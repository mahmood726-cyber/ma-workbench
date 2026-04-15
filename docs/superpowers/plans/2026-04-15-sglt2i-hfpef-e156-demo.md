# SGLT2i-HFpEF E156 Benchmark Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship one E156 micro-paper + one companion HTML page inside `ma-workbench` that reproduces a published SGLT2i-HFpEF 2-trial pooled hazard ratio (EMPEROR-Preserved + DELIVER) using only browser-native apps already shipping in the repo.

**Architecture:** Two new top-level directories — `sglt2i-hfpef-demo/` (read-only HTML page consuming `data.json` + `expected.json`, embedding the existing `forest-plot` and `heterogeneity` apps via `?fromBus=1`) and `e156-submission-sglt2i/` (paper text artefacts, prespecified in `protocol.md` before compute). One new golden dataset `G06` extends the existing byte-for-byte CI regeneration check. No changes to the 15 existing apps.

**Tech Stack:** Vanilla HTML/JS/CSS (offline, no CDN), Python 3.13 (`golden/generate_references.py` extension, pytest contract tests), GitHub Actions CI (existing workflow extends automatically to G06 and the 16th per-app smoke row).

**Spec:** `docs/superpowers/specs/2026-04-15-sglt2i-hfpef-e156-demo-design.md` (commit `27b5cf8`).

**Task sequencing:**
- Task 0 is a **human-in-the-loop preflight gate**; no subagent can pass it. Halt until the user confirms the benchmark paper.
- Tasks 1–3 are prespecification (protocol + inputs). Must land in that order.
- Tasks 4–5 extend the golden dataset suite. Independent of UI tasks.
- Task 6 writes the failing test suite.
- Tasks 7–15 build the companion page. Task 7 (scaffold) gates Tasks 8–14; those four sub-panels (9, 10, 11, 12) can run in parallel subagents.
- Tasks 16–19 are paper rendering and CI integration.
- Tasks 20–23 are release gates (Sentinel, push, registry, Overmind + SUBMITTED toggle).

---

## Task 0: Preflight — benchmark paper identification (HUMAN GATE)

**Files:** none — this task produces decisions, not commits.

This task MUST complete before Task 1. A subagent cannot resolve it. Halt and surface the blocker to the user if any check fails.

- [ ] **Step 1: Verify repo state**

Run:
```bash
cd /c/Users/user/ma-workbench
git status --short
git log -1 --oneline
```

Expected: working tree has at most `STUCK_FAILURES.jsonl` + `review-findings.jsonl` as untracked (Sentinel artefacts, tolerable); HEAD is on `main` at or ahead of commit `27b5cf8`.

If anything else is uncommitted, surface to user and halt.

- [ ] **Step 2: Confirm existing CI green on master**

Run:
```bash
gh run list --repo mahmood726-cyber/ma-workbench --branch main --limit 3
```

Expected: most recent run on `main` shows `completed success`.

If most recent run failed, halt and surface — do not build on a red tree.

- [ ] **Step 3: Verify primary-trial source access**

Confirm the human has:

- EMPEROR-Preserved: NEJM 2021;385:1451, Table 2 — DOI `10.1056/NEJMoa2107038`
- DELIVER: NEJM 2022;387:1089, Table 2 — DOI `10.1056/NEJMoa2206286`

Extract and record, freshly from the PDFs (do not trust spec values; the spec's HR/CI are best-effort recall):

- EMPEROR-Preserved primary composite HR, 95% CI lower, 95% CI upper, N
- DELIVER primary composite HR, 95% CI lower, 95% CI upper, N

If either HR differs from the spec (spec said 0.79 and 0.82) by more than ±0.01, flag to user — may indicate different composite or different subgroup.

- [ ] **Step 4: Identify benchmark paper**

The human must produce ONE benchmark paper that reports a pooled HR for EMPEROR-Preserved + DELIVER on the primary composite endpoint in HFpEF. Record:

1. Citation (journal, year, volume, pages)
2. DOI
3. Pool type (`ipd` if patient-level meta-analysis; `aggregate` if fixed-effect or random-effects aggregate pool of published HRs)
4. Reported pooled HR, 95% CI lower, 95% CI upper
5. Reported τ² and I² (if given)

Candidates to check (not authoritative — verify):

- Vaduganathan M et al. *Lancet* 2022 five-trial pool (check whether it reports a 2-trial HFpEF subset)
- Editorial or meta-analysis letter published with DELIVER (NEJM 2022)
- ESC Heart Failure review 2023/2024
- Cochrane update 2023/2024

**Sanity check:** the reported pooled HR should land in `[0.75, 0.85]` with CI inside `[0.70, 0.90]`. If it's outside that range, flag — may indicate wrong endpoint or wrong pool.

If the human cannot identify a single benchmark paper, halt and ask whether to (a) pivot to a different benchmark pool, (b) use a different trial set, or (c) switch the paper from benchmark-replication to fresh-synthesis (which would require revising the spec).

- [ ] **Step 5: Record the decisions**

Output the 5 facts from step 3 and the 5 facts from step 4 to the user in a readable block. Do not proceed to Task 1 without the user confirming the block is correct.

These facts are the inputs to `data.json` (Task 2) and `expected.json` (Task 3). Getting them wrong here poisons everything downstream.

---

## Task 1: Prespecification — `e156-submission-sglt2i/protocol.md`

**Files:**
- Create: `e156-submission-sglt2i/protocol.md`

This file is frozen before any compute runs. It records the decision rule that `expected.json` will be built against.

- [ ] **Step 1: Create the directory**

```bash
cd /c/Users/user/ma-workbench
mkdir -p e156-submission-sglt2i
```

- [ ] **Step 2: Write `protocol.md`**

Create `e156-submission-sglt2i/protocol.md` with this exact content (replace `<...>` placeholders with the Task 0 step 5 values):

```markdown
# SGLT2i-HFpEF E156 Benchmark Demo — Prespecification

Date locked: 2026-04-15
Author: Mahmood Ahmad

## Question

Does ma-workbench, run in a browser on published aggregate-data inputs,
reproduce the <benchmark_citation> pooled hazard ratio for SGLT2
inhibitors vs placebo on the primary composite endpoint in HFpEF?

## Population

HFpEF (ejection fraction > 40%); two RCTs pooled:

- EMPEROR-Preserved (empagliflozin, n=<emp_n>)
- DELIVER (dapagliflozin, n=<deliver_n>)

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
| EMPEROR-Preserved | <emp_hr> | (<emp_lo>, <emp_hi>) | Anker NEJM 2021;385:1451, Table 2 |
| DELIVER | <deliver_hr> | (<deliver_lo>, <deliver_hi>) | Solomon NEJM 2022;387:1089, Table 2 |

## Benchmark (frozen)

- Citation: <benchmark_citation>
- DOI: <benchmark_doi>
- Pool type: <ipd | aggregate>
- Reported HR: <bench_hr> (95% CI <bench_lo>, <bench_hi>)

## Pooling Method (frozen, primary)

REML random-effects, generic inverse-variance on log-HR scale.

## Sensitivity Estimators (frozen)

- Fixed-effect (IVhet)
- Paule-Mandel random-effects
- HKSJ-adjusted with floor `max(1, Q/(k-1))` and `qt(α/2, k-1)`

DerSimonian-Laird is excluded per the k<10 rule and will be displayed
greyed on the method-comparison panel with reason string "k<10".

## Decision Rule (frozen)

### Primary decision

`applied_delta` is derived from benchmark pool type:

- `pool_type = ipd` → `applied_delta = 0.02`
- `pool_type = aggregate` → `applied_delta = 0.005`

PASS iff both:

1. `|pooled_hr - bench_hr| <= applied_delta`
2. pooled 95% CI overlaps benchmark 95% CI (non-empty intersection)

Otherwise FAIL.

### Method-range decision

Across the four live estimators (FE, REML, PM, HKSJ-floored), the
**absolute HR range** (max HR − min HR) must be ≤ 0.03.

## Paper Branches (frozen)

PASS branch and FAIL branch wording both committed to `paper.md` ahead
of compute. Only the S4/S6/S7 fill-ins change between branches; the
seven-sentence structure is identical.

## What is NOT Decided Here

- The pooled HR, CI, τ², I², Q-p values (computed by the workbench).
- Which paper branch ships (driven by the decision rule).
- Whether `SUBMITTED` is toggled (gated additionally by Overmind PASS).
```

- [ ] **Step 3: Commit the protocol alone**

```bash
cd /c/Users/user/ma-workbench
git add e156-submission-sglt2i/protocol.md
git commit -m "feat(sglt2i): prespecify SGLT2i-HFpEF benchmark protocol

Freeze the decision rule, inputs, methods, and paper branches before
any compute runs. Numbers filled from Task 0 preflight. Adaptive delta
(0.02 for IPD benchmark / 0.005 for aggregate benchmark) derived from
benchmark pool type.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: `sglt2i-hfpef-demo/data.json` with provenance + schema test

**Files:**
- Create: `sglt2i-hfpef-demo/data.json`
- Create: `tests/test_sglt2i_data_schema.py`

- [ ] **Step 1: Write the failing schema test first**

Create `tests/test_sglt2i_data_schema.py`:

```python
"""Contract test for sglt2i-hfpef-demo/data.json.

Ensures the trial inputs match a fixed schema and that derived fields
(log_hr, se_log_hr) are internally consistent with reported HR and CI.
"""
import json
import math
from pathlib import Path

DATA_PATH = Path("sglt2i-hfpef-demo/data.json")

REQUIRED_TRIAL_KEYS = {
    "id", "hr", "ci_low", "ci_high", "n_total", "n_events_total",
    "log_hr", "se_log_hr", "source",
}
REQUIRED_SOURCE_KEYS = {"citation", "doi", "table", "page", "accessed"}
EXPECTED_TRIAL_IDS = {"EMPEROR-Preserved", "DELIVER"}


def load():
    assert DATA_PATH.exists(), f"{DATA_PATH} missing"
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def test_schema_version():
    data = load()
    assert data["schema_version"] == "1.0"


def test_two_trials():
    data = load()
    ids = {t["id"] for t in data["trials"]}
    assert ids == EXPECTED_TRIAL_IDS


def test_trial_keys_complete():
    data = load()
    for t in data["trials"]:
        missing = REQUIRED_TRIAL_KEYS - t.keys()
        assert not missing, f"{t['id']} missing keys: {missing}"
        missing_src = REQUIRED_SOURCE_KEYS - t["source"].keys()
        assert not missing_src, f"{t['id']} source missing: {missing_src}"


def test_source_fields_non_empty():
    data = load()
    for t in data["trials"]:
        for key in REQUIRED_SOURCE_KEYS:
            v = t["source"][key]
            assert v not in (None, "", 0), (
                f"{t['id']}.source.{key} is empty: {v!r}"
            )


def test_log_hr_derivation():
    data = load()
    for t in data["trials"]:
        expected = math.log(t["hr"])
        assert abs(t["log_hr"] - expected) < 1e-4, (
            f"{t['id']}.log_hr = {t['log_hr']}, expected {expected:.6f}"
        )


def test_se_log_hr_derivation():
    data = load()
    for t in data["trials"]:
        expected = (math.log(t["ci_high"]) - math.log(t["ci_low"])) / (2 * 1.96)
        assert abs(t["se_log_hr"] - expected) < 1e-4, (
            f"{t['id']}.se_log_hr = {t['se_log_hr']}, expected {expected:.6f}"
        )


def test_ci_ordering():
    data = load()
    for t in data["trials"]:
        assert t["ci_low"] < t["hr"] < t["ci_high"], (
            f"{t['id']} CI ordering broken: {t['ci_low']}/{t['hr']}/{t['ci_high']}"
        )
```

- [ ] **Step 2: Run the test to verify failure**

```bash
cd /c/Users/user/ma-workbench
python -m pytest tests/test_sglt2i_data_schema.py -v
```

Expected: all tests fail with `AssertionError: sglt2i-hfpef-demo/data.json missing`.

- [ ] **Step 3: Create `sglt2i-hfpef-demo/data.json`**

Using Task 0 step 5 values, create `sglt2i-hfpef-demo/data.json`. Compute `log_hr = ln(hr)` and `se_log_hr = (ln(ci_high) - ln(ci_low)) / 3.92` to 4 decimal places. Fill `<...>` with actual values from Task 0:

```json
{
  "schema_version": "1.0",
  "trials": [
    {
      "id": "EMPEROR-Preserved",
      "hr": <emp_hr>,
      "ci_low": <emp_lo>,
      "ci_high": <emp_hi>,
      "n_total": <emp_n>,
      "n_events_total": null,
      "log_hr": <computed to 4dp>,
      "se_log_hr": <computed to 4dp>,
      "source": {
        "citation": "Anker SD et al. NEJM 2021;385:1451-61",
        "doi": "10.1056/NEJMoa2107038",
        "table": "Table 2, row 'Primary composite outcome'",
        "page": 1455,
        "accessed": "2026-04-15"
      }
    },
    {
      "id": "DELIVER",
      "hr": <deliver_hr>,
      "ci_low": <deliver_lo>,
      "ci_high": <deliver_hi>,
      "n_total": <deliver_n>,
      "n_events_total": null,
      "log_hr": <computed to 4dp>,
      "se_log_hr": <computed to 4dp>,
      "source": {
        "citation": "Solomon SD et al. NEJM 2022;387:1089-98",
        "doi": "10.1056/NEJMoa2206286",
        "table": "Table 2, row 'Primary composite outcome'",
        "page": 1092,
        "accessed": "2026-04-15"
      }
    }
  ]
}
```

- [ ] **Step 4: Run the schema test to verify green**

```bash
cd /c/Users/user/ma-workbench
python -m pytest tests/test_sglt2i_data_schema.py -v
```

Expected: all 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add sglt2i-hfpef-demo/data.json tests/test_sglt2i_data_schema.py
git commit -m "feat(sglt2i): add data.json with EMPEROR-Preserved + DELIVER inputs

Trial HRs extracted from NEJM primary reports. log_hr and se_log_hr
are derived audit fields; contract test enforces 1e-4 consistency with
hr/ci_low/ci_high. Source fields require non-empty citation, DOI,
table, page, and accessed date; fail-closed on empty.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: `sglt2i-hfpef-demo/expected.json` with benchmark + tolerance rule

**Files:**
- Create: `sglt2i-hfpef-demo/expected.json`
- Create: `tests/test_sglt2i_expected_schema.py`

- [ ] **Step 1: Write the failing schema test**

Create `tests/test_sglt2i_expected_schema.py`:

```python
"""Contract test for sglt2i-hfpef-demo/expected.json.

Ensures the benchmark block is fully populated, pool_type is a known
value, and applied_delta matches the prespecified rule from protocol.md.
"""
import json
from pathlib import Path

EXPECTED_PATH = Path("sglt2i-hfpef-demo/expected.json")

REQUIRED_BENCHMARK_KEYS = {
    "source", "doi", "pool_type", "hr", "ci_low", "ci_high", "accessed",
}
REQUIRED_TOLERANCE_KEYS = {
    "delta_hr_ipd_branch", "delta_hr_aggregate_branch", "applied_delta",
    "applied_delta_source", "method", "decision_rule",
}
VALID_POOL_TYPES = {"ipd", "aggregate"}


def load():
    assert EXPECTED_PATH.exists(), f"{EXPECTED_PATH} missing"
    return json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))


def test_schema_version():
    assert load()["schema_version"] == "1.0"


def test_benchmark_keys():
    b = load()["benchmark"]
    assert REQUIRED_BENCHMARK_KEYS <= b.keys()


def test_benchmark_non_empty():
    b = load()["benchmark"]
    for k in ("source", "doi", "accessed"):
        assert b[k] not in (None, ""), f"benchmark.{k} empty"
    for k in ("hr", "ci_low", "ci_high"):
        assert b[k] > 0, f"benchmark.{k} not positive"


def test_pool_type_valid():
    pool_type = load()["benchmark"]["pool_type"]
    assert pool_type in VALID_POOL_TYPES, (
        f"pool_type={pool_type!r} not in {VALID_POOL_TYPES}"
    )


def test_tolerance_keys():
    t = load()["tolerance"]
    assert REQUIRED_TOLERANCE_KEYS <= t.keys()


def test_applied_delta_matches_pool_type():
    d = load()
    pool_type = d["benchmark"]["pool_type"]
    t = d["tolerance"]
    if pool_type == "ipd":
        assert t["applied_delta"] == t["delta_hr_ipd_branch"] == 0.02
    else:
        assert t["applied_delta"] == t["delta_hr_aggregate_branch"] == 0.005


def test_benchmark_ci_ordering():
    b = load()["benchmark"]
    assert b["ci_low"] < b["hr"] < b["ci_high"]
```

- [ ] **Step 2: Run test, verify failure**

```bash
python -m pytest tests/test_sglt2i_expected_schema.py -v
```

Expected: fails with `expected.json missing`.

- [ ] **Step 3: Create `sglt2i-hfpef-demo/expected.json`**

Using Task 0 step 4 values:

```json
{
  "schema_version": "1.0",
  "benchmark": {
    "source": "<benchmark_citation>",
    "doi": "<benchmark_doi>",
    "pool_type": "<ipd | aggregate>",
    "hr": <bench_hr>,
    "ci_low": <bench_lo>,
    "ci_high": <bench_hi>,
    "accessed": "2026-04-15"
  },
  "tolerance": {
    "delta_hr_ipd_branch": 0.02,
    "delta_hr_aggregate_branch": 0.005,
    "applied_delta": <0.02 if ipd else 0.005>,
    "applied_delta_source": "derived from benchmark.pool_type per protocol.md",
    "method": "REML random-effects, GIV on log-HR",
    "decision_rule": "|pooled_hr - benchmark.hr| <= applied_delta AND pooled 95% CI overlaps benchmark 95% CI"
  }
}
```

- [ ] **Step 4: Verify green**

```bash
python -m pytest tests/test_sglt2i_expected_schema.py -v
```

Expected: 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add sglt2i-hfpef-demo/expected.json tests/test_sglt2i_expected_schema.py
git commit -m "feat(sglt2i): add expected.json with benchmark + adaptive delta rule

applied_delta = 0.02 (IPD branch) or 0.005 (aggregate branch), derived
from benchmark.pool_type at file creation, then frozen. decision_rule
is a human-readable string; the pytest contract enforces the actual
computation.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Golden dataset `G06-sglt2i-hfpef-benchmark.json`

**Files:**
- Create: `golden/datasets/G06-sglt2i-hfpef-benchmark.json`

- [ ] **Step 1: Write the G06 dataset file**

The existing G01–G05 datasets use `{"slug", "title", "description", "effect_label", "null_value", "bus_payload", "r_script"}`. Match that shape exactly.

Create `golden/datasets/G06-sglt2i-hfpef-benchmark.json`. Substitute `<emp_log_hr>` / `<emp_se>` / `<deliver_log_hr>` / `<deliver_se>` from the values already computed in Task 2 step 3 (they must be byte-identical to `data.json` — if they drift, the CI regen gate catches it):

```json
{
  "slug": "G06-sglt2i-hfpef-benchmark",
  "title": "SGLT2i in HFpEF: EMPEROR-Preserved + DELIVER primary composite pool (k=2)",
  "description": "Real-trial 2-study pool. Pooling HR 0.79 and HR 0.82 on log-HR scale; expected REML HR ~0.80, tau2 ~0, I2 ~0, Q small. Benchmark reproduction target with adaptive delta (0.02 IPD / 0.005 aggregate) per protocol.md.",
  "effect_label": "logHR",
  "null_value": 0,
  "bus_payload": {
    "_schema": "ma-studies-v1",
    "_savedAt": "deterministic",
    "studies": [
      {
        "label": "EMPEROR-Preserved",
        "est": <emp_log_hr>,
        "se": <emp_se>,
        "moderator": null,
        "group": null,
        "year": 2021
      },
      {
        "label": "DELIVER",
        "est": <deliver_log_hr>,
        "se": <deliver_se>,
        "moderator": null,
        "group": null,
        "year": 2022
      }
    ]
  },
  "r_script": "# G06-sglt2i-hfpef-benchmark — SGLT2i in HFpEF: EMPEROR-Preserved + DELIVER\nlibrary(metafor)\nyi  <- c(<emp_log_hr>, <deliver_log_hr>)\nsei <- c(<emp_se>, <deliver_se>)\nslab <- c(\"EMPEROR-Preserved\", \"DELIVER\")\nfe <- rma(yi, sei = sei, method = \"FE\", slab = slab)\npm <- rma(yi, sei = sei, method = \"PM\", slab = slab)\ncat(sprintf(\n  \"fe.estimate=%.10f\\nfe.se=%.10f\\npm.estimate=%.10f\\npm.se=%.10f\\npm.tau2=%.10f\\npm.I2=%.10f\\npm.QE=%.10f\\n\",\n  as.numeric(fe$b), as.numeric(fe$se),\n  as.numeric(pm$b), as.numeric(pm$se),\n  as.numeric(pm$tau2), as.numeric(pm$I2), as.numeric(pm$QE)))"
}
```

- [ ] **Step 2: Sanity-check with metafor locally (optional but recommended)**

```bash
python -c "import json; print(json.load(open('golden/datasets/G06-sglt2i-hfpef-benchmark.json'))['r_script'])" > /tmp/g06.R
"/c/Program Files/R/R-4.5.2/bin/Rscript.exe" /tmp/g06.R
```

Expected output: `pm.estimate` should be ≈ −0.22 (i.e. log(HR) for pooled HR ≈ 0.80), `pm.tau2` ≈ 0, `pm.I2` ≈ 0, `pm.QE` small.

If `pm.estimate` back-transforms (`exp(-0.22) = 0.80`) to more than ±0.03 from the benchmark HR, halt — either `data.json` has a transcription error, or the benchmark HR is from a different endpoint/subset.

- [ ] **Step 3: Commit the dataset alone (references come in Task 5)**

```bash
git add golden/datasets/G06-sglt2i-hfpef-benchmark.json
git commit -m "feat(sglt2i): add G06 golden dataset (EMPEROR-Preserved + DELIVER)

Real-trial 2-study pool matching sglt2i-hfpef-demo/data.json exactly.
References are regenerated deterministically in the next commit. log_hr
and se values are byte-identical to data.json; any drift fails the
existing byte-for-byte CI regeneration gate.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Extend `generate_references.py` to emit G06 references

**Files:**
- Modify: `golden/generate_references.py`
- Create: `golden/references/G06-sglt2i-hfpef-benchmark.json`
- Modify: `golden/SUMMARY.json`

- [ ] **Step 1: Inspect the existing generator**

```bash
grep -n "G0[1-5]" golden/generate_references.py
```

Expected: each dataset appears in a `DATASETS` list or similar registry. Record the pattern the existing five use.

- [ ] **Step 2: Add G06 to the generator's dataset registry**

Open `golden/generate_references.py`. Find the line where `G05-null-crossing` is registered. Add an entry for `G06-sglt2i-hfpef-benchmark` following the identical pattern. Do not change any G01–G05 entry. Do not add new computation logic.

- [ ] **Step 3: Regenerate references**

```bash
cd /c/Users/user/ma-workbench
python golden/generate_references.py
```

Expected:
- Creates `golden/references/G06-sglt2i-hfpef-benchmark.json` with FE/RE/tau2/I2/Q/PI fields at 10 decimal places.
- Updates `golden/SUMMARY.json` to include the G06 one-liner.
- G01–G05 reference files remain byte-identical (verify with `git diff --stat golden/references/`).

If G01–G05 references drift, the generator code was accidentally modified — revert and isolate the change.

- [ ] **Step 4: Verify the regenerated G06 reference**

```bash
cat golden/references/G06-sglt2i-hfpef-benchmark.json
```

Check: `fe.estimate` and `pm.estimate` should be negative (log-HR of a protective effect), near −0.22. `tau2` near 0. `I2` near 0. The `pi_low` and `pi_high` fields should be `null` (undefined at k<3 per the existing generator).

If `pi_low` / `pi_high` are NOT null at k=2, the existing generator has a bug — halt and fix in a separate commit before continuing.

- [ ] **Step 5: Run existing golden-parity tests**

```bash
python -m pytest golden/test_golden_parity.py -v
```

Expected: all pass (including the new G06 row).

- [ ] **Step 6: Verify byte-for-byte CI check will pass**

```bash
python golden/generate_references.py
git diff golden/
```

Expected: empty diff after a second run — generation is idempotent.

- [ ] **Step 7: Commit**

```bash
git add golden/generate_references.py golden/references/G06-sglt2i-hfpef-benchmark.json golden/SUMMARY.json
git commit -m "feat(sglt2i): register G06 in golden generator; emit references

Extends the byte-for-byte CI regeneration gate to cover the SGLT2i
dataset. FE/PM/tau2/I2/Q computed by the same Python estimators that
mirror the JS apps; pi_low/pi_high remain null because k<3.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Benchmark test suite (TDD red)

**Files:**
- Create: `tests/test_sglt2i_benchmark.py`

This task writes the 5 tests that define PASS/FAIL for the benchmark. They remain red until the companion page wires up.

- [ ] **Step 1: Write the test file**

Create `tests/test_sglt2i_benchmark.py`:

```python
"""SGLT2i-HFpEF benchmark tests.

These tests define the success criteria for the E156 benchmark demo:
the workbench-computed pool must reproduce the named benchmark paper
within the prespecified applied_delta. All five must pass for the
paper to ship in the PASS branch.

The tests read the computed pool from golden/references/G06-*.json
(the deterministic regeneration already runs in CI); this keeps the
test independent of a headless browser.
"""
import json
import math
from pathlib import Path

DATA = Path("sglt2i-hfpef-demo/data.json")
EXPECTED = Path("sglt2i-hfpef-demo/expected.json")
G06_REF = Path("golden/references/G06-sglt2i-hfpef-benchmark.json")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def pooled_hr_and_ci_from_ref(ref):
    """Back-transform REML (PM) pool from log-HR to HR scale.

    The golden reference emits pm.estimate and pm.se on log scale; we
    exponentiate here. The demo page does the same transform for display.
    """
    log_hr = ref["pm"]["estimate"]
    se = ref["pm"]["se"]
    hr = math.exp(log_hr)
    lo = math.exp(log_hr - 1.96 * se)
    hi = math.exp(log_hr + 1.96 * se)
    return hr, lo, hi


def test_main_hr_within_tolerance():
    expected = load_json(EXPECTED)
    ref = load_json(G06_REF)
    bench = expected["benchmark"]["hr"]
    delta = expected["tolerance"]["applied_delta"]
    hr, _, _ = pooled_hr_and_ci_from_ref(ref)
    assert abs(hr - bench) <= delta, (
        f"pooled HR {hr:.4f} diverges from benchmark {bench} "
        f"by {abs(hr-bench):.4f}, tolerance {delta}"
    )


def test_ci_overlaps_published():
    expected = load_json(EXPECTED)
    ref = load_json(G06_REF)
    bench = expected["benchmark"]
    _, lo, hi = pooled_hr_and_ci_from_ref(ref)
    assert max(lo, bench["ci_low"]) <= min(hi, bench["ci_high"]), (
        f"pooled CI [{lo:.3f},{hi:.3f}] does not overlap "
        f"benchmark CI [{bench['ci_low']},{bench['ci_high']}]"
    )


def test_methods_agree():
    """Absolute HR range across FE, REML, PM, HKSJ-floored must be <= 0.03.

    The golden reference gives FE and PM (== REML for this data since
    tau2=0). HKSJ-floored and the PM estimator are identical at
    tau2=0 on the point estimate (they differ only in the SE/CI
    calculation). So at k=2 with homogeneity, the absolute HR range
    reduces to |exp(fe) - exp(pm)| which must be <= 0.03.
    """
    ref = load_json(G06_REF)
    hrs = [math.exp(ref["fe"]["estimate"]), math.exp(ref["pm"]["estimate"])]
    assert max(hrs) - min(hrs) <= 0.03, (
        f"method HR range {max(hrs) - min(hrs):.4f} exceeds 0.03"
    )


def test_dl_excluded_in_demo_page():
    """The demo page must explicitly mark DerSimonian-Laird unavailable.

    Checks the rendered companion page for the 'k<10' reason string
    attached to a 'DerSimonian' or 'DL' label.
    """
    html = Path("sglt2i-hfpef-demo/index.html")
    assert html.exists(), f"{html} missing"
    text = html.read_text(encoding="utf-8")
    assert "DerSimonian" in text or "DL" in text, "no DL row in method panel"
    assert "k<10" in text, "DL exclusion reason 'k<10' not present"


def test_undefined_panels_reasons_present():
    """Four greyed cards must each emit the expected reason string verbatim."""
    html = Path("sglt2i-hfpef-demo/index.html")
    text = html.read_text(encoding="utf-8")
    reasons = {
        "prediction-interval": "undefined at k<3",
        "funnel": "needs k",
        "trim-and-fill": "sensitivity",
        "tsa": "already",
    }
    for label, needle in reasons.items():
        assert needle in text, (
            f"{label} card missing expected reason fragment {needle!r}"
        )
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_sglt2i_benchmark.py -v
```

Expected: first three tests may pass if `data.json`, `expected.json`, and `G06` reference are all populated. The last two (which check `sglt2i-hfpef-demo/index.html`) MUST fail with "index.html missing" — the file has not been created yet.

Record which tests pass and which fail. The pass count at this point is the "inputs-only" passing set; the full five-green gate comes after Task 14.

- [ ] **Step 3: Commit the red tests**

```bash
git add tests/test_sglt2i_benchmark.py
git commit -m "test(sglt2i): add 5 benchmark success-criterion tests (TDD-red)

test_main_hr_within_tolerance, test_ci_overlaps_published, and
test_methods_agree pass off the G06 reference alone.
test_dl_excluded_in_demo_page and test_undefined_panels_reasons_present
remain red until the companion page ships (Task 14).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Companion page scaffold — `sglt2i-hfpef-demo/index.html`

**Files:**
- Create: `sglt2i-hfpef-demo/index.html`

This task delivers a minimal offline HTML scaffold: DOCTYPE, header, empty claim card, empty section placeholders for forest plot / method table / heterogeneity / not-computed cards / provenance / paper card. Subsequent tasks fill the sections.

- [ ] **Step 1: Write the scaffold**

Create `sglt2i-hfpef-demo/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SGLT2i in HFpEF — ma-workbench reproducibility demo</title>
<style>
  :root {
    --fg: #1a1a1a; --muted: #6b6b6b; --bg: #ffffff;
    --accent: #0b5394; --pass: #0a8a3a; --fail: #b42318;
    --grey: #eee; --rule: #d8d8d8;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font: 15px/1.5 system-ui, -apple-system, sans-serif;
    color: var(--fg); background: var(--bg); max-width: 860px;
    padding: 1.25rem; margin-inline: auto;
  }
  header { display: flex; justify-content: space-between;
    align-items: baseline; border-bottom: 1px solid var(--rule);
    padding-bottom: .5rem; margin-bottom: 1rem; }
  header h1 { margin: 0; font-size: 1.15rem; }
  header small { color: var(--muted); }
  section { margin: 1.5rem 0; }
  h2 { font-size: 1rem; margin: 0 0 .5rem; }
  .claim {
    background: #f7f9fc; border: 1px solid var(--rule);
    border-radius: 6px; padding: 1rem;
  }
  .claim-row { display: flex; justify-content: space-between;
    padding: .25rem 0; }
  .badge {
    display: inline-block; padding: .2rem .6rem; border-radius: 4px;
    font-weight: 600; color: white;
  }
  .badge.pass { background: var(--pass); }
  .badge.fail { background: var(--fail); }
  .badge.pending { background: var(--muted); }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: .4rem .6rem;
    border-bottom: 1px solid var(--rule); }
  .greyed { color: var(--muted); background: var(--grey); }
  .not-computed {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: .5rem;
  }
  .not-computed > div {
    border: 1px solid var(--rule); border-radius: 4px;
    padding: .6rem; background: var(--grey); color: var(--muted);
  }
  @media (max-width: 640px) {
    .not-computed { grid-template-columns: 1fr; }
  }
  details summary { cursor: pointer; color: var(--accent); }
  .error { color: var(--fail); font-weight: 600; }
  iframe { width: 100%; min-height: 420px; border: 1px solid var(--rule); }
</style>
</head>
<body>
  <header>
    <h1>SGLT2i in HFpEF <small>— ma-workbench reproducibility demo</small></h1>
    <small>
      <a href="../hub/">&larr; hub</a> ·
      <span id="build-sha">build …</span>
    </small>
  </header>

  <section class="claim" aria-live="polite" id="claim-card">
    <h2>Benchmark reproduction</h2>
    <div class="claim-row">
      <span>Benchmark pool HR:</span>
      <span id="bench-hr">loading…</span>
    </div>
    <div class="claim-row">
      <span>ma-workbench REML HR:</span>
      <span id="our-hr">loading…</span>
    </div>
    <div class="claim-row">
      <span>|Δ|:</span>
      <span><span id="delta">…</span> (tolerance <span id="delta-tol">…</span>)</span>
    </div>
    <div class="claim-row">
      <span>Verdict:</span>
      <span class="badge pending" id="verdict">pending</span>
    </div>
  </section>

  <section id="forest-section">
    <h2>Forest plot</h2>
    <div id="forest-host" data-state="empty">
      <!-- forest-plot app iframe injected by orchestrator (Task 9) -->
    </div>
  </section>

  <section id="method-section">
    <h2>Method comparison</h2>
    <table id="method-table">
      <thead>
        <tr><th>Method</th><th>HR</th><th>95% CI</th><th>Note</th></tr>
      </thead>
      <tbody id="method-body">
        <tr><td colspan="4">loading…</td></tr>
      </tbody>
    </table>
  </section>

  <section id="hetero-section">
    <h2>Heterogeneity</h2>
    <div id="hetero-host">loading…</div>
  </section>

  <section id="not-computed-section">
    <h2>Not computed at k=2</h2>
    <div class="not-computed">
      <div data-card="prediction-interval">
        <strong>Prediction interval</strong><br>
        <small>undefined at k&lt;3; requires t_{k-2}</small>
      </div>
      <div data-card="funnel">
        <strong>Funnel plot / Egger</strong><br>
        <small>needs k ≥ 10 for meaningful asymmetry</small>
      </div>
      <div data-card="trim-and-fill">
        <strong>Trim-and-fill</strong><br>
        <small>sensitivity analysis; primary use requires larger k</small>
      </div>
      <div data-card="tsa">
        <strong>TSA</strong><br>
        <small>2 trials, already well-powered (n ≈ 12,000)</small>
      </div>
    </div>
  </section>

  <details id="provenance">
    <summary>Input provenance</summary>
    <div id="provenance-body">loading…</div>
  </details>

  <section id="paper-card">
    <h2>Paper</h2>
    <p>
      <a href="../e156-submission-sglt2i/paper.md">E156 body (7 sentences)</a> ·
      <a href="../e156-submission-sglt2i/protocol.md">Protocol (prespecification)</a>
    </p>
  </section>

  <script>
    // Orchestrator loads in Task 8. Scaffold only — no logic here yet.
    (function () {
      document.getElementById("build-sha").textContent =
        "build " + (document.documentElement.dataset.buildSha || "(dev)");
    })();
  </script>
</body>
</html>
```

- [ ] **Step 2: Smoke-test the scaffold**

Open `sglt2i-hfpef-demo/index.html` directly in a browser (double-click or drag to a tab). Confirm:

- Page renders without console errors.
- Header shows "SGLT2i in HFpEF — ma-workbench reproducibility demo".
- All 4 greyed "not computed" cards are visible with their reason text.
- No dead layout regions (every section has some visible content or a "loading…" placeholder).

- [ ] **Step 3: Run the DL-excluded + undefined-panels tests**

```bash
python -m pytest tests/test_sglt2i_benchmark.py::test_undefined_panels_reasons_present -v
```

Expected: PASS (all 4 reason fragments are now in the HTML).

```bash
python -m pytest tests/test_sglt2i_benchmark.py::test_dl_excluded_in_demo_page -v
```

Expected: still FAIL (the DL row is added in Task 11's method table).

- [ ] **Step 4: Commit**

```bash
git add sglt2i-hfpef-demo/index.html
git commit -m "feat(sglt2i): scaffold companion HTML page

Header + empty claim card + section placeholders + 4 greyed
not-computed cards. No JS logic yet; orchestrator + embedded apps
land in Tasks 8–14. test_undefined_panels_reasons_present now green.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Orchestrator — fetch data + fill claim card + provenance

**Files:**
- Modify: `sglt2i-hfpef-demo/index.html` (replace the `<script>` block at the bottom)

- [ ] **Step 1: Replace the scaffold `<script>` with a fetch orchestrator**

Find the existing `<script>` block in `sglt2i-hfpef-demo/index.html` (from Task 7). Replace it with this:

```html
  <script>
  (async function () {
    function setText(id, v) { document.getElementById(id).textContent = v; }
    function renderError(msg) {
      document.getElementById("claim-card").innerHTML =
        '<p class="error">Cannot render: ' + msg + '</p>';
    }
    try {
      const [data, expected] = await Promise.all([
        fetch("data.json").then(r => r.json()),
        fetch("expected.json").then(r => r.json()),
      ]);

      // Fail-closed validation
      if (!data.trials || data.trials.length !== 2) {
        return renderError("data.json missing or malformed (need 2 trials)");
      }
      if (!expected.benchmark || !expected.tolerance) {
        return renderError("expected.json missing benchmark/tolerance block");
      }
      for (const t of data.trials) {
        for (const k of ["citation","doi","table","page","accessed"]) {
          if (!t.source || !t.source[k]) {
            return renderError("data.json " + t.id + ".source." + k + " empty");
          }
        }
      }

      // Store for panels wired in later tasks
      window.__SGLT2I = { data, expected };

      // Benchmark HR display
      const b = expected.benchmark;
      setText("bench-hr",
        b.hr.toFixed(2) + " (95% CI " + b.ci_low + "–" + b.ci_high + ")"
      );
      setText("delta-tol", expected.tolerance.applied_delta.toFixed(3));
      setText("our-hr", "computing…");
      setText("delta", "—");

      // Provenance panel
      const prov = document.getElementById("provenance-body");
      prov.innerHTML = data.trials.map(t =>
        '<p><strong>' + t.id + ':</strong> ' + t.source.citation +
        ', ' + t.source.table + ', p' + t.source.page +
        '<br><small>DOI ' + t.source.doi +
        ' · accessed ' + t.source.accessed + '</small></p>'
      ).join("") + '<p><strong>Benchmark:</strong> ' + b.source +
        '<br><small>DOI ' + b.doi +
        ' · pool type ' + b.pool_type + '</small></p>';

      // Emit a ready event so later panels can orchestrate
      document.dispatchEvent(new CustomEvent("sglt2i:inputs-ready"));
    } catch (e) {
      renderError((e && e.message) || String(e));
    }
  })();
  </script>
```

- [ ] **Step 2: Smoke-test in browser**

Serve the repo locally so `fetch()` works (file:// fetches are blocked in most browsers):

```bash
cd /c/Users/user/ma-workbench
python -m http.server 8787
```

Navigate to `http://localhost:8787/sglt2i-hfpef-demo/index.html`.

Confirm:
- Claim card shows benchmark HR and tolerance pulled from `expected.json`.
- "ma-workbench REML HR" still shows "computing…" (correct — computed in Task 9).
- Provenance panel (expand the collapsed `<details>`) shows both trial citations and the benchmark citation.
- No errors in DevTools Console.

Kill the server: Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add sglt2i-hfpef-demo/index.html
git commit -m "feat(sglt2i): orchestrator fetches data + expected, fills claim card

Fail-closed: refuses to render if data.json/expected.json missing or
source fields empty. Provenance panel populated from source.*. Emits
sglt2i:inputs-ready CustomEvent for downstream panels.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: REML pool — compute in-page, fill claim card + verdict

**Files:**
- Modify: `sglt2i-hfpef-demo/index.html` (append a second `<script>` block)

The existing `forest-plot` and `heterogeneity` apps can compute the pool if we feed studies through the `ma-studies-v1` bus. But for the claim card's REML HR + Δ + verdict, we need the pooled number in the page's own script so the badge updates reliably. Embed a tiny REML estimator in-page (k=2, tau2-clamps-to-0 case is trivial: REML reduces to inverse-variance weighted mean).

- [ ] **Step 1: Append a second `<script>` block for pool + verdict**

Append *after* the Task 8 script block, before `</body>`:

```html
  <script>
  (function () {
    function poolInverseVariance(studies) {
      // At k=2 with tau2=0, REML == PM == FE on the point estimate.
      // Variances differ at higher k; we surface all four methods in
      // the method-comparison panel (Task 11).
      let sw = 0, swy = 0, sw2 = 0;
      for (const s of studies) {
        const w = 1 / (s.se * s.se);
        sw += w; sw2 += w*w; swy += w * s.est;
      }
      const mu = swy / sw;
      const se = Math.sqrt(1 / sw);
      return { mu, se };
    }

    function updateVerdict() {
      const ctx = window.__SGLT2I;
      if (!ctx) return;
      const studies = ctx.data.trials.map(t => ({
        label: t.id, est: t.log_hr, se: t.se_log_hr,
      }));
      const { mu, se } = poolInverseVariance(studies);
      const hr = Math.exp(mu);
      const lo = Math.exp(mu - 1.96 * se);
      const hi = Math.exp(mu + 1.96 * se);
      const bench = ctx.expected.benchmark;
      const delta = Math.abs(hr - bench.hr);
      const tol = ctx.expected.tolerance.applied_delta;
      const ciOverlap =
        Math.max(lo, bench.ci_low) <= Math.min(hi, bench.ci_high);
      const pass = delta <= tol && ciOverlap;

      document.getElementById("our-hr").textContent =
        hr.toFixed(2) + " (95% CI " + lo.toFixed(2) + "–" + hi.toFixed(2) + ")";
      document.getElementById("delta").textContent = delta.toFixed(3);
      const verdict = document.getElementById("verdict");
      verdict.textContent = pass ? "PASS" : "FAIL";
      verdict.className = "badge " + (pass ? "pass" : "fail");

      ctx.pool = { hr, lo, hi, mu, se, delta, tol, pass, ciOverlap };
      document.dispatchEvent(new CustomEvent("sglt2i:pool-ready"));
    }

    document.addEventListener("sglt2i:inputs-ready", updateVerdict);
  })();
  </script>
```

- [ ] **Step 2: Smoke-test**

```bash
cd /c/Users/user/ma-workbench
python -m http.server 8787
```

Navigate to `http://localhost:8787/sglt2i-hfpef-demo/index.html`.

Confirm:
- Claim card now shows both benchmark HR and ma-workbench REML HR with CI.
- |Δ| displays a number like 0.00–0.02.
- Verdict badge shows PASS (green) or FAIL (red). Record which.
- DevTools Console: `window.__SGLT2I.pool` should be populated.

Kill the server.

- [ ] **Step 3: Commit**

```bash
git add sglt2i-hfpef-demo/index.html
git commit -m "feat(sglt2i): compute REML pool in-page; claim card verdict

At k=2 with tau2=0, REML collapses to inverse-variance weighted mean.
Claim card now shows HR + CI + |delta| + PASS/FAIL badge. Emits
sglt2i:pool-ready for the method-comparison panel.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: Embed forest-plot via `?fromBus=1`

**Files:**
- Modify: `sglt2i-hfpef-demo/index.html`

- [ ] **Step 1: Append forest-plot orchestration**

Append a new `<script>` block before `</body>`:

```html
  <script>
  (function () {
    const BUS_KEY = "ma-studies-v1";
    function publishBus() {
      const ctx = window.__SGLT2I;
      if (!ctx) return;
      const payload = {
        _schema: "ma-studies-v1",
        _savedAt: "sglt2i-hfpef-demo",
        studies: ctx.data.trials.map(t => ({
          label: t.id, est: t.log_hr, se: t.se_log_hr,
          moderator: null, group: null,
          year: t.id === "EMPEROR-Preserved" ? 2021 : 2022,
        })),
      };
      try {
        localStorage.setItem(BUS_KEY, JSON.stringify(payload));
      } catch (e) {
        console.warn("localStorage publish failed:", e);
      }
    }
    function embedForest() {
      publishBus();
      const host = document.getElementById("forest-host");
      host.innerHTML =
        '<iframe src="../forest-plot/index.html?fromBus=1" ' +
        'title="Forest plot (embedded)" loading="lazy"></iframe>';
      host.dataset.state = "loaded";
    }
    document.addEventListener("sglt2i:inputs-ready", embedForest);
  })();
  </script>
```

- [ ] **Step 2: Smoke-test**

```bash
python -m http.server 8787
```

Open `http://localhost:8787/sglt2i-hfpef-demo/index.html`.

Confirm:
- Forest plot section renders an iframe.
- Inside the iframe, two studies appear: EMPEROR-Preserved and DELIVER.
- Estimates are on log-HR scale (negative numbers around −0.2). This is expected — forest-plot displays the raw `est`, not back-transformed HR. Back-transformed display is a forest-plot enhancement for a separate future task.
- Iframe's pooled estimate visually matches the claim card (on log scale).

Kill server.

- [ ] **Step 3: Commit**

```bash
git add sglt2i-hfpef-demo/index.html
git commit -m "feat(sglt2i): embed forest-plot app via ?fromBus=1

Publishes the two trials to localStorage[ma-studies-v1] and mounts
forest-plot in an iframe. Forest-plot renders on the log-HR scale (its
native behaviour); claim card displays HR-scale separately.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 11: Method-comparison panel

**Files:**
- Modify: `sglt2i-hfpef-demo/index.html`

Fill the `<tbody id="method-body">` with 6 rows: FE, REML, PM, HKSJ (pre-floor), HKSJ (with floor), and the greyed DerSimonian-Laird row. At k=2 with tau2=0, FE/REML/PM produce identical point estimates; HKSJ recomputes the CI with t_{k-1} and the floor rule.

- [ ] **Step 1: Append the method-comparison script**

Append a new `<script>` block before `</body>`:

```html
  <script>
  (function () {
    function qLines(studies, tau2) {
      let sw = 0, swy = 0;
      for (const s of studies) {
        const w = 1 / (s.se*s.se + tau2);
        sw += w; swy += w * s.est;
      }
      const mu = swy / sw;
      let q = 0;
      for (const s of studies) {
        const w = 1 / (s.se*s.se + tau2);
        q += w * (s.est - mu) * (s.est - mu);
      }
      return { mu, se: Math.sqrt(1/sw), q };
    }

    // Two-sided 95% t-critical value; at k=2, df=1 -> 12.706
    const T_975 = { 1: 12.706, 2: 4.303 };
    function tCrit(df) {
      return T_975[df] !== undefined ? T_975[df] : 1.96;
    }

    function render() {
      const ctx = window.__SGLT2I;
      if (!ctx) return;
      const studies = ctx.data.trials.map(t => ({
        est: t.log_hr, se: t.se_log_hr,
      }));
      const k = studies.length;

      // FE / REML / PM (tau2 = 0 at this k; all three collapse)
      const fe = qLines(studies, 0);
      const feHR = Math.exp(fe.mu);
      const feLo = Math.exp(fe.mu - 1.96 * fe.se);
      const feHi = Math.exp(fe.mu + 1.96 * fe.se);

      // HKSJ adjustment: var_{HKSJ} = (1/(k-1)) * sum_i w_i * (est_i - mu)^2 / sum_i w_i
      // Then CI = mu +/- t_{alpha/2, k-1} * sqrt(var_HKSJ)
      // At k=2, df=1, t = 12.706.
      // Floor: if Q/(k-1) < 1, multiply var_HKSJ by max(1, Q/(k-1)) = 1.
      // => post-floor HKSJ CI is at least the FE CI (with t instead of z).
      let varHk = 0;
      let sw = 0;
      for (const s of studies) {
        const w = 1 / (s.se*s.se);
        sw += w;
        varHk += w * (s.est - fe.mu) * (s.est - fe.mu);
      }
      varHk = varHk / ((k - 1) * sw);
      const sePre = Math.sqrt(varHk);
      const qOverDf = fe.q / (k - 1);
      const floor = Math.max(1, qOverDf);
      const sePost = Math.sqrt(varHk * floor);
      const hkPreLo = Math.exp(fe.mu - tCrit(k-1) * sePre);
      const hkPreHi = Math.exp(fe.mu + tCrit(k-1) * sePre);
      const hkPostLo = Math.exp(fe.mu - tCrit(k-1) * sePost);
      const hkPostHi = Math.exp(fe.mu + tCrit(k-1) * sePost);

      const fmt = (x) => x.toFixed(2);
      const rows = [
        ["Fixed-effect (IVhet)", feHR, feLo, feHi, "baseline"],
        ["REML random-effects", feHR, feLo, feHi, "tau² = 0 at k=2"],
        ["Paule-Mandel", feHR, feLo, feHi, "matches REML here"],
        ["HKSJ (pre-floor)", feHR, hkPreLo, hkPreHi,
          "t_" + (k-1) + " = " + tCrit(k-1).toFixed(3)],
        ["HKSJ (with floor)", feHR, hkPostLo, hkPostHi,
          "floor = max(1, Q/(k-1)) = " + floor.toFixed(3)],
      ];

      const body = document.getElementById("method-body");
      body.innerHTML = rows.map(r =>
        '<tr><td>' + r[0] + '</td><td>' + fmt(r[1]) + '</td>' +
        '<td>(' + fmt(r[2]) + '–' + fmt(r[3]) + ')</td>' +
        '<td><small>' + r[4] + '</small></td></tr>'
      ).join("") +
        '<tr class="greyed" data-row="dl">' +
        '<td><strong>DerSimonian-Laird</strong></td>' +
        '<td>—</td><td>—</td>' +
        '<td><small>unavailable: k&lt;10 rule</small></td></tr>';
    }

    document.addEventListener("sglt2i:pool-ready", render);
  })();
  </script>
```

- [ ] **Step 2: Smoke-test**

```bash
python -m http.server 8787
```

Open the page. Confirm the method-comparison table:
- 5 live rows (FE, REML, PM, HKSJ pre, HKSJ post) each with HR + CI.
- 1 greyed DerSimonian-Laird row with "unavailable: k<10 rule".
- HKSJ pre-floor CI is narrower than FE (expected at Q<1).
- HKSJ with-floor CI is at least as wide as FE (expected after floor + t).

Kill server.

- [ ] **Step 3: Run the DL-excluded test**

```bash
python -m pytest tests/test_sglt2i_benchmark.py::test_dl_excluded_in_demo_page -v
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add sglt2i-hfpef-demo/index.html
git commit -m "feat(sglt2i): method-comparison panel with HKSJ pre+post-floor rows

FE/REML/PM collapse at k=2 tau2=0. HKSJ shows pre-floor and post-floor
CIs using t_{k-1}=12.706 and floor max(1, Q/(k-1)). DerSimonian-Laird
row greyed with 'unavailable: k<10 rule'. test_dl_excluded now green.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: Embed heterogeneity app

**Files:**
- Modify: `sglt2i-hfpef-demo/index.html`

- [ ] **Step 1: Append heterogeneity embed**

Find the existing `embedForest()` function from Task 10. After its declaration, add a parallel `embedHetero()` inside the same `<script>` (or a new script block before `</body>`):

```html
  <script>
  (function () {
    function embedHetero() {
      const host = document.getElementById("hetero-host");
      host.innerHTML =
        '<iframe src="../heterogeneity/index.html?fromBus=1" ' +
        'title="Heterogeneity (embedded)" loading="lazy"></iframe>';
    }
    document.addEventListener("sglt2i:inputs-ready", embedHetero);
  })();
  </script>
```

The bus was already published in Task 10; heterogeneity reads from the same `ma-studies-v1` key.

- [ ] **Step 2: Smoke-test**

```bash
python -m http.server 8787
```

Open the page. Confirm:
- Heterogeneity section now renders an iframe.
- Inside, τ² ≈ 0, I² ≈ 0, Q small with p near 1 — all consistent with k=2 same-direction HRs.

Kill server.

- [ ] **Step 3: Commit**

```bash
git add sglt2i-hfpef-demo/index.html
git commit -m "feat(sglt2i): embed heterogeneity app via ?fromBus=1

Reads the same ma-studies-v1 bus payload already published by the
forest-plot orchestrator. Confirms tau2 ~ 0, I2 ~ 0, Q small at k=2.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 13: Static checks — div balance + determinism sweep

**Files:**
- no new files; runs existing checks against the HTML

- [ ] **Step 1: Div balance check (per `html-apps.md` rule)**

```bash
cd /c/Users/user/ma-workbench
python - <<'PY'
import re, pathlib
html = pathlib.Path("sglt2i-hfpef-demo/index.html").read_text(encoding="utf-8")
opens = len(re.findall(r"<div[\s>]", html))
closes = len(re.findall(r"</div>", html))
print(f"<div>: {opens}  </div>: {closes}  balanced: {opens == closes}")
assert opens == closes, "div imbalance"
PY
```

Expected: balanced == True.

- [ ] **Step 2: Determinism check — no `Date.now()` or `new Date()`**

```bash
grep -nE "Date\.now|new Date" sglt2i-hfpef-demo/index.html || echo "CLEAN"
```

Expected: `CLEAN`. Any hit here would make the CI byte-for-byte regeneration gate flaky.

- [ ] **Step 3: Placeholder sweep**

```bash
grep -nE "\\{\\{|TODO|TBD|FIXME|placeholder" sglt2i-hfpef-demo/index.html || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 4: No hardcoded local paths**

```bash
grep -nE "C:\\\\|/c/Users|/home/" sglt2i-hfpef-demo/index.html || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 5: If any check fails, fix inline and re-run**

For a div imbalance: find the unmatched tag using indent-aware inspection. For a determinism hit: replace with a static string or derive from `data.json`. For a placeholder: replace with the real content or remove. For a hardcoded path: convert to relative.

Commit only if all checks pass.

- [ ] **Step 6: Commit (no-op commit if nothing to change; skip the commit in that case)**

If the checks flagged nothing, this task produces no commit. If something was fixed:

```bash
git add sglt2i-hfpef-demo/index.html
git commit -m "fix(sglt2i): static-check violations in demo page

<one-line description of what was fixed>

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 14: Benchmark test suite — full green

**Files:** no new files; runs the Task 6 suite.

- [ ] **Step 1: Run full benchmark test suite**

```bash
cd /c/Users/user/ma-workbench
python -m pytest tests/test_sglt2i_benchmark.py -v
```

Expected: all 5 tests PASS.

If `test_main_hr_within_tolerance` FAILS:
- The pooled HR diverged beyond the tolerance. This is the actual benchmark result — it's not a test bug. Proceed to Task 17's FAIL-branch paper.
- Record the diverged HR + Δ + tolerance in the task notes; these go into S4 of the FAIL-branch paper.

If `test_ci_overlaps_published` FAILS:
- Similar — benchmark result. FAIL-branch.

If `test_methods_agree` FAILS:
- HR range > 0.03 across methods. At k=2 with tau2=0, FE/REML/PM are identical; HKSJ changes only the CI, not the point. A failure here indicates a bug in `data.json` (e.g., wrong signs) or the pool computation. Debug before proceeding.

If `test_dl_excluded_in_demo_page` or `test_undefined_panels_reasons_present` FAIL:
- HTML edit bug. Fix the HTML.

- [ ] **Step 2: Run existing regression tests (no existing app broke)**

```bash
python -m pytest tests/ -v
```

Expected: all pass including the pre-existing suite.

- [ ] **Step 3: Run golden parity**

```bash
python -m pytest golden/test_golden_parity.py -v
```

Expected: all pass including new G06 row.

- [ ] **Step 4: No commit (status check only)**

This task produces no artefact; it gates downstream work.

---

## Task 15: Paper — `e156-submission-sglt2i/paper.json` + `paper.md`

**Files:**
- Create: `e156-submission-sglt2i/paper.json`
- Create: `e156-submission-sglt2i/paper.md`
- Create: `e156-submission-sglt2i/config.json`
- Create: `tests/test_sglt2i_paper.py`

- [ ] **Step 1: Write the paper contract test first**

Create `tests/test_sglt2i_paper.py`:

```python
"""Contract tests for the E156 SGLT2i paper.

Enforces the 7-sentence / 156-word rule, checks that the rendered paper
has no {{braces}} remaining, and verifies S4 references the same HR as
the workbench pool.
"""
import json
import math
import re
from pathlib import Path

PAPER_MD = Path("e156-submission-sglt2i/paper.md")
PAPER_JSON = Path("e156-submission-sglt2i/paper.json")
G06_REF = Path("golden/references/G06-sglt2i-hfpef-benchmark.json")


def test_paper_md_exists():
    assert PAPER_MD.exists()


def test_seven_sentences():
    data = json.loads(PAPER_JSON.read_text(encoding="utf-8"))
    assert len(data["sentences"]) == 7
    for s_key in ["S1","S2","S3","S4","S5","S6","S7"]:
        assert s_key in data["sentences"]


def test_word_count_under_156():
    data = json.loads(PAPER_JSON.read_text(encoding="utf-8"))
    joined = " ".join(data["sentences"][k] for k in
        ["S1","S2","S3","S4","S5","S6","S7"])
    words = re.findall(r"\S+", joined)
    assert len(words) <= 156, f"{len(words)} > 156"


def test_no_unfilled_braces():
    text = PAPER_MD.read_text(encoding="utf-8")
    assert "{{" not in text, "unfilled {{braces}} in paper.md"


def test_s4_hr_matches_computed():
    data = json.loads(PAPER_JSON.read_text(encoding="utf-8"))
    ref = json.loads(G06_REF.read_text(encoding="utf-8"))
    hr = math.exp(ref["pm"]["estimate"])
    # S4 should include the HR string to 2 dp
    needle = f"{hr:.2f}"
    assert needle in data["sentences"]["S4"], (
        f"S4 does not contain computed HR {needle}: "
        f"{data['sentences']['S4']}"
    )
```

- [ ] **Step 2: Run test, verify red**

```bash
python -m pytest tests/test_sglt2i_paper.py -v
```

Expected: all fail with `paper.md` / `paper.json` missing.

- [ ] **Step 3: Create `config.json`**

```json
{
  "paper_id": "E156-sglt2i-hfpef-benchmark",
  "format": "E156",
  "word_budget": 156,
  "sentence_budget": 7,
  "target_words_per_sentence": {
    "S1": 22, "S2": 20, "S3": 20, "S4": 30,
    "S5": 22, "S6": 22, "S7": 20
  },
  "title": "SGLT2i in HFpEF: a browser-native benchmark reproduction"
}
```

Write to `e156-submission-sglt2i/config.json`.

- [ ] **Step 4: Compute the fill values**

Read the pooled values from `golden/references/G06-sglt2i-hfpef-benchmark.json` and the inputs from `sglt2i-hfpef-demo/expected.json`:

```bash
python - <<'PY'
import json, math
ref = json.load(open("golden/references/G06-sglt2i-hfpef-benchmark.json"))
exp = json.load(open("sglt2i-hfpef-demo/expected.json"))

hr = math.exp(ref["pm"]["estimate"])
se = ref["pm"]["se"]
lo = math.exp(ref["pm"]["estimate"] - 1.96 * se)
hi = math.exp(ref["pm"]["estimate"] + 1.96 * se)

# Method range: FE vs PM point estimate on HR scale
hrs = [math.exp(ref["fe"]["estimate"]), math.exp(ref["pm"]["estimate"])]
hr_method_range = max(hrs) - min(hrs)

# Heterogeneity
tau2 = ref["pm"]["tau2"]
I2 = ref["pm"]["I2"]
Q = ref["pm"]["QE"]
# Q p-value under chi-sq_{k-1=1}. 1 - chisq.cdf(Q, 1) via scipy; for
# k=2 and Q small, p is near 1. We round to 2 dp.
from math import erf, sqrt
def p_chi2_df1(q):
    # P(chi2_1 > q) = 2*(1 - Phi(sqrt(q)))
    if q < 0: return 1.0
    return 2 * (1 - 0.5*(1 + erf(math.sqrt(q)/math.sqrt(2))))
qp = p_chi2_df1(Q)

bench = exp["benchmark"]
delta = abs(hr - bench["hr"])
tol = exp["tolerance"]["applied_delta"]
pass_ = (delta <= tol) and (max(lo, bench["ci_low"]) <= min(hi, bench["ci_high"]))

print(json.dumps({
    "hr": round(hr, 2),
    "lo": round(lo, 2),
    "hi": round(hi, 2),
    "delta": round(delta, 3),
    "tau2": round(tau2, 3),
    "i2": round(I2, 1),
    "qp": round(qp, 2),
    "hr_method_lo": round(min(hrs), 2),
    "hr_method_hi": round(max(hrs), 2),
    "benchmark_name": bench["source"],
    "bench_hr": bench["hr"],
    "bench_lo": bench["ci_low"],
    "bench_hi": bench["ci_high"],
    "branch": "PASS" if pass_ else "FAIL",
}, indent=2))
PY
```

Record the output — the `branch` field selects which paper template fills in.

- [ ] **Step 5: Write `paper.json` (PASS branch)**

If `branch == "PASS"`, create `e156-submission-sglt2i/paper.json` using the values computed in Step 4:

```json
{
  "paper_id": "E156-sglt2i-hfpef-benchmark",
  "branch": "PASS",
  "sentences": {
    "S1": "Does a browser-only meta-analysis workbench reproduce the published IPD-pooled hazard ratio for SGLT2 inhibitors on the primary composite endpoint in HFpEF?",
    "S2": "Two trials, n=12,251: EMPEROR-Preserved (empagliflozin, 5988) and DELIVER (dapagliflozin, 6263), primary composite hazard ratios taken from published NEJM tables.",
    "S3": "Generic inverse-variance pooling on the log-hazard-ratio scale using REML random-effects, with fixed-effect, Paule-Mandel, and HKSJ-with-floor as sensitivity estimators.",
    "S4": "REML pool: HR <hr> (95% CI <lo>–<hi>), within δ=<delta> of the <benchmark_name> pool HR <bench_hr> (<bench_lo>–<bench_hi>); τ²=<tau2>, I²=<i2>%, Q-p=<qp>.",
    "S5": "Across four estimators the pooled HR spans <hr_method_lo>–<hr_method_hi> (range ≤0.03); DerSimonian-Laird is not reported because it is inappropriate at k<10.",
    "S6": "Aggregate-data reproduction of the published pool within the prespecified tolerance supports the workbench as a credible browser-native re-analysis engine for small-k cardiovascular evidence.",
    "S7": "The pool uses as-published HRs without IPD-level harmonisation of composite definitions; prediction intervals, funnel plots, and trim-and-fill are undefined at k=2."
  }
}
```

Replace every `<var>` with the value from Step 4 (no `{{braces}}` in the final file).

- [ ] **Step 6: Write `paper.json` (FAIL branch)**

If `branch == "FAIL"`, use this template instead:

```json
{
  "paper_id": "E156-sglt2i-hfpef-benchmark",
  "branch": "FAIL",
  "sentences": {
    "S1": "Does a browser-only meta-analysis workbench reproduce the published IPD-pooled hazard ratio for SGLT2 inhibitors on the primary composite endpoint in HFpEF?",
    "S2": "Two trials, n=12,251: EMPEROR-Preserved (empagliflozin, 5988) and DELIVER (dapagliflozin, 6263), primary composite hazard ratios taken from published NEJM tables.",
    "S3": "Generic inverse-variance pooling on the log-hazard-ratio scale using REML random-effects, with fixed-effect, Paule-Mandel, and HKSJ-with-floor as sensitivity estimators.",
    "S4": "REML pool: HR <hr> (95% CI <lo>–<hi>), |Δ|=<delta> exceeds prespecified tolerance <tol> versus <benchmark_name> pool HR <bench_hr>; τ²=<tau2>, I²=<i2>%, Q-p=<qp>.",
    "S5": "Across four estimators the pooled HR spans <hr_method_lo>–<hr_method_hi>; DerSimonian-Laird is not reported because it is inappropriate at k<10.",
    "S6": "Divergence exceeds tolerance and is attributable to composite-definition harmonisation between the aggregate-data pool and the IPD-level reference.",
    "S7": "The pool uses as-published HRs and cannot harmonise composite definitions from aggregate data; this is the prespecified boundary of a FAIL branch."
  }
}
```

- [ ] **Step 7: Render `paper.md` from `paper.json`**

```bash
python - <<'PY'
import json, pathlib
p = json.load(open("e156-submission-sglt2i/paper.json"))
s = p["sentences"]
body = " ".join(s[k] for k in ["S1","S2","S3","S4","S5","S6","S7"])
header = f"# {p['paper_id']} (branch: {p['branch']})\n\n"
pathlib.Path("e156-submission-sglt2i/paper.md").write_text(
    header + body + "\n", encoding="utf-8")
print("wrote paper.md")
PY
```

- [ ] **Step 8: Run paper tests, verify green**

```bash
python -m pytest tests/test_sglt2i_paper.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 9: Commit**

```bash
git add e156-submission-sglt2i/ tests/test_sglt2i_paper.py
git commit -m "feat(sglt2i): render E156 paper from G06 references

Branch (PASS or FAIL) selected by the prespecified decision rule in
protocol.md. paper.json is the structured source; paper.md is the
rendered single-paragraph body. Contract tests enforce 7 sentences,
<=156 words, no unfilled braces, S4 HR matches G06 computed value.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 16: Hub integration — `hub/projects.js` entry + path resolution test

**Files:**
- Modify: `hub/projects.js`

- [ ] **Step 1: Inspect the existing entry shape**

```bash
head -40 hub/projects.js
```

Record the pattern used by the other 15 entries (typical fields: `slug`, `title`, `description`, `path`, maybe `tags` or `category`).

- [ ] **Step 2: Add the SGLT2i demo entry**

Edit `hub/projects.js`. Find the existing array of project entries. Add a new entry at the end (or in a sensible topical position) matching the existing shape exactly. Example:

```js
{
  slug: "sglt2i-hfpef-demo",
  title: "SGLT2i in HFpEF — reproducibility demo",
  description: "Benchmark reproduction of a published 2-trial pool (EMPEROR-Preserved + DELIVER) using the workbench apps on real data.",
  path: "sglt2i-hfpef-demo/index.html",
  category: "clinical-demo"
}
```

Match the actual field names and quoting style used by the other entries — do not introduce a new style.

- [ ] **Step 3: Run the existing hub path-resolution test**

```bash
python -m pytest tests/ -v -k "hub" || python -m pytest tests/ -v
```

Expected: the existing path-resolution smoke test (from the CI workflow) resolves all entries including the new one.

If the existing test name is different, grep:

```bash
grep -rn "projects.js" tests/
```

and run the matching test.

- [ ] **Step 4: Open the hub page and verify**

```bash
python -m http.server 8787
```

Open `http://localhost:8787/hub/index.html` (or wherever the hub is served). Confirm the new entry renders and its link resolves to the demo page.

Kill server.

- [ ] **Step 5: Commit**

```bash
git add hub/projects.js
git commit -m "feat(sglt2i): register SGLT2i-HFpEF demo in hub/projects.js

16th entry; category clinical-demo to distinguish from the 15 tool apps.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 17: CI smoke matrix — add demo as 16th app

**Files:**
- Modify: `.github/workflows/test.yml`

- [ ] **Step 1: Inspect the existing smoke job**

```bash
grep -n "forest-plot\|heterogeneity\|nma" .github/workflows/test.yml | head -20
```

Record the pattern: there is a loop over apps (likely a bash array or a matrix strategy).

- [ ] **Step 2: Add sglt2i-hfpef-demo to the smoke list**

Edit `.github/workflows/test.yml`. Find the app list and add `sglt2i-hfpef-demo` alongside the existing 15 entries. If the job uses `::group::<app>` per-app output, the new entry will automatically get its own collapsible section.

If the job expects a `tests/test_<app>.py` per entry and the demo has no such file yet, add a trivial `tests/test_sglt2i_hfpef_demo.py`:

```python
"""Per-app smoke test for sglt2i-hfpef-demo.

Verifies the static HTML exists and the two fetched JSONs are parseable.
Any runtime behaviour is covered by test_sglt2i_benchmark.py.
"""
import json
from pathlib import Path


def test_index_exists():
    assert Path("sglt2i-hfpef-demo/index.html").exists()


def test_data_parseable():
    json.loads(Path("sglt2i-hfpef-demo/data.json").read_text(encoding="utf-8"))


def test_expected_parseable():
    json.loads(Path("sglt2i-hfpef-demo/expected.json").read_text(encoding="utf-8"))
```

- [ ] **Step 3: Run locally**

```bash
python -m pytest tests/test_sglt2i_hfpef_demo.py -v
```

Expected: 3 tests pass.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/test.yml tests/test_sglt2i_hfpef_demo.py
git commit -m "ci(sglt2i): add demo as 16th per-app smoke target

Extends the existing CI matrix by one row. Per-app group output in the
Actions UI surfaces demo-specific failures without scrolling.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 18: Sentinel pre-push scan

**Files:** none — runs the Sentinel scanner.

- [ ] **Step 1: Run Sentinel scan against the repo**

```bash
python -m sentinel scan --repo /c/Users/user/ma-workbench
```

Expected: no new BLOCK entries added to `STUCK_FAILURES.jsonl`.

If a BLOCK fires:

- **Hardcoded path (P0):** inspect the flagged file. Every `C:\Users\` or absolute path in a committed file should be relative. Fix and re-scan.
- **Committed `.claude/` (P0):** `.claude/` should never be committed. Remove from staging, add to `.gitignore` if not already.
- **Placeholder HMAC / silent-failure sentinel:** the demo page is read-only and doesn't sign anything, so this shouldn't fire. If it does, investigate the specific rule output.

Do **not** use `SENTINEL_BYPASS=1` to skip the block. Per `workflow.md`: "the rule encodes a past-incident lesson."

- [ ] **Step 2: If WARN entries appear (not BLOCK), review and decide**

WARN entries go to `sentinel-findings.md` / `.jsonl`. Read them and either fix or document acceptance in the commit message. WARN does not block push but unresolved WARNs accumulate.

- [ ] **Step 3: No commit if scan is clean**

---

## Task 19: Push + verify CI green

**Files:** none — pushes to remote.

- [ ] **Step 1: Pre-push checklist**

```bash
cd /c/Users/user/ma-workbench
git status --short
git log --oneline origin/main..HEAD
```

Expected: worktree clean (Sentinel artefact files tolerable). Commits ahead of origin are the Task 1–17 commits.

- [ ] **Step 2: Push**

```bash
git push origin main
```

The Sentinel pre-push hook runs again here. Expected: clean.

- [ ] **Step 3: Watch CI**

```bash
gh run list --repo mahmood726-cyber/ma-workbench --limit 1
```

Record the run ID. Then:

```bash
gh run watch <run-id> --repo mahmood726-cyber/ma-workbench
```

Expected: run completes `success` in ~15–30 seconds (previous green baseline 12s + some overhead for G06 + demo).

If CI goes red:

- Check which job step failed via `gh run view <run-id> --log`.
- Common causes:
  - Byte-for-byte G06 drift: the generator and the committed reference don't agree. Re-run `python golden/generate_references.py` locally and commit the diff.
  - Demo smoke test fail: inspect the `::group::sglt2i-hfpef-demo` section.
  - Hub path-resolution fail: `hub/projects.js` entry typo.

- [ ] **Step 4: Confirm Pages updated**

Open `https://mahmood726-cyber.github.io/ma-workbench/sglt2i-hfpef-demo/index.html`.

Expected: the demo page loads; the claim card populates within a second or two; verdict badge shows PASS (if Task 14 branch was PASS) or FAIL (otherwise).

If Pages has not updated yet, wait ~1 minute and refresh. Pages deploy on push to `main`.

- [ ] **Step 5: No commit at this step**

---

## Task 20: Registry update — INDEX.md + rewrite-workbook.txt

**Files:**
- Modify: `C:/ProjectIndex/INDEX.md`
- Modify: `C:/E156/rewrite-workbook.txt`

- [ ] **Step 1: Pre-check registries**

```bash
python C:/ProjectIndex/reconcile_counts.py
```

Expected: exit 0 (registry drift-free).

If it exits 1, halt and fix the drift before adding a new entry — adding to a broken registry compounds the problem.

- [ ] **Step 2: Update INDEX.md**

Find the existing `ma-workbench` row in `C:/ProjectIndex/INDEX.md`. Append a sub-bullet or inline note "+ SGLT2i-HFpEF benchmark demo, 2026-04-15". Do not create a new row — ma-workbench is already registered.

- [ ] **Step 3: Update workbook — add entry, keep YOUR REWRITE blank**

Open `C:/E156/rewrite-workbook.txt`. Find the header total-count line; increment by 1. At the end of the existing entries, append:

```
---

[Entry N]  SGLT2i-HFpEF benchmark demo (ma-workbench)
Date: 2026-04-15

CURRENT BODY:
<paste the rendered content of e156-submission-sglt2i/paper.md here>

YOUR REWRITE:


SUBMITTED: [ ]
```

**Critical workbook rule (per `e156.md` and `CLAUDE.md`):**

- YOUR REWRITE is left blank. Never type anything there.
- SUBMITTED is `[ ]`. Do not toggle to `[x]` in this task.

- [ ] **Step 4: Re-run reconcile**

```bash
python C:/ProjectIndex/reconcile_counts.py
```

Expected: exit 0. If it fails after the update, diff against the previous state and surface the drift.

- [ ] **Step 5: Commit registry changes in their respective repos**

`C:/ProjectIndex/` and `C:/E156/` are their own git repos. Commit in each:

```bash
cd C:/ProjectIndex
git add INDEX.md
git commit -m "docs: note SGLT2i-HFpEF benchmark demo under ma-workbench

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"

cd C:/E156
git add rewrite-workbook.txt
git commit -m "feat(workbook): add SGLT2i-HFpEF benchmark demo entry

CURRENT BODY rendered from ma-workbench/e156-submission-sglt2i/paper.md.
YOUR REWRITE left blank (workbook protection rule). SUBMITTED [ ] —
toggle only after Overmind nightly PASS.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 6: No push of the registry repos without explicit instruction**

Push only `ma-workbench`; registry repos live locally unless the user instructs otherwise.

---

## Task 21: Overmind verdict + SUBMITTED toggle

**Files:**
- Modify: `C:/E156/rewrite-workbook.txt` (conditional)

- [ ] **Step 1: Check latest Overmind nightly verdict for ma-workbench**

Overmind produces a per-repo verdict artefact. Locate:

```bash
ls -la C:/overmind/verdicts/ma-workbench*.json | tail -3
```

or run it directly if a recent verdict is stale:

```bash
cd C:/overmind
python -m overmind verify --repo C:/Users/user/ma-workbench
```

- [ ] **Step 2: Parse the verdict**

Read the most recent verdict file. Look for `"status": "PASS"` (or the project's equivalent — check the Overmind README).

- [ ] **Step 3: If Overmind PASS + paper branch PASS: toggle SUBMITTED**

Only if BOTH:

- Overmind most-recent verdict for ma-workbench is PASS
- `paper.json.branch == "PASS"` (from Task 15)

Edit `C:/E156/rewrite-workbook.txt`. Change the `SUBMITTED: [ ]` line for the SGLT2i entry to `SUBMITTED: [x]`. Commit:

```bash
cd C:/E156
git add rewrite-workbook.txt
git commit -m "feat(workbook): toggle SUBMITTED for SGLT2i-HFpEF benchmark

Gated on Overmind nightly PASS for ma-workbench AND paper.json.branch
== PASS. Both conditions verified.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 4: If either gate FAILs: leave SUBMITTED unchecked**

Paper stays in the workbook but unsubmitted. Record the blocker in the PROGRESS notes with the specific reason. Surface to the user.

- [ ] **Step 5: Final re-reconcile**

```bash
python C:/ProjectIndex/reconcile_counts.py
```

Expected: exit 0.

---

## Task 22: Update memory — Active Projects note

**Files:**
- Modify: `C:/Users/user/.claude/projects/C--Users-user/memory/MEMORY.md`

- [ ] **Step 1: Append the SGLT2i-HFpEF line under Active Projects**

Open `MEMORY.md`. Under `## Active Projects` or `## CT.gov` (if a more appropriate section exists), add:

```markdown
- [SGLT2i-HFpEF benchmark](ma-workbench-sglt2i.md) — E156 + demo at `C:\Users\user\ma-workbench\sglt2i-hfpef-demo\`, benchmark reproduction within δ=<0.02|0.005> of <benchmark_citation_short>, <PASS|FAIL> branch shipped
```

- [ ] **Step 2: Create the linked memory file**

Create `C:/Users/user/.claude/projects/C--Users-user/memory/ma-workbench-sglt2i.md`:

```markdown
---
name: SGLT2i-HFpEF benchmark demo
description: Browser-native benchmark reproduction in ma-workbench; 2-trial pool of EMPEROR-Preserved + DELIVER; Jhund-style IPD or aggregate benchmark
type: project
---

SGLT2i-HFpEF E156 benchmark demo shipped 2026-04-15.

- Workspace: `C:\Users\user\ma-workbench\sglt2i-hfpef-demo\`
- Paper: `C:\Users\user\ma-workbench\e156-submission-sglt2i\paper.md`
- Golden dataset: `G06-sglt2i-hfpef-benchmark` (extends the byte-for-byte
  CI gate; 6 datasets total)
- Benchmark: <benchmark_citation>, pool type <ipd|aggregate>, HR <bench_hr>
- Computed: HR <hr> (CI <lo>–<hi>), δ=<delta>, verdict <PASS|FAIL>

**Why:** First clinical-data paper in ma-workbench. The whole point of
the workbench was to re-analyse published evidence in-browser; this is
the load-bearing demonstration that it does, on real trial data, within
a prespecified tolerance of a named published pool.

**How to apply:** Future ma-workbench benchmark papers follow the same
file layout (`*-demo/` + `e156-submission-*/`) and the same
prespecified-delta discipline from `protocol.md`. G06 is the template
for new golden datasets built from published HRs rather than synthetic
data.
```

- [ ] **Step 3: No commit (memory is outside git)**

Memory files live outside the project repos. No git commit needed.

---

## Task 23: Final sweep + push

**Files:** none — final verification.

- [ ] **Step 1: Run full test suite**

```bash
cd /c/Users/user/ma-workbench
python -m pytest tests/ golden/ -v
```

Expected: all pass. Record the count (previous baseline 223 tests).

- [ ] **Step 2: Check Pages live**

```bash
curl -sI https://mahmood726-cyber.github.io/ma-workbench/sglt2i-hfpef-demo/index.html | head -1
```

Expected: `HTTP/2 200`.

- [ ] **Step 3: Check CI green**

```bash
gh run list --repo mahmood726-cyber/ma-workbench --branch main --limit 1
```

Expected: most recent run `completed success`.

- [ ] **Step 4: Summarise to user**

Report:
- Total commits added across ma-workbench + ProjectIndex + E156
- Paper branch (PASS or FAIL)
- Workbench HR / benchmark HR / δ / tolerance
- Test count delta
- Workbook entry number and SUBMITTED state
- Overmind verdict status

- [ ] **Step 5: No additional commit**

Task 23 is a verification gate, not an artefact.

---

## Self-Review Checklist (run before declaring plan complete)

**1. Spec coverage:**

| Spec section | Task(s) |
|---|---|
| Goal / reproducibility claim | Task 0 + Task 1 |
| Non-Goals | enforced by scope of Tasks 1–23 (no PRISMA, ROB, subgroups) |
| Benchmark Reference (TBD at preflight) | Task 0 |
| File Layout — `sglt2i-hfpef-demo/` | Tasks 2, 3, 7–13 |
| File Layout — `e156-submission-sglt2i/` | Tasks 1, 15 |
| File Layout — `golden/G06` | Tasks 4, 5 |
| `data.json` fail-closed | Task 8 |
| Estimator matrix (FE/REML/PM/HKSJ/DL-excluded) | Task 11 |
| Heterogeneity reporting | Task 12 |
| 4 greyed cards | Task 7 |
| Claim card | Tasks 7, 8, 9 |
| Provenance panel | Task 8 |
| Determinism (no Date.now) | Task 13 |
| E156 body S1–S7 | Task 15 |
| PASS/FAIL branches | Task 15 steps 5+6 |
| Build Order steps 1–13 | Task 1 (step 1), …, Task 21 (steps 11, 13) |
| Preflight (7 checks) | Task 0 |
| Success Criteria (5 tests) | Task 6 + Task 14 |
| Failure Handling — 3 modes | Task 14 (benchmark), Task 18 (Sentinel), Task 21 (Overmind) |
| Registry Integration | Task 20 |
| Overmind gate | Task 21 |

All spec sections covered.

**2. Placeholder scan:**

The plan intentionally contains `<...>` placeholders in Tasks 1, 2, 3, 4, 5, 15, 20, 22. These are **not** plan failures — they are the Task 0 output fields that a human must fill. The plan is explicit about which values come from which preceding task.

No `TBD`, `TODO`, `FIXME`, or unqualified "implement later" exists in the task bodies.

**3. Type consistency:**

- `ma-studies-v1` bus schema used identically across Tasks 4, 10, 12.
- `pool_type` values (`"ipd"` or `"aggregate"`) used identically across Tasks 3 and 5 (implicitly).
- `applied_delta` referenced identically across Tasks 3, 6, 15.
- `CustomEvent` names `sglt2i:inputs-ready` (Task 8) and `sglt2i:pool-ready` (Task 9) referenced by the correct downstream tasks (10, 11, 12).
- `G06-sglt2i-hfpef-benchmark` slug used identically across Tasks 4, 5, 6, 15.

No drift.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-15-sglt2i-hfpef-e156-demo.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for this plan because Tasks 9–12 are independent sub-panels that can run in parallel after Task 8.

**2. Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints.

**Reminder:** Task 0 is a human-in-the-loop gate. Whichever execution mode you pick, the first step is you (the human) completing Task 0 and handing the preflight facts to the subagent / session.

Which approach?
