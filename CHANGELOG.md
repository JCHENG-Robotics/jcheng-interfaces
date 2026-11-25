# Changelog

All notable changes to this project are documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `scripts/humble_ci.sh`: local Humble build and contract-check wrapper in the
  `armpi-humble-moveit` image, mirroring the `m2-contract` CI job with a
  disposable workspace copy.

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
