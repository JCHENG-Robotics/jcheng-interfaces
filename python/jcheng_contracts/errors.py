"""Canonical error codes and legacy mapping."""

from __future__ import annotations

from enum import Enum
import json
from pathlib import Path
from typing import Any


class ErrorCode(str, Enum):
    OK = "OK"
    CONTRACT_MAJOR_MISMATCH = "CONTRACT_MAJOR_MISMATCH"
    CONTRACT_HASH_MISMATCH = "CONTRACT_HASH_MISMATCH"
    CONTRACT_UNKNOWN = "CONTRACT_UNKNOWN"
    INVALID_COMMAND = "INVALID_COMMAND"
    UNKNOWN_KIND = "UNKNOWN_KIND"
    UNKNOWN_PROFILE = "UNKNOWN_PROFILE"
    SOURCE_NOT_REGISTERED = "SOURCE_NOT_REGISTERED"
    CAPABILITY_MISMATCH = "CAPABILITY_MISMATCH"
    PROFILE_HASH_MISMATCH = "PROFILE_HASH_MISMATCH"
    CONFIG_HASH_MISMATCH = "CONFIG_HASH_MISMATCH"
    RATE_LIMITED = "RATE_LIMITED"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    NO_LEASE = "NO_LEASE"
    LEASE_EXPIRED = "LEASE_EXPIRED"
    LEASE_PREEMPTED = "LEASE_PREEMPTED"
    LEASE_CONFLICT = "LEASE_CONFLICT"
    LEASE_REVOKED = "LEASE_REVOKED"
    NOT_LEASE_HOLDER = "NOT_LEASE_HOLDER"
    VALIDATION_REQUIRED = "VALIDATION_REQUIRED"
    VALIDATION_EXPIRED = "VALIDATION_EXPIRED"
    VALIDATION_MISMATCH = "VALIDATION_MISMATCH"
    VALIDATION_REUSED = "VALIDATION_REUSED"
    SAFETY_STOP_LATCHED = "SAFETY_STOP_LATCHED"
    SAFETY_HEARTBEAT_MISSING = "SAFETY_HEARTBEAT_MISSING"
    SAFETY_FAULT = "SAFETY_FAULT"
    SYSTEM_DISARMED = "SYSTEM_DISARMED"
    STATE_STALE = "STATE_STALE"
    JOINT_LIMIT = "JOINT_LIMIT"
    VELOCITY_LIMIT = "VELOCITY_LIMIT"
    ACCELERATION_LIMIT = "ACCELERATION_LIMIT"
    STEP_LIMIT = "STEP_LIMIT"
    START_STATE = "START_STATE"
    DURATION_LIMIT = "DURATION_LIMIT"
    WORKSPACE = "WORKSPACE"
    TABLE_CLEARANCE = "TABLE_CLEARANCE"
    LOW_POSE_YAW = "LOW_POSE_YAW"
    FK_UNAVAILABLE = "FK_UNAVAILABLE"
    CONFIG_INVALID = "CONFIG_INVALID"
    PERCEPTION_UNAVAILABLE = "PERCEPTION_UNAVAILABLE"
    PERCEPTION_STALE = "PERCEPTION_STALE"
    MOTION_BUSY = "MOTION_BUSY"
    BUS_READ_FAILED = "BUS_READ_FAILED"
    MOTION_OUTCOME_UNKNOWN = "MOTION_OUTCOME_UNKNOWN"
    TIMEOUT = "TIMEOUT"
    HARDWARE_UNAVAILABLE = "HARDWARE_UNAVAILABLE"
    EVIDENCE_WRITE_FAILED = "EVIDENCE_WRITE_FAILED"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


CANONICAL_CODES = tuple(code.value for code in ErrorCode)


def load_registry(root: str | Path) -> dict[str, Any]:
    """Load ``schemas/error-codes.v1.json`` from a repository root."""
    path = Path(root) / "schemas" / "error-codes.v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_mapping(root: str | Path) -> dict[str, str]:
    """Load the legacy-to-canonical mapping."""
    path = Path(root) / "schemas" / "error-code-mapping.v1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    mappings = payload.get("mappings", {})
    if not isinstance(mappings, dict):
        raise ValueError("error-code-mapping mappings must be an object")
    return {str(key): str(value) for key, value in mappings.items()}


def map_legacy(code: str, root: str | Path) -> str:
    """Return the canonical code for a legacy code, or raise ``KeyError``."""
    return load_mapping(root)[code]
