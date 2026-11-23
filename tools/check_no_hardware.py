#!/usr/bin/env python3
"""Reject raw hardware primitives from the canonical contract."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDL_ROOT = ROOT / "ros2_ws" / "src" / "jcheng_interfaces"

FORBIDDEN_FIELDS = {
    "servo_id",
    "target_pulse",
    "raw_position",
    "raw",
    "register",
    "eeprom",
    "torque",
    "set_position",
    "motor_duty",
    "duty_raw",
}
FORBIDDEN_TYPES = {
    "ServoPosition",
    "ServosPosition",
    "SetBusServoState",
    "GetBusServoState",
    "MotorsSpeedControl",
}
ALLOWED_FIELDS = {"base_pulse", "base_duty"}


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def field_name(line: str) -> str | None:
    stripped = line.split("#", 1)[0].strip()
    if not stripped or stripped == "---" or "=" in stripped:
        return None
    parts = stripped.split()
    if len(parts) < 2:
        return None
    name = parts[-1].strip()
    if name.endswith("[]"):
        name = name[:-2]
    return name


def scan(idl_root: Path = IDL_ROOT) -> list[str]:
    problems: list[str] = []
    for path in sorted(Path(idl_root).rglob("*")):
        if path.suffix not in (".msg", ".srv", ".action"):
            continue
        if path.stem in FORBIDDEN_TYPES:
            problems.append(f"{_display(path)}: forbidden type name {path.stem}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            name = field_name(line)
            if name in FORBIDDEN_FIELDS and name not in ALLOWED_FIELDS:
                problems.append(f"{_display(path)}:{number}: forbidden field {name}")
            for forbidden in FORBIDDEN_TYPES:
                if forbidden in line.split("#", 1)[0]:
                    problems.append(
                        f"{_display(path)}:{number}: forbidden type {forbidden}"
                    )
    return problems


def main() -> int:
    problems = scan()
    if problems:
        print("raw hardware primitives found:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    print("no raw hardware primitives in jcheng_interfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
