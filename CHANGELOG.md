# Changelog

All notable changes to this project are documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **Accepted** `docs/proposals/offline-artifact-contract-v1.md` for the offline
  artifact contract only (contract 1.0.0; PR #20 review approval, merge
  `a142641`). No IDL/schema/runtime change.
- Proposal `docs/proposals/offline-artifact-contract-v1.md`: cross-repository
  semantics for device snapshots, scenario requirements, cell composition,
  capability-match results, hash rules and units. Status Proposed; vocabulary
  remains `local_draft`. Golden vectors and their test are included. No IDL,
  schema relocation or contract-hash change.
- `scripts/humble_ci.sh`: local Humble build and contract-check wrapper in the
  `armpi-humble-moveit` image, mirroring the `m2-contract` CI job with a
  disposable workspace copy.
- Proposal `docs/proposals/measured-facts.md`: additive named
  `measured_joints`/`measured_gripper_rad` fields for `MotionResult`, populated
  only from a verified bus read. No schema or contract-hash change.
- Proposal `docs/proposals/piper-x-robot-profile.md`: PiPER X profile and
  joint-limit contract for a simulation-only arm. No schema or contract-hash
  change.

## [0.3.0] — 2026-11-28

Additive multi-chain and gripper-unit contract release for the fixed-cell
pivot. `interface_manifest.json` is `sha256:8bc92d18…`; the VERSION bump is
required because the IDL and schemas changed.

### Added

- `robot-profile.v2.schema.json`: bus-agnostic n-DoF profiles with per-chain
  workspace/tip, `kind` (`bus_servo` / `can_arm`), an optional base chain and a
  typed gripper.
- `MotionCommand.chain_id`, `TeleopCommand.chain_id` and `ControlLease.chain_id`
  (empty = default chain) so one arm of a dual-arm cell can be addressed and
  leased independently.
- `RobotState.chain_ids` parallel to `joint_names`.
- `GripperCommand.unit` (`rad` / `m`, empty = profile) with profile-driven
  bounds; the 2.22 rad upper bound is removed from the contract.

### Changed

- `robot-profile.v2` makes `chains[].workspace` optional so an unmeasured cell
  fails closed instead of inventing bounds.

## [0.2.0] — 2026-11-27

Additive stop-confirmation contract release; no IDL or ROS message change.
Signed tag `v0.2.0` is GitHub-verified.

### Added

- `StopResponse.confirmation` with `request_accepted` (S1) and
  `backend_confirmed` (S2), required in v0.2.0.
- `StopResponse.physical_stop` fixed to `unverified`; S3 is not measurable on
  this platform.
- `StopResponse.requested_at` as an optional ISO 8601 timestamp, matching the
  existing system response.
- OpenAPI test for the required fields, enum and const.

### Changed

- `VERSION` is `0.2.0`; the contract hash is
  `sha256:afca22a42f7163e0351d185d5a8577b0b51f2f3da4b92278f161a4a7d2c35b1c`.
- Consumers pinned to `interfaces >=0.1,<0.2` or to the v0.1.0 hash must adopt
  the v0.2.0 hash before their runtime handshake can pass.

## [0.1.0] — 2026-11-23

First contract release; signed tag `v0.1.0`.

### Added

- `jcheng_interfaces` ROS 2 package: 14 messages, 10 services and the
  `ExecuteMotion` action.
- v0.1 JSON Schemas, OpenAPI `/v1`, WebSocket `/v1` protocol and the
  52-entry error-code registry.
- `jcheng_contracts` Python bindings, manifest generator and the contract
  hash `sha256:0b8d72ced7f54d444d6851d8b99a51a78e2bed3f687324f51a15f76557f24b42`.
- Contract CI (`contract-ci`): manifest, schema, parity, no-hardware and
  repository gates; the M2 execution record also reports a local Jazzy build
  with the same checks.
- Contract audit and scope documents (`docs/CONTRACT_AUDIT.md`,
  `docs/M2-SCOPE.md`).

## Version policy

- `0.y.z`: initial development; any IDL structure change raises the minor
  version and changes the contract hash.
- From `1.0.0`: breaking changes raise major; new fields/messages raise minor;
  documentation or generator fixes are patch.
- The full rules are in `docs/VERSIONING.md`.
