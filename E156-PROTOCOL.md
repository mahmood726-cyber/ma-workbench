# E156 Protocol — MA Workbench

This repository is tracked under the **E156 micro-paper** format (7 sentences, ≤156 words, single paragraph).

- **Slug:** `ma-workbench`
- **Date:** 2026-04-14
- **Version:** 1.1
- **Author:** Mahmood Ahmad (Tahir Heart Institute)

## Abstract (144 / 156 words)

> Can a browser-native toolkit deliver the common methods of meta-analysis with R-parity validation, eliminating package-install friction for applied reviewers? We built MA Workbench, fifteen single-file HTML apps covering PRISMA, pairwise pooling, heterogeneity, bias, DTA, and network meta-analysis. Each app implements Paule-Mandel τ², Knapp-Hartung CIs, Egger regression, Moses SROC, contrast-based NMA, and HMAC-signed TruthCert receipts. A paste-once shared bus propagates studies across every app; optional in-browser WebR runs `metafor::rma` and diffs to four decimal places, producing signed receipts verifiable via constant-time comparison. 185 tests pass across sixteen suites including a cross-module contract test and HMAC sign-verify roundtrip; Egger matches `statsmodels` to four significant figures. The toolkit lowers adoption cost for single-site reviewers and gives editors a verifiable bridge between browser estimates and R without data leaving the device. Network meta-regression, multi-arm τ²/2 correction, hierarchical Bayesian pooling via `stan`, and individual-patient-data methods remain out of scope.

## Full paper package

| File | Purpose |
|---|---|
| [`e156-submission/paper.md`](./e156-submission/paper.md) | Full paper with sentence-role table and reproducibility block |
| [`e156-submission/config.json`](./e156-submission/config.json) | Structured version (sentences + metadata) |
| [`e156-submission/protocol.md`](./e156-submission/protocol.md) | Submission protocol + non-claims |
| [`e156-submission/index.html`](./e156-submission/index.html) | Paper-as-dashboard — abstract + live app links + validation card |

## Live

- Dashboard: https://mahmood726-cyber.github.io/ma-workbench/e156-submission/
- Live demo (launcher): https://mahmood726-cyber.github.io/ma-workbench/
- Workbench (one-paste): https://mahmood726-cyber.github.io/ma-workbench/workbench/

## Submission state

`SUBMITTED: [ ]` — draft. Author retains control of the `YOUR REWRITE` section in the workbook.
