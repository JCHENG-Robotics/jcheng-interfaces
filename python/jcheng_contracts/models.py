"""Plain dataclass bindings for the contract metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ContractVersion:
    major: int
    minor: int
    patch: int
    contract_hash: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ContractVersion":
        return cls(
            major=int(value["major"]),
            minor=int(value["minor"]),
            patch=int(value["patch"]),
            contract_hash=str(value["contract_hash"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "contract_hash": self.contract_hash,
        }

    def compatible_with(self, other: "ContractVersion") -> bool:
        """Major must match; the contract hash must match exactly."""
        return self.major == other.major and self.contract_hash == other.contract_hash


@dataclass(frozen=True)
class CapabilityManifest:
    schema_version: str
    name: str
    version: str
    contract: ContractVersion
    scopes: tuple[str, ...]
    hardware_access: bool
    publishes: tuple[str, ...] = field(default_factory=tuple)
    subscribes: tuple[str, ...] = field(default_factory=tuple)
    services: tuple[str, ...] = field(default_factory=tuple)
    max_rate_hz: int = 0
    deadman_ms: int = 0

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CapabilityManifest":
        return cls(
            schema_version=str(value["schema_version"]),
            name=str(value["name"]),
            version=str(value["version"]),
            contract=ContractVersion.from_dict(value["contract"]),
            scopes=tuple(str(item) for item in value.get("scopes", [])),
            hardware_access=bool(value.get("hardware_access", False)),
            publishes=tuple(str(item) for item in value.get("publishes", [])),
            subscribes=tuple(str(item) for item in value.get("subscribes", [])),
            services=tuple(str(item) for item in value.get("services", [])),
            max_rate_hz=int(value.get("max_rate_hz", 0)),
            deadman_ms=int(value.get("deadman_ms", 0)),
        )
