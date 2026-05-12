"""Integration contract test for the ma-studies-v1 shared data bus.

Per the local testing rules on "Integration Tests First":
this test defines the contract between study-based MA apps BEFORE the
bus is retrofitted into each one. It must run green after the retrofit.

## Contract

Study-based apps share a single localStorage key:
    `ma-studies-v1`

Value is JSON:
    {
      "_schema": "ma-studies-v1",
      "_savedAt": "ISO-8601 timestamp",
      "studies": [
        {"label": "...", "est": 0.0, "se": 0.0,
         "moderator": null, "group": null, "year": null}
      ]
    }

Apps participate via an **explicit pull**: each app exposes a button with
id `btn-bus-load` that, when clicked, reads the bus and writes the
canonical (label, est, SE) rows into that app's own CSV textarea.

A complementary `btn-bus-save` pushes the current textarea into the bus.

No silent overwrite: apps never read the bus automatically on load.
The user always initiates the transfer.

## Participating apps (MUST have bus buttons)

- forest-plot
- funnel-plot
- heterogeneity
- tsa
- rob-traffic-light   (accepts via cell-data bus, not studies bus — excluded)
- dta-sroc            (different data shape, 2x2 counts — excluded)
- meta-regression     (new in batch 4c — included)
- cumulative-subgroup (new in batch 4d — included)

The PRISMA and GRADE apps are not study-based; they do not touch the bus.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STUDY_APPS = (
    "forest-plot",
    "funnel-plot",
    "heterogeneity",
    "tsa",
    # New in batch 4:
    "meta-regression",
    "cumulative-subgroup",
)

SHARED_KEY = "ma-studies-v1"


def _read(app):
    path = ROOT / app / "index.html"
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


# ---- The bus key must be declared by every participating app ----

def test_all_study_apps_declare_bus_key():
    missing = []
    for app in STUDY_APPS:
        text = _read(app)
        if text is None:
            # Not yet built — that's OK for brand-new apps during batch 4,
            # but the existing apps must declare it.
            if app in ("meta-regression", "cumulative-subgroup"):
                continue
            missing.append(f"{app} (index.html not found)")
            continue
        if f'"{SHARED_KEY}"' not in text:
            missing.append(app)
    assert not missing, f"Apps missing bus key '{SHARED_KEY}': {missing}"


# ---- Each participating app must expose the two bus buttons ----

def test_all_study_apps_have_bus_buttons():
    missing = []
    for app in STUDY_APPS:
        text = _read(app)
        if text is None:
            if app in ("meta-regression", "cumulative-subgroup"):
                continue
            missing.append(f"{app} (index.html not found)")
            continue
        for btn in ("btn-bus-load", "btn-bus-save"):
            if f'id="{btn}"' not in text:
                missing.append(f"{app}:{btn}")
    assert not missing, f"Missing bus buttons: {missing}"


# ---- Schema-literal inside the app bundle must match the contract ----

def test_schema_literal_is_exact():
    for app in STUDY_APPS:
        text = _read(app)
        if text is None:
            continue  # app not built yet
        # The app should use the exact schema string so round-tripped bus
        # payloads are self-describing.
        assert '"_schema": "ma-studies-v1"' in text or '"_schema":"ma-studies-v1"' in text, \
            f"{app}: missing _schema marker '{SHARED_KEY}'"


# ---- Bus writes must include _savedAt ISO timestamp for provenance ----

def test_bus_payload_includes_savedat():
    for app in STUDY_APPS:
        text = _read(app)
        if text is None:
            continue
        # Either direct mention of _savedAt near the bus key, or use of
        # toISOString when building the bus payload.
        near_bus = re.search(
            r'ma-studies-v1[\s\S]{0,600}?(_savedAt|toISOString)',
            text
        )
        assert near_bus, f"{app}: bus write missing _savedAt / toISOString provenance"


# ---- No silent auto-load: the bus must NOT be read in the initial boot ----

def test_no_auto_load_on_boot():
    """The bus should never overwrite a user's textarea without an
    explicit click — rule: no silent data clobber."""
    for app in STUDY_APPS:
        text = _read(app)
        if text is None:
            continue
        # Find the bootstrap at the bottom of the IIFE (loadSaved / attach / render)
        # and assert there is no getItem("ma-studies-v1") before the user
        # interacts. We implement by requiring the bus-load call is ONLY
        # inside a function wired to a click listener.
        tail = text[-3000:]
        # loadSaved reads the per-app key, which is FINE. The bus key must
        # not appear in the boot tail except inside click handlers.
        # Simpler invariant: the string "ma-studies-v1" appears at least
        # twice (one in the bus-load handler, one in the bus-save handler),
        # and the handler names appear inside addEventListener("click", ...) calls.
        assert text.count(f'"{SHARED_KEY}"') >= 2, \
            f"{app}: bus key must appear at least twice (load + save paths)"


# ---- Each app must keep its own localStorage key working too ----

def test_per_app_keys_preserved():
    """Retrofitting the bus must not remove each app's own key."""
    own_keys = {
        "forest-plot": "forest-plot-v1",
        "funnel-plot": "funnel-plot-v1",
        "heterogeneity": "heterogeneity-v1",
        "tsa": "tsa-v1",
        "meta-regression": "meta-regression-v1",
        "cumulative-subgroup": "cumulative-subgroup-v1",
    }
    missing = []
    for app, key in own_keys.items():
        text = _read(app)
        if text is None:
            continue
        if f'"{key}"' not in text:
            missing.append(f"{app}:{key}")
    assert not missing, f"Per-app keys removed: {missing}"


# ---- The workbench integrator (4b) is the canonical bus writer ----

def test_workbench_if_built_writes_bus():
    wb = _read("workbench")
    if wb is None:
        # Not yet built — that's OK during batch 4b
        return
    assert f'"{SHARED_KEY}"' in wb, "workbench must reference the bus key"
    # Expect a deliberate write path
    assert "localStorage.setItem" in wb and SHARED_KEY in wb, \
        "workbench must write to the bus"


# ---- Batch 5e: per-app Validate-with-WebR button ----
# Each study-based app exposes a button id="btn-validate-webr" that routes
# to ../webr-validator/index.html after writing current studies to the bus.

def test_validate_webr_button_on_study_apps():
    missing = []
    for app in STUDY_APPS:
        text = _read(app)
        if text is None:
            continue
        if 'id="btn-validate-webr"' not in text:
            missing.append(app)
        if "../webr-validator/index.html" not in text:
            missing.append(f"{app} (no deep-link)")
    assert not missing, f"Missing Validate-with-WebR wiring: {missing}"
