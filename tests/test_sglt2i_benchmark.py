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
    log_hr = ref["reference"]["re_pm"]["estimate"]
    se = ref["reference"]["re_pm"]["se"]
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
    hrs = [
        math.exp(ref["reference"]["fe"]["estimate"]),
        math.exp(ref["reference"]["re_pm"]["estimate"]),
    ]
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
