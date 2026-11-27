# jcheng-interfaces

**English** | [简体中文](README.zh-CN.md)

The canonical contract repository for JCHENG Robotics.

> Status: **Experimental** — v0.2.0 as of 2026-11-27. The contract audit is
> signed, the contract test suite passes in CI, and the signed `v0.2.0` tag is
> GitHub-verified. v0.2.0 adds the additive stop-confirmation fields; no
> runtime nodes, hardware access or vendor dependencies.
> English canonical; the Chinese README is a translation.

## 1. Responsibility

- One ROS 2 package, `jcheng_interfaces`: 14 msg / 10 srv / 1 action.
- JSON Schema, OpenAPI `/v1`, WebSocket `/v1` and the error-code registry.
- Pure Python contract bindings, `jcheng_contracts`.
- The `contract_hash` and `interface_manifest.json`.
- Compatibility checks and contract documentation.

**Not included:** nodes, hardware access, vendor dependencies, business logic.

## 2. Why audit first

The baseline already carried a scattered interface surface:

- `arm_interfaces/action/ArmMove.action` and `srv/ValidateTrajectory.srv`.
- Studio backend `/api/*` (preview, execute, stop, lease, events).
- Gateway `/motion/*`, `/chassis/*`, `/state`, `/safety_stop`.
- `armpi_safety`'s consumption of `ValidateTrajectory` and `/safety_stop`.

Defining a new contract directly would risk duplicate names, changed
units/frames, broken compatibility or lost safety semantics. The M1/M2 gate was
therefore: **audit first, define second**.

- [Contract audit plan](docs/CONTRACT_AUDIT_PLAN.md)
- [Contract audit (M2.1, signed)](docs/CONTRACT_AUDIT.md)
- [M1 scope](docs/M1-SCOPE.md)
- [M2 scope](docs/M2-SCOPE.md)
- [Contract principles (v0.1)](docs/CONTRACT.md)
- [Version policy](docs/VERSIONING.md)
- [Compatibility matrix](docs/COMPATIBILITY.md)

## 3. v0.2 layout

```text
ros2_ws/src/jcheng_interfaces/    # 14 msg / 10 srv / 1 action
schemas/                          # JSON Schema / OpenAPI / WS / error codes
python/jcheng_contracts/          # Python bindings and manifest tooling
tests/                            # contract / compatibility / parity tests
tools/                            # manifest / schema / hardware-primitive checks
interface_manifest.json           # per-file hashes + contract hash
```

v0.2 is an additive schema release: `StopResponse` gains `confirmation`
(`request_accepted` / `backend_confirmed`), `physical_stop=unverified` and the
optional `requested_at` timestamp. The IDL, ROS message set and WebSocket
protocol are unchanged; the contract hash changes because the OpenAPI schema is
covered by it. The full suite passes locally; TypeScript bindings are still
planned for M2.3.

## 4. Requirements

- ROS 2 Humble or Jazzy (CI uses Humble).
- Python ≥ 3.10 with `jsonschema`, `PyYAML` and `pytest` for the test layer.
- No hardware, devices or runtime nodes.

## 5. Quick start

```bash
# Contract tests (pure Python, no ROS)
python3 -m pytest -q

# Contract gates
python3 tools/generate_manifest.py --check
python3 tools/check_schemas.py
python3 tools/check_no_hardware.py

# Build the ROS interface package
source /opt/ros/humble/setup.bash
colcon build --base-paths ros2_ws/src --packages-select jcheng_interfaces
source install/setup.bash
ros2 interface show jcheng_interfaces/msg/MotionCommand
```

`tools/generate_manifest.py --write` rebuilds the manifest after a contract
change; CI uses `--check` and rejects a stale manifest.

## 6. Constraints

- The contract exposes no raw servo registers, arbitrary duty cycle or direct
  vendor-topic primitives.
- Motion is expressed only through `ExecuteMotion`; state must carry `truth`
  and `verification`.
- Contract changes precede consumer changes; runtimes hand-shake on the
  contract hash.
- The `jcheng-manipulation v1.0.0` tags, evidence and experiment history are
  never modified.

## 7. Validation status

| Claim | Status | Evidence |
|---|---|---|
| IDL / Schema / OpenAPI / error-code parity | Verified (L0–L1) | 15 contract tests; `contract-ci` |
| Manifest and contract hash match the files | Verified (L0) | `interface_manifest.json`; `generate_manifest.py --check` |
| No hardware primitives, no runtime nodes | Verified (L0) | `check_no_hardware.py`; repository gate |
| TypeScript bindings | Not provided | Planned for M2.3 |

Full report: [ACCEPTANCE.md](ACCEPTANCE.md).

## 8. Related repositories

- [`jcheng-system`](https://github.com/JCHENG-Robotics/jcheng-system) — the main runtime consumer.
- [`jcheng-mobile`](https://github.com/JCHENG-Robotics/jcheng-mobile) and
  [`jcheng-perception`](https://github.com/JCHENG-Robotics/jcheng-perception) — capability repositories.
- [`.github`](https://github.com/JCHENG-Robotics/.github) — ecosystem roadmap, changelog and acceptance.

## 9. License

The license review is in progress; this repository has no `LICENSE` and all
rights are reserved. See [LICENSE-REVIEW.md](LICENSE-REVIEW.md) and the full
inventory in `.github`.
