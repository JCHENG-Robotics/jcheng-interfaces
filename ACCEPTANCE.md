# Acceptance report — jcheng-interfaces

> Status: **pass** as of 2026-11-27 for v0.2.0.
> Operator: JerichoCheng. Reviewer: JerichoSwaine (audit and PR approval).
> Scope: contract package, schemas, Python bindings, manifest and CI.
> No runtime node, hardware access or motion command is involved.

## 1. Gates

| Gate | Command | Level | Result | Evidence |
|---|---|---|---|---|
| Repository gate | `bash scripts/check_repo_gate.sh` | L0 | pass | `contract-ci` |
| Manifest freshness | `python3 tools/generate_manifest.py --check` | L0 | pass | `interface_manifest.json` |
| Schema validation | `python3 tools/check_schemas.py` | L0 | pass | `schemas/` |
| No hardware primitives | `python3 tools/check_no_hardware.py` | L0 | pass | `tools/check_no_hardware.py` |
| Contract tests | `python3 -m pytest -q` | L1 | pass (15 tests) | `tests/` |
| ROS interface build | `colcon build --packages-select jcheng_interfaces` | L0 | pass | `contract-ci` (Humble) |
| Interface smoke | `ros2 interface show jcheng_interfaces/msg/MotionCommand` | L0 | pass | `contract-ci` |
| Organization contract-check | `reusable-contract-check.yml@v1` | L0–L1 | pass | `contract-ci` (`org-contract-check`) |
| Organization security baseline | `reusable-security.yml@v1` | L0 | pass | `contract-ci` (`org-security`) |

## 2. Verified claims

| Claim | Level | Evidence |
|---|---|---|
| 14 msg / 10 srv / 1 action are defined and build | L0 | `ros2_ws/src/jcheng_interfaces/`; `interface_manifest.json` |
| IDL, JSON Schema, OpenAPI and error codes agree | L0–L1 | `tests/test_idl_parity.py`, `test_schemas.py`, `test_openapi.py` |
| The contract hash is reproducible from the files | L0 | `tests/test_manifest.py`; `generate_manifest.py --check` |
| The contract exposes no hardware primitives | L0 | `tests/test_no_hardware.py` |
| The v0.1.0 tag is signed and verified | L0 | `v0.1.0` tag on GitHub (`verified=true`) |
| The audit was signed before the IDL was defined | L0 | `docs/CONTRACT_AUDIT.md` |

## 3. Not verified

| Item | Reason | Risk |
|---|---|---|
| TypeScript bindings | Not generated | Web/Studio consumers cannot use generated types |
| Contract behavior inside a runtime | This repository has no nodes | Runtime semantics are covered by `jcheng-system` acceptance, not here |
| Compatibility with a later contract version | Only v0.1.0 exists | The first breaking change has no prior-version test |
| Every consumer hand-shakes the hash | Adoption is in progress | A drifted consumer may fail only at deployment |

## 4. Limitations

- The contract hash is the authoritative compatibility check; SemVer is
  explanatory only. A minor change can still alter the ROS 2 type hash.
- The `jcheng-perception` message package is provisional and not yet promoted
  into this contract.
- No safety or timing behavior is verified by this repository; it defines the
  vocabulary for those checks.

## 5. Sign-off

| Role | Name | Date |
|---|---|---|
| Operator | JerichoCheng | 2026-11-23 |
| Reviewer | JerichoSwaine | 2026-11-23 |

## 6. Machine-readable report

None. Per-repository reports, when produced, must validate against
[`acceptance-report.v1.schema.json`](schemas/acceptance-report.v1.schema.json).
