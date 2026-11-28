from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from jcheng_contracts.validate import check_schema, validate_instance, validate_message

from conftest import load_json, load_yaml


def test_all_schemas_are_valid(root: Path) -> None:
    schemas = sorted((root / "schemas").glob("*.schema.json"))
    assert schemas
    for path in schemas:
        check_schema(load_json(path))


def test_messages_schema_defs(root: Path) -> None:
    schema = load_json(root / "schemas" / "messages.v1.schema.json")
    expected = {
        "ContractVersion", "CapabilityManifest", "SafetyState", "ControlLease",
        "MotionCommand", "MotionFeedback", "MotionResult", "RobotState",
        "JointTrajectory", "JointTrajectoryPoint", "BasePulse", "GripperCommand",
        "TeleopCommand", "ValidationReport",
    }
    assert set(schema["$defs"]) == expected | {"Header"}


def test_message_fixtures(root: Path, fixtures: Path) -> None:
    mapping = {
        "motion_command.json": "MotionCommand",
        "safety_state.json": "SafetyState",
        "control_lease.json": "ControlLease",
        "robot_state.json": "RobotState",
        "validation_report.json": "ValidationReport",
        "motion_result.json": "MotionResult",
    }
    for name, message in mapping.items():
        validate_message(message, load_json(fixtures / name), root)


def test_config_fixtures(root: Path, fixtures: Path) -> None:
    cases = [
        ("capability.yaml", "capability-manifest.v1.schema.json"),
        ("robot_profile.yaml", "robot-profile.v1.schema.json"),
        ("lockfile.yaml", "lockfile.v1.schema.json"),
    ]
    for name, schema_name in cases:
        schema = load_json(root / "schemas" / schema_name)
        validate_instance(load_yaml(fixtures / name), schema)

    for name, schema_name in [
        ("evidence.json", "evidence-record.v1.schema.json"),
        ("acceptance.json", "acceptance-report.v1.schema.json"),
    ]:
        schema = load_json(root / "schemas" / schema_name)
        validate_instance(load_json(fixtures / name), schema)


def test_robot_profile_v2_fixtures(root: Path, fixtures: Path) -> None:
    schema = load_json(root / "schemas" / "robot-profile.v2.schema.json")
    for name in ("robot_profile_v2_piper.json", "robot_profile_v2_bus_servo.json"):
        validate_instance(load_json(fixtures / name), schema)


def test_robot_profile_v2_bus_fields_follow_kind(root: Path, fixtures: Path) -> None:
    schema = load_json(root / "schemas" / "robot-profile.v2.schema.json")
    piper = load_json(fixtures / "robot_profile_v2_piper.json")
    bus = load_json(fixtures / "robot_profile_v2_bus_servo.json")

    wrong = deepcopy(piper)
    wrong["joints"][0]["servo_id"] = 1
    with pytest.raises(ValueError, match="servo_id"):
        validate_instance(wrong, schema)

    wrong = deepcopy(bus)
    wrong["joints"][0]["index"] = 1
    with pytest.raises(ValueError, match="index"):
        validate_instance(wrong, schema)


def test_robot_profile_v2_requires_chains_and_typed_gripper(
    root: Path, fixtures: Path
) -> None:
    schema = load_json(root / "schemas" / "robot-profile.v2.schema.json")
    piper = load_json(fixtures / "robot_profile_v2_piper.json")

    wrong = deepcopy(piper)
    del wrong["chains"]
    with pytest.raises(ValueError, match="chains"):
        validate_instance(wrong, schema)

    wrong = deepcopy(piper)
    wrong["gripper"]["unit"] = "rad"
    with pytest.raises(ValueError):
        validate_instance(wrong, schema)
