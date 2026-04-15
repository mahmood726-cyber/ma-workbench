"""Per-app smoke tests for the precision-sweep demo page."""
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DATA = ROOT / "data.json"
XOSHIRO_JS = ROOT / "xoshiro.js"
SIMULATE_JS = ROOT / "simulate.js"

FORBIDDEN = ("{{", "}}", "REPLACE_ME", "__PLACEHOLDER__", "TODO:", "TBD:")


def test_files_exist():
    for p in (INDEX, DATA, XOSHIRO_JS, SIMULATE_JS):
        assert p.exists(), f"{p} missing"


def test_data_parses():
    json.loads(DATA.read_text(encoding="utf-8"))


def test_no_placeholders():
    text = INDEX.read_text(encoding="utf-8")
    for token in FORBIDDEN:
        assert token not in text, f"placeholder {token!r} present"


def test_div_balance():
    text = INDEX.read_text(encoding="utf-8")
    opens = len(re.findall(r"<div[\s>]", text))
    closes = len(re.findall(r"</div>", text))
    assert opens == closes, f"<div> {opens} != </div> {closes}"


def test_no_external_cdn():
    text = INDEX.read_text(encoding="utf-8")
    assert "cdn." not in text.lower(), "external CDN reference found"


def test_no_date_now():
    text = INDEX.read_text(encoding="utf-8")
    assert "Date.now" not in text
    assert "new Date" not in text


def test_xoshiro_imported_before_simulate():
    text = INDEX.read_text(encoding="utf-8")
    xi = text.find('src="xoshiro.js"')
    si = text.find('src="simulate.js"')
    assert xi > 0 and si > xi, "xoshiro.js must load before simulate.js"


def test_claim_card_present():
    text = INDEX.read_text(encoding="utf-8")
    assert 'id="claim-card"' in text
    assert 'id="claim-median"' in text
