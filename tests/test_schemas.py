from __future__ import annotations

from pathlib import Path

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
