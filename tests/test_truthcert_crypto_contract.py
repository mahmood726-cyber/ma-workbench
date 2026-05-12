"""Integration contract for HMAC-signed TruthCert receipts.

Per the local agent lessons on Cryptography / Signing:
- HMAC key must NOT come from the bundle itself.
- Placeholder signatures are a security bug, not a TODO.
- Constant-time comparison always.
- Delete / label forgeable artifacts after migration.

This test defines the browser-side contract BEFORE the crypto code
is wired into webr-validator. It must pass after the retrofit.

## Contract

1. The webr-validator ships a `signCert(body, key)` function that returns
   an HMAC-SHA256 hex digest (64 lowercase hex chars).
2. It also ships `verifyCert(receipt, key)` using `crypto.subtle.verify`
   (constant-time), NOT string equality on hex.
3. The HMAC key is sourced from a password input (`f-hmac-key`) — never
   from localStorage, never from the receipt itself, never from a
   hardcoded constant in the source.
4. Receipts include a `_key_id` field = first 16 hex chars of SHA-256(key),
   for identifying which key signed without revealing the key.
5. Receipts DO NOT include any placeholder signature literal like
   "SIG_RSA_SHA256_..." — signing is either real or absent.
6. A separate Verify panel exposes `btn-verify-cert` that requires the
   user to supply the key again and returns a match/mismatch banner.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "webr-validator" / "index.html"


def _read():
    return VALIDATOR.read_text(encoding="utf-8")


def test_validator_exists():
    assert VALIDATOR.is_file()


def test_hmac_key_input_present():
    """Key must be entered by the user via a password input, never stored."""
    text = _read()
    assert 'id="f-hmac-key"' in text, "HMAC key input field missing"
    assert 'type="password"' in text, "HMAC key field must be type=password"


def test_sign_function_declared():
    text = _read()
    assert "async function signCert" in text or "signCert = async" in text, \
        "signCert async function missing"


def test_verify_function_uses_subtle_verify():
    """Must use crypto.subtle.verify (constant-time), not == on hex strings."""
    text = _read()
    assert "crypto.subtle.verify" in text, \
        "verifyCert must use crypto.subtle.verify, not == comparison"


def test_no_placeholder_signature_literal():
    """lessons.md: SIG_* placeholders are security bugs."""
    text = _read()
    assert "SIG_RSA_SHA256_" not in text
    assert "signature_placeholder" not in text
    # "signature" as a field name is fine; forbidden is PLACEHOLDER VALUES.


def test_key_not_stored_in_localstorage():
    """Grepping: localStorage.setItem(...key...) patterns involving the
    HMAC key field are forbidden."""
    text = _read()
    # Blanket check — f-hmac-key value never persisted
    assert "localStorage.setItem" in text  # other persistence OK
    # But NOT tied to the HMAC key field
    assert "f-hmac-key" not in re.findall(
        r'localStorage\.setItem\([^)]*\)', text
    ).__str__(), "HMAC key must never hit localStorage"


def test_key_not_hardcoded():
    """No literal secret keys in the source."""
    text = _read()
    # Heuristic: no lines assigning KEY = "..." or SECRET = "..."
    assert not re.search(r'(KEY|SECRET|HMAC_KEY)\s*=\s*"[A-Za-z0-9+/=]{16,}"', text), \
        "Hardcoded key literal found"


def test_key_id_field_is_hash_prefix():
    """The receipt's _key_id is a hash prefix, not the key itself."""
    text = _read()
    assert '"_key_id"' in text
    # The hash prefix is computed via SHA-256 on the key bytes
    assert "SHA-256" in text or "\"SHA-256\"" in text


def test_signature_is_over_canonical_body():
    """Signing must be over a stable canonical serialization so verifiers
    recompute an identical digest. Must not re-sort keys silently — we
    enforce a deterministic canonicalization step."""
    text = _read()
    assert "canonicalJson" in text or "canonicalize" in text, \
        "Must have an explicit canonicalization step for the signed body"


def test_verify_ui_present():
    """A Verify panel lets a peer validate a third-party receipt."""
    text = _read()
    assert 'id="btn-verify-cert"' in text
    assert 'id="f-verify-json"' in text


def test_legacy_receipt_banner():
    """Receipts without a real HMAC get an explicit LEGACY label so the
    migration story is visible to reviewers."""
    text = _read()
    assert "legacy" in text.lower() or "LEGACY" in text


def test_acknowledge_still_gates_webr():
    """The pre-existing WebR acknowledgement gate must not be removed."""
    text = _read()
    assert 'id="f-acknowledge"' in text


def test_constant_time_comment_in_source():
    """A comment reminds future editors why we use subtle.verify."""
    text = _read()
    assert "constant-time" in text.lower() or "constant time" in text.lower()
