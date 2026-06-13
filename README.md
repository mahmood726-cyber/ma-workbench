# MA Workbench

[![test](https://github.com/mahmood726-cyber/ma-workbench/actions/workflows/test.yml/badge.svg)](https://github.com/mahmood726-cyber/ma-workbench/actions/workflows/test.yml)
[![pages](https://img.shields.io/badge/pages-live-success)](https://mahmood726-cyber.github.io/ma-workbench/)
[![licence](https://img.shields.io/badge/licence-MIT-informational)](./LICENSE)

**An integrated, browser-native meta-analysis suite.** Eighteen single-file
HTML tools connected by a shared data bus, with optional in-browser R
validation against `metafor` and HMAC-signed TruthCert receipts. Every
push to `main` runs the contract tests, the golden-dataset parity tests,
and every per-app smoke suite — see the badge above.

Live demo: `https://mahmood726-cyber.github.io/ma-workbench/`
Paper (E156): `https://mahmood726-cyber.github.io/ma-workbench/e156-submission/`
Golden validation: `https://mahmood726-cyber.github.io/ma-workbench/golden/README.md`

## What's in the box

| Category | Apps |
|---|---|
| **Integrator** | MA Workbench (`workbench/`) |
| **Pre-MA** | PRISMA Screening, PRISMA Flow |
| **Core MA** | Forest Plot Viewer, Funnel Plot Explorer, Heterogeneity Explorer, Meta-Regression, Cumulative + Subgroup, TSA Calculator, Bayesian MA |
| **Specialised** | Network Meta-Analysis, DTA SROC Explorer, RoB Traffic Light |
| **Reporting** | GRADE SoF Builder |
| **Validation** | WebR Validator (HMAC-signed receipts) |

Every app is a single `index.html` with no build step, no external
runtime CDN, no npm packages. Paste studies, get figures + JSON state.

## The `ma-studies-v1` data bus

Paste your studies once in the **MA Workbench** or any study-based app
and click **↑ Shared**. Then in any other app (forest, funnel,
heterogeneity, TSA, meta-regression, cumulative+subgroup, Bayesian, or
the validator), click **↓ Shared** to pull the same rows. Identical
numbers everywhere; no copy-paste drift.

## Validation against R

The **WebR Validator** offers two paths:

1. **WebR (in-browser R)** — ~30 MB one-time download on first click;
   runs `metafor::rma(yi, sei, method="PM", test="z")` entirely in your
   browser tab. URL is user-configurable for self-hosting.
2. **Paste-back** — export a ready-to-run R script, execute in your
   local R, paste the console output back, the app diffs to 4 decimal
   places.

Either path produces a **signed TruthCert receipt** (JSON). The signing
key comes from a password input (never stored, never in the bundle);
verification uses Web Crypto `subtle.verify` for constant-time
comparison. Receipts include a `_key_id` (SHA-256 prefix of the key) so
a reviewer can confirm which key signed without ever seeing it.

## Security + crypto

- **HMAC-SHA256** signing, canonical-JSON body.
- Key sourced from user password input only. Never persisted.
- `constant-time` verification via Web Crypto `subtle.verify`.
- Receipts without a real signature are explicitly labelled
  `_legacy_unsigned` — no placeholder values.

## Methods anchored to advanced-stats conventions

- `tau^2` estimators: Paule-Mandel (default, any k), REML, DerSimonian-
  Laird (k ≥ 10 only, per `advanced-stats.md` gate).
- 95% prediction interval with `t(k-2)`, undefined below k=3.
- Egger's regression uses a full t-distribution via regularized
  incomplete beta (matches `statsmodels` to 4 sig figs).
- Continuity correction for DTA applied **only** when a cell is zero
  (never unconditional).
- HKSJ `q` floored at `max(1, RSS/(k-p))` for meta-regression CIs.

## Running locally

Any static HTTP server works (some apps want HTTP for `fetch`/
`localStorage` niceties; most work over `file://` too):

```powershell
.\serve-html-apps.ps1 -Open    # Windows
python -m http.server 8080     # cross-platform
```

Then open `http://localhost:8080/` and launch any app.

## Tests

```bash
# Contract tests (bus + crypto)
python -m pytest tests/

# Per-app smoke tests
for d in workbench forest-plot funnel-plot heterogeneity tsa meta-regression \
         cumulative-subgroup bayesian-ma nma dta-sroc grade-sof prisma-flow \
         prisma-screen rob-traffic-light webr-validator; do
  python -m pytest "$d/tests" -q
done
```

235 tests pass across the root, golden, and per-app suites.

## Limitations (honest non-goals)

- **Not a replacement for R** for Bayesian NMA with stan, multivariate
  MoM, robust variance estimation, or cluster-correlated effects.
- Meta-regression supports **one moderator** (not a full design matrix).
- Network meta-analysis is **contrast-based (frequentist)** only — no
  Bayesian NMA, and no individual-patient data pipeline.
- Bayesian MA uses a **conjugate normal-normal** posterior; not a full
  hierarchical model with τ² prior.

For those methods, use `metafor` / `brms` / `multinma` and reference the
WebR validator for a bridge.

## Citation

If you use this suite in a published meta-analysis, please cite:

> Ahmad, M. *MA Workbench: browser-native meta-analysis with HMAC-signed
> validation against metafor.* 2026.

## Licence

MIT. See `LICENSE`.
