window.HTML_APPS_PROJECTS = [
  {
    name: "MA Workbench",
    folder: "workbench",
    path: "./workbench/index.html",
    collection: "new",
    mode: "file",
    category: "Integrator",
    summary: "One paste, full MA: live forest / funnel / heterogeneity / TSA previews with deep-links to dedicated apps. One-click full HTML report export.",
    note: "Start here. Writes to the shared ma-studies-v1 bus so every other app can pull.",
    tags: ["workbench", "integrator", "bus"]
  },
  {
    name: "PRISMA Screening",
    folder: "prisma-screen",
    path: "./prisma-screen/index.html",
    collection: "new",
    mode: "file",
    category: "Pre-MA Pipeline",
    summary: "Citation-level include / exclude / duplicate / maybe tagging, Cohen's \u03ba for dual-reviewer agreement, PRISMA-shaped count roll-up, one-click push to the PRISMA Flow generator.",
    note: "Outputs feed directly into prisma-flow/index.html via the prisma-flow-v1 key.",
    tags: ["prisma", "screening", "kappa"]
  },
  {
    name: "PRISMA Flow",
    folder: "prisma-flow",
    path: "./prisma-flow/index.html",
    collection: "new",
    mode: "file",
    category: "Pre-MA Pipeline",
    summary: "PRISMA 2020 flow-diagram generator: enter record counts, render SVG, export as SVG or PNG. Built-in consistency checks.",
    note: "Deterministic output, offline, single-file.",
    tags: ["prisma", "systematic-review", "flow-diagram"]
  },
  {
    name: "Forest Plot Viewer",
    folder: "forest-plot",
    path: "./forest-plot/index.html",
    collection: "new",
    mode: "file",
    category: "Evidence Synthesis",
    summary: "Standalone forest plot from pasted (label, estimate, SE) studies. Fixed-effect and Paule-Mandel random-effects pooling with I\u00b2 and \u03c4\u00b2.",
    note: "SVG / PNG / JSON export; bus-aware.",
    tags: ["forest-plot", "meta-analysis", "pooling"]
  },
  {
    name: "Funnel Plot Explorer",
    folder: "funnel-plot",
    path: "./funnel-plot/index.html",
    collection: "new",
    mode: "file",
    category: "Evidence Synthesis",
    summary: "Funnel plot with 95% / 99% pseudo-CI limits plus Egger's regression test for small-study effects (p-value via incomplete-beta t-distribution).",
    note: "Validated against statsmodels OLS. Low-k warning below 10 studies.",
    tags: ["funnel-plot", "publication-bias", "egger"]
  },
  {
    name: "RoB Traffic Light",
    folder: "rob-traffic-light",
    path: "./rob-traffic-light/index.html",
    collection: "new",
    mode: "file",
    category: "Evidence Synthesis",
    summary: "Risk-of-bias traffic-light plot plus weighted summary bar, robvis-style palette. Accepts low / some / high / unclear / na ratings.",
    note: "Matrix grid + weighted-summary view; print-safe glyphs.",
    tags: ["risk-of-bias", "rob2", "robvis"]
  },
  {
    name: "Heterogeneity Explorer",
    folder: "heterogeneity",
    path: "./heterogeneity/index.html",
    collection: "new",
    mode: "file",
    category: "Evidence Synthesis",
    summary: "Q, I\u00b2, \u03c4\u00b2 under DL (k\u226510) / REML / PM, 95% prediction interval via t(k-2), Baujat diagnostic plot, and leave-one-out influence.",
    note: "Follows the no-DL-for-k<10 guard.",
    tags: ["heterogeneity", "baujat", "prediction-interval"]
  },
  {
    name: "Meta-Regression",
    folder: "meta-regression",
    path: "./meta-regression/index.html",
    collection: "new",
    mode: "file",
    category: "Evidence Synthesis",
    summary: "Random-effects meta-regression with one moderator. Paule-Mandel \u03c4\u00b2, Knapp-Hartung t(k-2) CIs with max(1, \u2026) HKSJ floor.",
    note: "Exports a metafor R script for PM + knha replication.",
    tags: ["meta-regression", "knapp-hartung", "moderator"]
  },
  {
    name: "Cumulative + Subgroup",
    folder: "cumulative-subgroup",
    path: "./cumulative-subgroup/index.html",
    collection: "new",
    mode: "file",
    category: "Evidence Synthesis",
    summary: "Cumulative MA over study order/year; subgroup analysis with between-subgroup Q test and I\u00b2 of differences.",
    note: "Two views in one app; bus-aware.",
    tags: ["cumulative", "subgroup", "temporal"]
  },
  {
    name: "TSA Calculator",
    folder: "tsa",
    path: "./tsa/index.html",
    collection: "new",
    mode: "file",
    category: "Evidence Synthesis",
    summary: "Trial sequential analysis: cumulative Z-score against O'Brien-Fleming alpha-spending boundaries; diversity-adjusted Required Information Size.",
    note: "Auto-RIS from target effect and power, or manual in inverse-variance units.",
    tags: ["tsa", "alpha-spending", "obrien-fleming"]
  },
  {
    name: "Bayesian MA",
    folder: "bayesian-ma",
    path: "./bayesian-ma/index.html",
    collection: "new",
    mode: "file",
    category: "Evidence Synthesis",
    summary: "Conjugate normal-normal Bayesian meta-analysis: closed-form posterior for \u03b8 given studies and a normal prior; 95% CrI, P(\u03b8<c), ROPE probability, prior-sensitivity slider.",
    note: "No MCMC, no stan, no external deps. Deterministic.",
    tags: ["bayesian", "conjugate", "posterior"]
  },
  {
    name: "DTA SROC Explorer",
    folder: "dta-sroc",
    path: "./dta-sroc/index.html",
    collection: "new",
    mode: "file",
    category: "Evidence Synthesis",
    summary: "Diagnostic test accuracy: per-study Se/Sp in ROC space, Moses SROC curve, and threshold-effect flag via Spearman \u03c1 between logit(Se) and logit(1-Sp).",
    note: "Applies +0.5 continuity correction only when a cell is zero.",
    tags: ["dta", "sroc", "moses"]
  },
  {
    name: "GRADE SoF Builder",
    folder: "grade-sof",
    path: "./grade-sof/index.html",
    collection: "new",
    mode: "file",
    category: "Reporting",
    summary: "Cochrane-style Summary of Findings table: outcomes, assumed and corresponding risk, relative effect, participants, four-tier GRADE certainty.",
    note: "Print-ready standalone HTML export. JSON import/export.",
    tags: ["grade", "sof", "certainty-of-evidence"]
  },
  {
    name: "Network Meta-Analysis",
    folder: "nma",
    path: "./nma/index.html",
    collection: "new",
    mode: "file",
    category: "Evidence Synthesis",
    summary: "Contrast-based frequentist NMA: connectivity check, network graph, WLS pooling, SUCRA via 10k MC samples, league table, CSV export.",
    note: "Fixed-effect and DL random-effects; multi-arm \u03c4\u00b2/2 correction off in v1.",
    tags: ["nma", "network", "league", "sucra"]
  },
  {
    name: "WebR Validator",
    folder: "webr-validator",
    path: "./webr-validator/index.html",
    collection: "new",
    mode: "file",
    category: "Validation",
    summary: "Optional in-browser R (WebR) validation against metafor. Alternative paste-back path for local R. HMAC-SHA256 signed TruthCert receipts.",
    note: "WebR loads on explicit click (~30 MB). Signing key never stored. Constant-time verify. Accepts ?fromBus=1 for deep-link auto-load.",
    tags: ["webr", "validation", "truthcert", "hmac"]
  },
  {
    name: "SGLT2i in HFpEF Demo",
    folder: "sglt2i-hfpef-demo",
    path: "./sglt2i-hfpef-demo/index.html",
    collection: "new",
    mode: "file",
    category: "Clinical Demo",
    summary: "Real-trial benchmark: pools EMPEROR-Preserved and DELIVER on the HFpEF primary composite, compared against the Vaduganathan 2022 Lancet pool. Reproduces the workbench output side-by-side with the published HR.",
    note: "Read-only. Embeds forest-plot and heterogeneity via ?fromBus=1. Adaptive delta tolerance (0.005 aggregate / 0.02 IPD) frozen in protocol.md before compute.",
    tags: ["clinical", "sglt2i", "hfpef", "benchmark", "demo"]
  }
];
