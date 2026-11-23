#!/usr/bin/env python3
"""Validate JSON Schemas, OpenAPI, WebSocket and the error registry."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from jcheng_contracts.errors import CANONICAL_CODES, load_mapping, load_registry
from jcheng_contracts.validate import check_schema


def main() -> int:
    problems: list[str] = []
    schemas = sorted((ROOT / "schemas").glob("*.schema.json"))
    for path in schemas:
        try:
            check_schema(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:  # noqa: BLE001 - report all schema errors
            problems.append(f"{path.relative_to(ROOT)}: {exc}")

    try:
        import yaml  # type: ignore
    except ImportError:
        problems.append("PyYAML is required to validate OpenAPI")
        yaml = None
    if yaml is not None:
        openapi_path = ROOT / "schemas" / "openapi" / "jcheng-gateway.v1.yaml"
        try:
            spec = yaml.safe_load(openapi_path.read_text(encoding="utf-8"))
            if spec.get("openapi") != "3.1.0":
                problems.append("OpenAPI: expected openapi 3.1.0")
            for required in ("/v1/state", "/v1/safety", "/v1/leases", "/v1/motion/validate", "/v1/motion/execute", "/v1/motion/stop"):
                if required not in spec.get("paths", {}):
                    problems.append(f"OpenAPI: missing path {required}")
            forbidden = ("servo", "register", "eeprom", "set_position", "motor")
            for path in spec.get("paths", {}):
                for token in forbidden:
                    if token in path:
                        problems.append(f"OpenAPI: forbidden hardware path {path}")
        except Exception as exc:  # noqa: BLE001
            problems.append(f"OpenAPI: {exc}")

    ws_path = ROOT / "schemas" / "ws" / "jcheng-ws.v1.json"
    try:
        ws = json.loads(ws_path.read_text(encoding="utf-8"))
        check_schema(ws)
    except Exception as exc:  # noqa: BLE001
        problems.append(f"WebSocket schema: {exc}")

    try:
        registry = load_registry(ROOT)
        codes = registry.get("codes", {})
        if set(codes) != set(CANONICAL_CODES):
            problems.append("error registry and ErrorCode enum differ")
        mapping = load_mapping(ROOT)
        for legacy, target in mapping.items():
            if target not in codes:
                problems.append(f"error mapping {legacy} -> unknown target {target}")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"error registry: {exc}")

    if problems:
        print("schema checks failed:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    print(f"schema checks OK: {len(schemas)} schemas, {len(CANONICAL_CODES)} error codes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
