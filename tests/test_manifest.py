from __future__ import annotations

from pathlib import Path

from jcheng_contracts.manifest import (
    build_manifest,
    check_manifest,
    contract_hash,
    normalise,
)


def test_manifest_has_required_files(root: Path) -> None:
    manifest = build_manifest(root)
    assert manifest["package"] == "jcheng_interfaces"
    assert manifest["version"] == "0.1.0"
    assert manifest["contract_hash"].startswith("sha256:")
    assert len(manifest["contract_hash"]) == len("sha256:") + 64
    files = manifest["files"]
    assert "ros2_ws/src/jcheng_interfaces/msg/MotionCommand.msg" in files
    assert "schemas/messages.v1.schema.json" in files
    assert "schemas/openapi/jcheng-gateway.v1.yaml" in files
    assert "interface_manifest.json" not in files


def test_manifest_is_current(root: Path) -> None:
    assert check_manifest(root) == []


def test_contract_hash_is_stable(root: Path) -> None:
    assert contract_hash(root) == contract_hash(root)
    assert contract_hash(root) == build_manifest(root)["contract_hash"]


def test_idl_comments_do_not_change_hash(tmp_path: Path) -> None:
    path = tmp_path / "Sample.msg"
    path.write_text("float64 value  # comment\n", encoding="utf-8")
    first = normalise(path, path.read_text(encoding="utf-8"))
    path.write_text("float64 value\n", encoding="utf-8")
    second = normalise(path, path.read_text(encoding="utf-8"))
    assert first == second
