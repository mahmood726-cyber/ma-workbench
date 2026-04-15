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
    for s_key in ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]:
        assert s_key in data["sentences"]


def test_word_count_under_156():
    data = json.loads(PAPER_JSON.read_text(encoding="utf-8"))
    joined = " ".join(
        data["sentences"][k] for k in ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]
    )
    words = re.findall(r"\S+", joined)
    assert len(words) <= 156, f"{len(words)} > 156"


def test_no_unfilled_braces():
    text = PAPER_MD.read_text(encoding="utf-8")
    assert "{{" not in text, "unfilled {{braces}} in paper.md"


def test_s4_hr_matches_computed():
    data = json.loads(PAPER_JSON.read_text(encoding="utf-8"))
    ref = json.loads(G06_REF.read_text(encoding="utf-8"))
    hr = math.exp(ref["reference"]["re_pm"]["estimate"])
    needle = f"{hr:.2f}"
    assert needle in data["sentences"]["S4"], (
        f"S4 does not contain computed HR {needle}: {data['sentences']['S4']}"
    )


def test_branch_matches_decision_rule():
    """If pooled HR is within applied_delta and CI overlaps, branch is PASS;
    otherwise FAIL. paper.json.branch must agree with this rule."""
    paper = json.loads(PAPER_JSON.read_text(encoding="utf-8"))
    ref = json.loads(G06_REF.read_text(encoding="utf-8"))
    expected = json.loads(
        Path("sglt2i-hfpef-demo/expected.json").read_text(encoding="utf-8")
    )
    hr = math.exp(ref["reference"]["re_pm"]["estimate"])
    se = ref["reference"]["re_pm"]["se"]
    lo = math.exp(ref["reference"]["re_pm"]["estimate"] - 1.96 * se)
    hi = math.exp(ref["reference"]["re_pm"]["estimate"] + 1.96 * se)
    bench = expected["benchmark"]
    delta = abs(hr - bench["hr"])
    tol = expected["tolerance"]["applied_delta"]
    ci_overlap = max(lo, bench["ci_low"]) <= min(hi, bench["ci_high"])
    expected_branch = "PASS" if (delta <= tol and ci_overlap) else "FAIL"
    assert paper["branch"] == expected_branch, (
        f"paper.json branch={paper['branch']!r} but rule says {expected_branch!r}"
    )
