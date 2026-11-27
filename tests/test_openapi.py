from __future__ import annotations

from pathlib import Path

import yaml

from conftest import load_json


def test_openapi_core_paths(root: Path) -> None:
    path = root / "schemas" / "openapi" / "jcheng-gateway.v1.yaml"
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert spec["openapi"] == "3.1.0"
    for required in (
        "/v1/state",
        "/v1/safety",
        "/v1/leases",
        "/v1/motion/validate",
        "/v1/motion/execute",
        "/v1/motion/stop",
    ):
        assert required in spec["paths"]
    for forbidden in ("servo", "register", "eeprom", "set_position", "motor"):
        assert all(forbidden not in item for item in spec["paths"])


def test_stop_response_confirmation_fields(root: Path) -> None:
    path = root / "schemas" / "openapi" / "jcheng-gateway.v1.yaml"
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    stop = spec["components"]["schemas"]["StopResponse"]
    assert set(stop["required"]) == {
        "accepted",
        "safety",
        "confirmation",
        "physical_stop",
    }
    assert stop["properties"]["confirmation"]["enum"] == [
        "request_accepted",
        "backend_confirmed",
    ]
    assert stop["properties"]["physical_stop"]["const"] == "unverified"
    assert stop["properties"]["requested_at"]["format"] == "date-time"


def test_ws_schema_references_messages(root: Path) -> None:
    path = root / "schemas" / "ws" / "jcheng-ws.v1.json"
    ws = load_json(path)
    assert ws["properties"]["v"]["const"] == 1
    refs = str(ws["properties"]["payload"])
    assert "messages.v1.schema.json" in refs
