Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

MA Workbench: A Browser-Native Meta-Analysis Suite with Optional WebR Validation Against metafor

Can a browser-native toolkit deliver the common methods of meta-analysis with R-parity validation, eliminating package-install friction for applied reviewers? We built MA Workbench, fifteen single-file HTML apps covering PRISMA, pairwise pooling, heterogeneity, bias, DTA, and network meta-analysis. Each app implements Paule-Mandel tau-squared, Knapp-Hartung CIs, Egger regression, Moses SROC, contrast-based NMA, and HMAC-signed TruthCert receipts. A paste-once shared bus propagates studies across every app; WebR runs metafor::rma and diffs to 4 decimal places, achieving 100 percent parity, producing signed receipts via comparison. 185 tests pass across sixteen suites including a cross-module contract test and HMAC sign-verify roundtrip; Egger matches statsmodels to four significant figures. The toolkit lowers adoption cost for single-site reviewers and gives editors a verifiable bridge between browser estimates and R without data leaving the device. Network meta-regression, multi-arm tau-squared-over-two correction, hierarchical Bayesian pooling via stan, and individual-patient-data methods remain out of scope; this framework ensures high-assurance evidence synthesis for cardiology research and global health.

Outside Notes

Type: methods
Primary estimand: Four-decimal-place parity of pooled estimate, SE, 95% CI, tau-squared, I-squared, and Q between browser and metafor
App: MA Workbench v1.1
Data: No external dataset; validation is computational — tool outputs are diffed against metafor::rma via an embedded WebR runtime
Code: https://github.com/mahmood726-cyber/ma-workbench
Version: 1.1
Validation: browser vs metafor: four-decimal-place diff; HMAC sign-verify roundtrip passes correct-key / wrong-key / tampered-body

References

1. Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. BMJ. 2021;372:n71.
2. Moher D, Liberati A, Tetzlaff J, Altman DG. Preferred reporting items for systematic reviews and meta-analyses: the PRISMA statement. PLoS Med. 2009;6(7):e1000097.
3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.
