# Golden-Dataset Validation

This folder commits **five hand-curated meta-analysis datasets** and their
reference Paule-Mandel / fixed-effect pooled outputs. The browser apps, and
any external validator (`metafor::rma` via WebR, a local R install, or
another pooling library), **must reproduce these reference values to
four decimal places**. That match is the public parity claim of MA
Workbench.

## What's in here

```
golden/
├── datasets/            # ma-studies-v1 bus-compatible inputs + R script
│   ├── G01-homogeneous-small.json
│   ├── G02-moderate-heterogeneity.json
│   ├── G03-high-heterogeneity.json
│   ├── G04-large-trial-dominance.json
│   └── G05-null-crossing.json
├── references/          # expected FE/RE/τ²/I²/Q/PI per dataset
│   └── … (same slugs)
├── generate_references.py  # deterministic regenerator (idempotent)
├── test_golden_parity.py   # pytest: committed refs match fresh recompute
├── SUMMARY.json         # one-liner per dataset for quick comparison
└── README.md            # (this file)
```

## How to verify the browser output matches

### 1. Manually — drop a dataset into any app

```
# In any study-based app (forest-plot, heterogeneity, meta-regression, …)
#  • Click "↓ Shared" after pasting the JSON from
#    golden/datasets/G02-moderate-heterogeneity.json into the ma-studies-v1
#    slot (or use the workbench to populate the bus first).
#  • Compare the app's pooled estimate / τ² / I² to
#    golden/references/G02-moderate-heterogeneity.json.
```

### 2. Automatic — via the WebR validator

1. Open `workbench/index.html`.
2. Load any golden dataset into the textarea (first 3 columns).
3. Click **Validate (R)** — opens the WebR validator with `?fromBus=1`.
4. In the validator, click **Run in WebR**. The app downloads WebR once
   (~30 MB), runs `metafor::rma(yi, sei, method="PM")`, parses the
   output, and diffs each field against the browser computation at
   **1e-4 tolerance**. A signed TruthCert receipt records the match.

### 3. Automatic — via R locally

```r
# Each dataset JSON ships a ready-to-run metafor script:
python -c "import json; print(json.load(open('golden/datasets/G02-moderate-heterogeneity.json'))['r_script'])" > g02.R
Rscript g02.R
# Compare the printed estimate / se / tau2 / I2 / QE to the reference file.
```

### 4. Automatic — Python drift test

```
python -m pytest golden/ -v
```

This recomputes the references from the same Python formulas the browser
apps implement and asserts byte-match with the committed JSONs. It does
**not** exercise the JS — it protects against accidental drift in the
datasets or the Python estimator itself.

## The parity claim

| Field                      | Tolerance | Rationale                       |
|----------------------------|-----------|---------------------------------|
| FE estimate (`b`)          | 1e-4      | Closed-form IV pooling          |
| FE SE                      | 1e-4      | `sqrt(1/Σw)`                    |
| RE estimate (`b`, PM)      | 1e-4      | Bisection on Q = k−1            |
| RE SE                      | 1e-4      |                                 |
| τ² (Paule-Mandel)          | 1e-4      | Accepted for any k              |
| I² (%)                     | 1e-4      | `max(0, 100·(Q − df)/Q)`        |
| Q (heterogeneity stat)     | 1e-4      | Weighted RSS under FE           |
| 95% prediction interval    | 1e-3      | `t_{k-2}` critical — table-interp reduces precision slightly |

If the browser disagrees at any of these tolerances, the WebR validator
will emit a **signed `_mismatch_` receipt** and refuse to round-trip the
TruthCert — that is the enforceable public contract.

## Regenerating

```
python golden/generate_references.py
```

Deterministic. No network, no RNG. Two runs produce byte-identical JSON.

## Extending the golden set

Append a new entry to `DATASETS` in `generate_references.py`, rerun the
script. A new `test_golden_parity.py` case is picked up automatically for
any dataset with matching `datasets/*.json` + `references/*.json`.
