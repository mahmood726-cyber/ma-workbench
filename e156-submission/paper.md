# MA Workbench: A Browser-Native Meta-Analysis Suite with Optional WebR Validation Against `metafor`

**Mahmood Ahmad** — Tahir Heart Institute
Date: 2026-04-14 | Version: 1.1 | Format: E156 (7 sentences, ≤156 words)

---

## Abstract

Can a browser-native toolkit deliver the common methods of meta-analysis with R-parity validation, eliminating package-install friction for applied reviewers? We built MA Workbench, fifteen single-file HTML apps covering PRISMA, pairwise pooling, heterogeneity, bias, DTA, and network meta-analysis. Each app implements Paule-Mandel τ², Knapp-Hartung CIs, Egger regression, Moses SROC, contrast-based NMA, and HMAC-signed TruthCert receipts. A paste-once shared bus propagates studies across every app; optional in-browser WebR runs `metafor::rma` and diffs to four decimal places, producing signed receipts verifiable via constant-time comparison. 185 tests pass across sixteen suites including a cross-module contract test and HMAC sign-verify roundtrip; Egger matches `statsmodels` to four significant figures. The toolkit lowers adoption cost for single-site reviewers and gives editors a verifiable bridge between browser estimates and R without data leaving the device. Network meta-regression, multi-arm τ²/2 correction, hierarchical Bayesian pooling via `stan`, and individual-patient-data methods remain out of scope.

---

## Sentence roles (E156 contract)

| # | Role           | Words | Sentence |
|---|----------------|------:|----------|
| 1 | Question       |    19 | Can a browser-native toolkit deliver the common methods of meta-analysis with R-parity validation, eliminating package-install friction for applied reviewers? |
| 2 | Dataset        |    18 | We built MA Workbench, fifteen single-file HTML apps covering PRISMA, pairwise pooling, heterogeneity, bias, DTA, and network meta-analysis. |
| 3 | Method         |    17 | Each app implements Paule-Mandel τ², Knapp-Hartung CIs, Egger regression, Moses SROC, contrast-based NMA, and HMAC-signed TruthCert receipts. |
| 4 | Primary result |    27 | A paste-once shared bus propagates studies across every app; optional in-browser WebR runs `metafor::rma` and diffs to four decimal places, producing signed receipts verifiable via constant-time comparison. |
| 5 | Robustness     |    22 | 185 tests pass across sixteen suites including a cross-module contract test and HMAC sign-verify roundtrip; Egger matches `statsmodels` to four significant figures. |
| 6 | Interpretation |    24 | The toolkit lowers adoption cost for single-site reviewers and gives editors a verifiable bridge between browser estimates and R without data leaving the device. |
| 7 | Boundary       |    17 | Network meta-regression, multi-arm τ²/2 correction, hierarchical Bayesian pooling via `stan`, and individual-patient-data methods remain out of scope. |

**Total:** 144 words (cap = 156). **Sentences:** 7 (contract = 7).

---

## Code, data, live demo

- **Repo:** https://github.com/mahmood726-cyber/ma-workbench
- **Pages:** https://mahmood726-cyber.github.io/ma-workbench/
- **Apps (all single-file HTML, offline):** workbench, prisma-screen, prisma-flow, forest-plot, funnel-plot, rob-traffic-light, heterogeneity, meta-regression, cumulative-subgroup, tsa, bayesian-ma, dta-sroc, grade-sof, nma, webr-validator.
- **Data:** no external dataset; computational validation only.

## Validation summary

- **Method parity:** Egger regression matches `statsmodels` OLS to 4 significant figures on an n=10 dataset.
- **Conjugate posterior (Bayesian MA):** closed-form — no MCMC, no stan.
- **τ² estimators:** Paule-Mandel (default, any k), REML (any k), DerSimonian-Laird (gated to k ≥ 10 per Viechtbauer/Langan).
- **Prediction interval:** `t(k-2)` (undefined for k<3).
- **HKSJ q floor:** `max(1, RSS/(k-p))` — prevents under-covering CIs.
- **Continuity correction (DTA):** applied only when a cell is zero (never unconditional).
- **WebR bridge:** `metafor::rma(yi, sei=sei, method="PM", test="z")` output diffed to 4 decimal places; match / mismatch baked into the signed receipt.
- **HMAC receipts:** SHA-256, key from user password input (never bundled, never stored), constant-time verify via `crypto.subtle.verify`, `_key_id = SHA-256(key)[0:16]` so reviewers know which key signed without seeing it.

## Reproducibility

```
git clone https://github.com/mahmood726-cyber/ma-workbench
cd ma-workbench
python -m http.server 8080       # any static server
# open http://localhost:8080/

# Tests
python -m pytest tests/                                # contracts
for d in workbench forest-plot funnel-plot heterogeneity tsa \
         meta-regression cumulative-subgroup bayesian-ma dta-sroc \
         grade-sof prisma-flow prisma-screen rob-traffic-light \
         webr-validator nma; do
  python -m pytest "$d/tests" -q
done
```

## References

1. Viechtbauer W. Conducting meta-analyses in R with the **metafor** package. J Stat Softw. 2010;36(3):1-48.
2. DerSimonian R, Laird N. Meta-analysis in clinical trials. Controlled Clin Trials. 1986;7(3):177-88.
3. Paule RC, Mandel J. Consensus values and weighting factors. J Res Natl Bur Stand. 1982;87(5):377-85.
4. Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. BMJ. 1997;315(7109):629-34.
5. Knapp G, Hartung J. Improved tests for a random effects meta-regression with a single covariate. Stat Med. 2003;22(17):2693-710.
6. Lu G, Ades AE. Combination of direct and indirect evidence in mixed treatment comparisons. Stat Med. 2004;23(20):3105-24.
7. Moses LE, Shapiro D, Littenberg B. Combining independent studies of a diagnostic test into a summary ROC curve. Stat Med. 1993;12(14):1293-316.
8. Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. BMJ. 2021;372:n71.

AI Disclosure

This work represents a compiler-generated evidence micro-publication (i.e., a structured, pipeline-based synthesis output). AI (Claude, Anthropic) was used as a constrained synthesis engine operating on structured inputs and predefined rules for infrastructure generation, not as an autonomous author. The 156-word body was written and verified by the author, who takes full responsibility for the content. This disclosure follows ICMJE recommendations (2023) that AI tools do not meet authorship criteria, COPE guidance on transparency in AI-assisted research, and WAME recommendations requiring disclosure of AI use. All analysis code, data, and versioned evidence capsules (TruthCert) are archived for independent verification.
