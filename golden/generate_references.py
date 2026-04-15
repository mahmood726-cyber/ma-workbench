"""Generate golden-dataset input + reference JSONs for the MA Workbench.

Each dataset is paired with a reference file containing pooled FE/RE
estimates, tau-squared (Paule-Mandel), I-squared, Q, and 95% prediction
interval. The reference values are computed in Python using the same
estimator formulas the browser apps implement in JavaScript; a downstream
validator (either WebR or a manual pytest against the JS) must agree to
four decimal places.

Run:
    python golden/generate_references.py

Produces, per dataset:
    golden/datasets/<slug>.json      — studies + metadata + ma-studies-v1
                                        bus payload (import-compatible)
    golden/references/<slug>.json    — expected FE/RE/tau2/I2/Q/PI

The script is deterministic; datasets are hand-curated.
"""

from __future__ import annotations

import io
import json
import math
import os


# ---- Estimator implementations (mirror of the JS in forest-plot/etc) ----

def weighted_sums(studies, tau2):
    sw = 0.0
    sw2 = 0.0
    swy = 0.0
    for s in studies:
        w = 1.0 / (s["se"] ** 2 + tau2)
        sw += w
        sw2 += w * w
        swy += w * s["est"]
    mu = swy / sw if sw > 0 else 0.0
    q = 0.0
    for s in studies:
        w = 1.0 / (s["se"] ** 2 + tau2)
        q += w * (s["est"] - mu) ** 2
    return {"sw": sw, "sw2": sw2, "mu": mu, "q": q}


def tau2_pm(studies):
    k = len(studies)
    if k < 2:
        return 0.0
    target = k - 1
    q0 = weighted_sums(studies, 0.0)["q"]
    if q0 <= target:
        return 0.0
    lo, hi = 0.0, 100.0
    guard = 0
    while guard < 60 and hi < 1e9 and weighted_sums(studies, hi)["q"] > target:
        hi *= 2
        guard += 1
    for _ in range(200):
        mid = (lo + hi) / 2
        if weighted_sums(studies, mid)["q"] > target:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12:
            break
    return (lo + hi) / 2


def t_quantile_975(df: int) -> float:
    """Two-sided 95% t-critical value via lookup for small df, z for large."""
    if df <= 0:
        return math.nan
    table = {
        1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
        6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
        16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
        25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980,
    }
    if df in table:
        return table[df]
    if df > 120:
        return 1.96
    # Linear interpolate between nearest table entries
    keys = sorted(table)
    for k1, k2 in zip(keys, keys[1:]):
        if k1 <= df <= k2:
            w = (df - k1) / (k2 - k1)
            return table[k1] + w * (table[k2] - table[k1])
    return 1.96


def pool(studies):
    k = len(studies)
    if k == 0:
        return None
    tau2 = tau2_pm(studies)
    s = weighted_sums(studies, tau2)
    se = math.sqrt(1.0 / s["sw"])
    q0 = weighted_sums(studies, 0.0)["q"]
    df = k - 1
    i2 = max(0.0, 100.0 * (q0 - df) / q0) if df > 0 else 0.0
    mu = s["mu"]
    # Fixed-effect pooled (tau2 = 0)
    sf = weighted_sums(studies, 0.0)
    fe_mu = sf["mu"]
    fe_se = math.sqrt(1.0 / sf["sw"])
    # 95% prediction interval using t_{k-2}
    pi = None
    if k >= 3:
        tcrit = t_quantile_975(k - 2)
        pi_se = math.sqrt(tau2 + se * se)
        pi = [mu - tcrit * pi_se, mu + tcrit * pi_se]
    return {
        "k": k,
        "fe": {
            "estimate": round(fe_mu, 10),
            "se": round(fe_se, 10),
            "ci_lb": round(fe_mu - 1.96 * fe_se, 10),
            "ci_ub": round(fe_mu + 1.96 * fe_se, 10),
        },
        "re_pm": {
            "estimate": round(mu, 10),
            "se": round(se, 10),
            "ci_lb": round(mu - 1.96 * se, 10),
            "ci_ub": round(mu + 1.96 * se, 10),
            "tau2": round(tau2, 10),
            "i2_pct": round(i2, 6),
            "qe": round(q0, 10),
            "df": df,
            "pi_95": [round(pi[0], 10), round(pi[1], 10)] if pi else None,
        },
    }


# ---- Datasets ----

DATASETS = [
    {
        "slug": "G01-homogeneous-small",
        "title": "Homogeneous small MA (k=5, tau2 expected = 0)",
        "description": "Five studies with consistent estimates around -0.2; Q is below k-1 so tau2 should collapse to 0 under PM.",
        "effect_label": "logOR",
        "null_value": 0,
        "studies": [
            {"label": "S1", "est": -0.20, "se": 0.10},
            {"label": "S2", "est": -0.18, "se": 0.11},
            {"label": "S3", "est": -0.22, "se": 0.12},
            {"label": "S4", "est": -0.19, "se": 0.09},
            {"label": "S5", "est": -0.21, "se": 0.13},
        ],
    },
    {
        "slug": "G02-moderate-heterogeneity",
        "title": "Moderate heterogeneity (k=8)",
        "description": "Forest-plot / heterogeneity demo dataset; spread suggests non-trivial tau2.",
        "effect_label": "logOR",
        "null_value": 0,
        "studies": [
            {"label": "Trial A", "est": -0.20, "se": 0.10},
            {"label": "Trial B", "est": -0.35, "se": 0.12},
            {"label": "Trial C", "est": 0.05, "se": 0.18},
            {"label": "Trial D", "est": -0.50, "se": 0.15},
            {"label": "Trial E", "est": 0.12, "se": 0.11},
            {"label": "Trial F", "est": -0.28, "se": 0.09},
            {"label": "Trial G", "est": -0.10, "se": 0.14},
            {"label": "Trial H", "est": -0.45, "se": 0.20},
        ],
    },
    {
        "slug": "G03-high-heterogeneity",
        "title": "High heterogeneity (k=10, I^2 > 80%)",
        "description": "Large between-study variance; tau2 should be substantial and PI wide.",
        "effect_label": "SMD",
        "null_value": 0,
        "studies": [
            {"label": "A", "est": 0.80, "se": 0.15},
            {"label": "B", "est": -0.20, "se": 0.18},
            {"label": "C", "est": 1.10, "se": 0.22},
            {"label": "D", "est": 0.10, "se": 0.16},
            {"label": "E", "est": -0.60, "se": 0.14},
            {"label": "F", "est": 0.95, "se": 0.19},
            {"label": "G", "est": 0.05, "se": 0.17},
            {"label": "H", "est": 1.25, "se": 0.21},
            {"label": "I", "est": -0.35, "se": 0.20},
            {"label": "J", "est": 0.40, "se": 0.15},
        ],
    },
    {
        "slug": "G04-large-trial-dominance",
        "title": "Large trial dominance (k=6)",
        "description": "One very large (low-SE) trial dominates FE pooling; RE weighting is less extreme.",
        "effect_label": "logRR",
        "null_value": 0,
        "studies": [
            {"label": "Small 1", "est": -0.50, "se": 0.30},
            {"label": "Small 2", "est": -0.42, "se": 0.28},
            {"label": "Small 3", "est": -0.60, "se": 0.32},
            {"label": "Mid", "est": -0.25, "se": 0.15},
            {"label": "Large 1", "est": -0.12, "se": 0.05},
            {"label": "Large 2", "est": -0.10, "se": 0.04},
        ],
    },
    {
        "slug": "G05-null-crossing",
        "title": "Null-crossing pooled estimate (k=7)",
        "description": "Balanced positive + negative effects; pooled estimate near zero.",
        "effect_label": "MD",
        "null_value": 0,
        "studies": [
            {"label": "P1", "est": 0.30, "se": 0.14},
            {"label": "P2", "est": -0.25, "se": 0.15},
            {"label": "P3", "est": 0.10, "se": 0.12},
            {"label": "P4", "est": -0.15, "se": 0.13},
            {"label": "P5", "est": 0.05, "se": 0.10},
            {"label": "P6", "est": 0.20, "se": 0.11},
            {"label": "P7", "est": -0.05, "se": 0.09},
        ],
    },
    {
        "slug": "G06-sglt2i-hfpef-benchmark",
        "title": "SGLT2i in HFpEF: EMPEROR-Preserved + DELIVER primary composite pool (k=2)",
        "description": "Real-trial 2-study pool. Pooling HR 0.79 and HR 0.82 on log-HR scale; expected REML HR ~0.80, tau2 ~0, I2 ~0, Q small. Benchmark reproduction target with adaptive delta (0.02 IPD / 0.005 aggregate) per protocol.md.",
        "effect_label": "logHR",
        "null_value": 0,
        "studies": [
            {"label": "EMPEROR-Preserved", "est": -0.2357, "se": 0.0678},
            {"label": "DELIVER", "est": -0.1985, "se": 0.0590},
        ],
    },
]


def r_script(ds):
    yi = ", ".join(f"{s['est']:.6f}" for s in ds["studies"])
    sei = ", ".join(f"{s['se']:.6f}" for s in ds["studies"])
    labs = ", ".join('"' + s["label"].replace('"', '\\"') + '"' for s in ds["studies"])
    return "\n".join([
        f"# {ds['slug']} — {ds['title']}",
        "library(metafor)",
        f"yi  <- c({yi})",
        f"sei <- c({sei})",
        f"slab <- c({labs})",
        'fe <- rma(yi, sei = sei, method = "FE", slab = slab)',
        'pm <- rma(yi, sei = sei, method = "PM", slab = slab)',
        "cat(sprintf(",
        '  "fe.estimate=%.10f\\nfe.se=%.10f\\n',
        '   pm.estimate=%.10f\\npm.se=%.10f\\npm.tau2=%.10f\\npm.I2=%.10f\\npm.QE=%.10f\\n",',
        "  as.numeric(fe$b), as.numeric(fe$se),",
        "  as.numeric(pm$b), as.numeric(pm$se),",
        "  as.numeric(pm$tau2), as.numeric(pm$I2), as.numeric(pm$QE)))",
    ])


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    ds_dir = os.path.join(root, "datasets")
    ref_dir = os.path.join(root, "references")
    os.makedirs(ds_dir, exist_ok=True)
    os.makedirs(ref_dir, exist_ok=True)
    summary = []
    # Deterministic marker: git commit is authoritative for provenance,
    # so the JSON itself carries no runtime timestamp (keeps the CI
    # byte-for-byte regeneration check green).
    FROZEN_MARKER = "deterministic"
    for ds in DATASETS:
        # Bus-compatible dataset payload
        bus_payload = {
            "_schema": "ma-studies-v1",
            "_savedAt": FROZEN_MARKER,
            "studies": [
                {"label": s["label"], "est": s["est"], "se": s["se"],
                 "moderator": None, "group": None, "year": None}
                for s in ds["studies"]
            ],
        }
        ds_file = os.path.join(ds_dir, ds["slug"] + ".json")
        with io.open(ds_file, "w", encoding="utf-8") as fh:
            json.dump({
                "slug": ds["slug"],
                "title": ds["title"],
                "description": ds["description"],
                "effect_label": ds["effect_label"],
                "null_value": ds["null_value"],
                "bus_payload": bus_payload,
                "r_script": r_script(ds),
            }, fh, indent=2)

        ref = pool(ds["studies"])
        ref_file = os.path.join(ref_dir, ds["slug"] + ".json")
        with io.open(ref_file, "w", encoding="utf-8") as fh:
            json.dump({
                "slug": ds["slug"],
                "title": ds["title"],
                "generator": "golden/generate_references.py",
                "tolerance": 1e-4,
                "reference": ref,
                "note": "Computed in Python using the same Paule-Mandel bisection and IV pooling formulas the browser apps implement in JavaScript. Browser and R outputs must match these values to within tolerance. Deterministic — provenance is the git commit SHA, not a timestamp.",
            }, fh, indent=2)
        summary.append({"slug": ds["slug"], "k": ref["k"],
                        "fe_mu": ref["fe"]["estimate"], "pm_mu": ref["re_pm"]["estimate"],
                        "pm_tau2": ref["re_pm"]["tau2"], "pm_i2_pct": ref["re_pm"]["i2_pct"]})
        print(f"  {ds['slug']:<28}  k={ref['k']}  FE={ref['fe']['estimate']:+.4f}  PM={ref['re_pm']['estimate']:+.4f}  tau2={ref['re_pm']['tau2']:.4f}  I2={ref['re_pm']['i2_pct']:.1f}%")

    # G07 is an MC experiment, not a study-pooling dataset. Its dataset
    # file is hand-committed (mc_inputs schema, not `studies`), and its
    # reference is computed by the precision_sweep.simulate module.
    mc_count = generate_mc_references(root, summary)

    # summary index — also deterministic
    with io.open(os.path.join(root, "SUMMARY.json"), "w", encoding="utf-8") as fh:
        json.dump({"datasets": summary}, fh, indent=2)
    print(f"\nWrote {len(DATASETS) + mc_count} dataset + reference pairs to golden/")


def generate_mc_references(root, summary):
    """Regenerate Monte Carlo references (G07+).

    MC datasets have an `mc_inputs` block instead of `studies`. The
    dataset file itself is hand-committed and NOT rewritten here; only
    the reference file is regenerated deterministically.
    """
    ds_dir = os.path.join(root, "datasets")
    ref_dir = os.path.join(root, "references")
    count = 0
    for slug in ("G07-precision-sweep",):
        ds_file = os.path.join(ds_dir, slug + ".json")
        if not os.path.exists(ds_file):
            continue
        with io.open(ds_file, "r", encoding="utf-8") as fh:
            ds = json.load(fh)
        mc = ds["mc_inputs"]
        # Lazy import so G01-G06 regeneration does not need precision_sweep.
        import sys
        sys.path.insert(0, os.path.dirname(root))
        from precision_sweep.simulate import run_simulation
        result = run_simulation(
            seed=mc["seed"],
            n_replications=mc["n_replications"],
            true_hr_range=tuple(mc["true_hr_range"]),
            se_range=tuple(mc["se_range"]),
            dp_levels=mc["dp_levels"],
        )
        ref_file = os.path.join(ref_dir, slug + ".json")
        with io.open(ref_file, "w", encoding="utf-8") as fh:
            json.dump({
                "slug": slug,
                "title": ds["title"],
                "generator": "golden/generate_references.py via precision_sweep.simulate",
                "tolerance": 1e-6,
                "reference": result,
                "note": "Monte Carlo reference. Seed + generator + N + ranges + dp_levels are frozen in the dataset file. Browser client-side MC must match these values to within 1e-4 on median (per-dp).",
            }, fh, indent=2)
        summary.append({
            "slug": slug,
            "is_mc": True,
            "seed": mc["seed"],
            "n_replications": mc["n_replications"],
            "dp_medians": {
                dp: result["per_dp"][str(dp)]["median"]
                for dp in mc["dp_levels"]
            },
        })
        medians = " ".join(
            f"dp{dp}={result['per_dp'][str(dp)]['median']:.6f}"
            for dp in mc["dp_levels"]
        )
        print(f"  {slug:<28}  MC  {medians}")
        count += 1
    return count


if __name__ == "__main__":
    main()
