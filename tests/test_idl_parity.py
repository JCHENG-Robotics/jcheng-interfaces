from __future__ import annotations

from pathlib import Path

from conftest import load_json
from tools.check_no_hardware import field_name


def test_message_fields_match_json_schema(root: Path) -> None:
    schema = load_json(root / "schemas" / "messages.v1.schema.json")
    defs = schema["$defs"]
    msg_dir = root / "ros2_ws" / "src" / "jcheng_interfaces" / "msg"
    message_files = sorted(msg_dir.glob("*.msg"))
    assert message_files
    assert set(defs) - {"Header"} == {path.stem for path in message_files}

    for path in message_files:
        fields = {
            name
            for line in path.read_text(encoding="utf-8").splitlines()
            if (name := field_name(line)) is not None
        }
        schema_fields = set(defs[path.stem]["properties"])
        assert fields == schema_fields, (path.name, sorted(fields ^ schema_fields))
