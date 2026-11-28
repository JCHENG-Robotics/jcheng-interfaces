"""Golden vectors for the proposed offline artifact contract."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "offline_artifact_contract_v1.json"


def _load() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _content_hash(document: dict) -> str:
    body = {key: value for key, value in document.items() if key != "content_hash"}
    canonical = json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_fixture_declares_the_contract_identity() -> None:
    payload = _load()
    assert payload["contract"] == "jcheng.offline-artifact-contract.v1"
    assert payload["contract_version"] == "1.0.0"
    assert payload["semantics"]["cell_roles"] == [
        "arm",
        "gripper",
        "camera",
        "base",
        "sensor",
        "teleop",
    ]


@pytest.mark.parametrize("index", [0, 1])
def test_golden_vector_self_hash_matches(index: int) -> None:
    payload = _load()
    vector = payload["vectors"][index]
    document = vector["document"]
    assert document["content_hash"] == _content_hash(document)
    assert document["content_hash"].startswith("sha256:")
    assert len(document["content_hash"]) == len("sha256:") + 64


@pytest.mark.parametrize("index", [0, 1])
def test_one_field_edit_changes_the_hash(index: int) -> None:
    payload = _load()
    document = copy.deepcopy(payload["vectors"][index]["document"])
    original = document["content_hash"]
    document["notes" if index == 0 else "scenario_id"] = "edited"
    assert _content_hash(document) != original


def test_source_and_artifact_hashes_are_distinct() -> None:
    payload = _load()
    device = payload["vectors"][0]["document"]
    scenario = payload["vectors"][1]["document"]
    assert device["source_hash"] != device["content_hash"]
    assert (
        scenario["provenance"]["scenario_content_hash"]
        != scenario["content_hash"]
    )
