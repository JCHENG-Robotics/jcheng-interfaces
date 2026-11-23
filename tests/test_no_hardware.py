from __future__ import annotations

from pathlib import Path

from tools.check_no_hardware import scan


def test_contract_has_no_raw_hardware_fields(root: Path) -> None:
    assert scan(root / "ros2_ws" / "src" / "jcheng_interfaces") == []


def test_scanner_catches_servo_id(tmp_path: Path) -> None:
    (tmp_path / "Bad.msg").write_text("int32 servo_id\n", encoding="utf-8")
    problems = scan(tmp_path)
    assert problems
    assert "servo_id" in problems[0]
