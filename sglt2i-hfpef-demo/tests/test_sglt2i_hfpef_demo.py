"""Per-app smoke tests for the SGLT2i-HFpEF demo page.

Verifies static HTML structure and that the two required JSON inputs
parse. Runtime behaviour (claim card, panels, embedded apps) is covered
by tests/test_sglt2i_benchmark.py at repo level.
"""

import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DATA = ROOT / "data.json"
EXPECTED = ROOT / "expected.json"

FORBIDDEN = ("{{", "}}", "REPLACE_ME", "__PLACEHOLDER__", "TODO:", "TBD:")


class TagCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.opens = {}
        self.closes = {}

    def handle_starttag(self, tag, attrs):
        self.opens[tag] = self.opens.get(tag, 0) + 1

    def handle_endtag(self, tag):
        self.closes[tag] = self.closes.get(tag, 0) + 1


def test_index_exists():
    assert INDEX.exists(), f"{INDEX} missing"


def test_data_parses():
    json.loads(DATA.read_text(encoding="utf-8"))


def test_expected_parses():
    json.loads(EXPECTED.read_text(encoding="utf-8"))


def test_no_placeholders():
    text = INDEX.read_text(encoding="utf-8")
    for token in FORBIDDEN:
        assert token not in text, f"placeholder {token!r} present in index.html"


def test_div_balance():
    text = INDEX.read_text(encoding="utf-8")
    opens = len(re.findall(r"<div[\s>]", text))
    closes = len(re.findall(r"</div>", text))
    assert opens == closes, f"<div> {opens} != </div> {closes}"


def test_required_section_ids_present():
    text = INDEX.read_text(encoding="utf-8")
    for id_ in (
        "claim-card", "forest-host", "method-table", "method-body",
        "hetero-host", "not-computed-section", "provenance",
        "bench-hr", "our-hr", "delta", "verdict",
    ):
        assert f'id="{id_}"' in text, f"id={id_!r} not found in index.html"


def test_not_computed_cards_have_data_card_attrs():
    text = INDEX.read_text(encoding="utf-8")
    for card in ("prediction-interval", "funnel", "trim-and-fill", "tsa"):
        assert f'data-card="{card}"' in text, f"data-card={card!r} missing"


def test_no_external_cdn_scripts():
    """Demo page must be offline (no external CDN, per html-apps.md)."""
    text = INDEX.read_text(encoding="utf-8")
    assert "cdn." not in text.lower(), "external CDN script reference found"
    assert "https://" not in re.sub(r"DOI", "", text), (
        "absolute https:// URL in shipped page"
    )
