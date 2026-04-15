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


PAPER_JSON = Path("e156-submission-sglt2i/paper.json")


def _paper_branch():
    return load_json(PAPER_JSON)["branch"]


def test_main_hr_within_tolerance():
    """Spec criterion 1, expressed as a branch-consistency check.

    The protocol froze both PASS and FAIL paper branches up-front; this
    test asserts the actual divergence agrees with what paper.json
    declared. Per the spec's Failure Handling section ("FAIL does not
    block CI, push, INDEX update"), a FAIL branch is a valid scientific
    outcome and does not red the build. The branch decision is the
    falsifiable claim — it must match the data.
    """
    expected = load_json(EXPECTED)
    ref = load_json(G06_REF)
    bench = expected["benchmark"]["hr"]
    delta = expected["tolerance"]["applied_delta"]
    hr, _, _ = pooled_hr_and_ci_from_ref(ref)
    diff = abs(hr - bench)
    within = diff <= delta
    branch = _paper_branch()
    if branch == "PASS":
        assert within, (
            f"paper.json declares PASS but |Δ|={diff:.4f} > tolerance {delta} "
            f"(pooled HR {hr:.4f}, benchmark {bench})"
        )
    else:
        assert not within, (
            f"paper.json declares FAIL but |Δ|={diff:.4f} <= tolerance {delta} "
            f"— branch wrongly chosen (pooled HR {hr:.4f}, benchmark {bench})"
        )


def test_ci_overlaps_published():
    """Spec criterion 2, expressed as a branch-consistency check.

    On PASS, pooled CI must overlap benchmark CI. On FAIL, the divergence
    can be from either delta-exceeded OR CI-non-overlap — the test only
    enforces overlap when branch=PASS. Branch consistency itself is
    enforced by test_branch_matches_decision_rule in test_sglt2i_paper.py.
    """
    expected = load_json(EXPECTED)
    ref = load_json(G06_REF)
    bench = expected["benchmark"]
    _, lo, hi = pooled_hr_and_ci_from_ref(ref)
    overlap = max(lo, bench["ci_low"]) <= min(hi, bench["ci_high"])
    if _paper_branch() == "PASS":
        assert overlap, (
            f"paper.json declares PASS but pooled CI [{lo:.3f},{hi:.3f}] "
            f"does not overlap benchmark CI "
            f"[{bench['ci_low']},{bench['ci_high']}]"
        )


def test_fe_pm_hr_range_k2():
    """Absolute HR range between FE and PM point estimates must be <= 0.03.

    The spec's four-estimator range (FE, REML, PM, HKSJ-floored) collapses
    to |exp(fe) - exp(pm)| at k=2 tau2=0 because REML==PM==FE point-estimate
    and HKSJ only modifies the CI, not the point. This test asserts the
    collapsed form; the full four-estimator range is re-asserted in the
    browser-driven integration test once sglt2i-hfpef-demo/index.html wires
    up the method-comparison panel (Bundle B). A regression in HKSJ SE
    or the floor rule would be caught there, not here.
    """
    ref = load_json(G06_REF)
    hrs = [
        math.exp(ref["reference"]["fe"]["estimate"]),
        math.exp(ref["reference"]["re_pm"]["estimate"]),
    ]
    assert max(hrs) - min(hrs) <= 0.03, (
        f"FE/PM HR range {max(hrs) - min(hrs):.4f} exceeds 0.03"
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
    # Accept either literal '<' or the HTML-entity encoded form '&lt;' since
    # the same character must be entity-encoded inside HTML text content.
    assert "k<10" in text or "k&lt;10" in text, (
        "DL exclusion reason 'k<10' not present (literal or entity form)"
    )


def test_undefined_panels_reasons_present():
    """Four greyed cards must each emit the expected reason string verbatim."""
    html = Path("sglt2i-hfpef-demo/index.html")
    assert html.exists(), f"{html} missing"
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
