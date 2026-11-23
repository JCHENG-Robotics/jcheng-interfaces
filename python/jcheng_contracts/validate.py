"""JSON Schema validation helpers (optional jsonschema dependency)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _jsonschema():
    try:
        import jsonschema  # type: ignore
    except ImportError as exc:  # pragma: no cover - CI installs jsonschema
        raise RuntimeError("jsonschema is required for schema validation") from exc
    return jsonschema


def check_schema(schema: dict[str, Any]) -> None:
    """Raise if a JSON Schema is not a valid Draft 2020-12 schema."""
    jsonschema = _jsonschema()
    jsonschema.Draft202012Validator.check_schema(schema)


def validate_instance(instance: Any, schema: dict[str, Any]) -> None:
    """Validate an instance, raising ``ValueError`` with sorted messages."""
    check_schema(schema)
    jsonschema = _jsonschema()
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        messages = [
            f"{'/'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
            for error in errors
        ]
        raise ValueError("; ".join(messages))


def messages_schema(root: str | Path) -> dict[str, Any]:
    return load_json(Path(root) / "schemas" / "messages.v1.schema.json")


def validate_message(name: str, instance: dict[str, Any], root: str | Path) -> None:
    """Validate against ``$defs/<name>`` in the messages schema."""
    root_schema = messages_schema(root)
    defs = root_schema.get("$defs", {})
    if name not in defs:
        raise KeyError(f"unknown message definition: {name}")
    schema = {
        "$schema": root_schema.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        "$defs": defs,
        "$ref": f"#/$defs/{name}",
    }
    validate_instance(instance, schema)
