"""Contract tests for the precision-sweep E156 paper."""
import json
import re
from pathlib import Path

PAPER_MD = Path("e156-submission-precision-sweep/paper.md")
PAPER_JSON = Path("e156-submission-precision-sweep/paper.json")
G07_REF = Path("golden/references/G07-precision-sweep.json")


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def test_paper_md_exists():
    assert PAPER_MD.exists()


def test_seven_sentences():
    data = load(PAPER_JSON)
    assert len(data["sentences"]) == 7
    for key in ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]:
        assert key in data["sentences"]


def test_word_count_under_156():
    data = load(PAPER_JSON)
    body = " ".join(
        data["sentences"][k]
        for k in ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]
    )
    words = re.findall(r"\S+", body)
    assert len(words) <= 156, f"{len(words)} > 156"


def test_no_unfilled_braces():
    text = PAPER_MD.read_text(encoding="utf-8")
    assert "{{" not in text, "unfilled {{braces}} in paper.md"


def test_s4_contains_dp_2_median():
    """S4 must quote the dp=2 median |Δ| to 4 dp."""
    paper = load(PAPER_JSON)
    ref = load(G07_REF)
    m2 = ref["reference"]["per_dp"]["2"]["median"]
    needle = f"{m2:.4f}"
    assert needle in paper["sentences"]["S4"], (
        f"S4 does not contain dp=2 median {needle}: "
        f"{paper['sentences']['S4']}"
    )


def test_sglt2i_consistency_claim_matches_data():
    """SGLT2i observed |Δ|=0.007 at dp=2 must be at or below MC max at dp=2.

    This closes the loop between the two E156 papers: the prior FAIL
    outcome is not an implementation bug but precision-bound behaviour
    inside the MC envelope.
    """
    ref = load(G07_REF)
    max_2 = ref["reference"]["per_dp"]["2"]["max"]
    assert 0.007 <= max_2, (
        f"SGLT2i observed |Δ|=0.007 exceeds the MC max at dp=2 ({max_2}); "
        "this would indicate an implementation bug in the prior paper"
    )
