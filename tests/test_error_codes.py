from __future__ import annotations

from pathlib import Path

from jcheng_contracts.errors import CANONICAL_CODES, load_mapping, load_registry


def test_registry_matches_enum(root: Path) -> None:
    registry = load_registry(root)
    assert set(registry["codes"]) == set(CANONICAL_CODES)
    for code, entry in registry["codes"].items():
        assert entry["category"]
        assert isinstance(entry["retryable"], bool)
        assert isinstance(entry["http_status"], int)
    assert len(CANONICAL_CODES) == len(set(CANONICAL_CODES))


def test_mapping_targets_exist(root: Path) -> None:
    registry = load_registry(root)
    mapping = load_mapping(root)
    assert mapping
    for legacy, target in mapping.items():
        assert target in registry["codes"], (legacy, target)
