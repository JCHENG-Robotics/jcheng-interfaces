# Proposal — Offline Artifact Contract v1

> Status: **Accepted (2026-11-28)** for the offline artifact contract only.
> This does not accept or stabilize any runtime/ROS interface. The proposal does
> not move a schema into `jcheng-interfaces` and does not create a new runtime
> contract.

## 1. Problem

`jcheng-devices`, `jcheng-scenarios` and `jcheng-applications` now exchange
generated offline artifacts:

- `jcheng.device_snapshot.v1`
- `jcheng.scenario_requirements.v1`
- `jcheng.device_compatibility.v1`
- `jcheng.applications.reference_report.v1`

The repositories agree in code and tests, but the vocabulary is still
`local_draft` and the cross-repository rules are not reviewed by the interface
owner. Without a recorded contract, a future consumer can misread a hash, a
unit or a capability result as deployment permission.

## 2. Scope and non-goals

In scope:

- identity, version and hash semantics of the generated offline artifacts;
- parameter, feedback and joint representation;
- device-role composition and capability matching result semantics;
- artifact version compatibility and ownership;
- golden test vectors.

Out of scope:

- ROS IDL, DDS topics, gateway HTTP schemas or the runtime robot profile;
- moving the device/scenario JSON Schemas into this repository;
- authorizing deployment, motion or hardware access;
- changing the current artifact filenames or versions.

## 3. Ownership

| Concern | Owner | Consumers |
|---|---|---|
| Contract lifecycle and version registry | `jcheng-interfaces` | all repositories below |
| `jcheng.device_snapshot.v1`, native device capability vocabulary | `jcheng-devices` | applications, system, simulation, learning, studio |
| `jcheng.scenario_requirements.v1`, device/algorithm requirement split | `jcheng-scenarios` | applications, benchmark, simulation |
| `jcheng.device_compatibility.v1`, matching result | `jcheng-devices` | applications, operations admission |
| `jcheng.applications.reference_report.v1`, cell composition consumer | `jcheng-applications` | benchmark, operations |
| Runtime authority, safety overlay, deployment and motion authorization | `jcheng-system` | none of the offline artifacts grant it |

An artifact owner changes its own schema. A cross-repository semantic change
requires a proposal here before a consumer relies on it. `jcheng-interfaces`
does not become the owner of device facts or scenario requirements.

## 4. Identity and hashes

### 4.1 Artifact self-hash

`content_hash` is the **artifact self-hash**:

```text
sha256: + SHA-256(
  canonical JSON of the document with the `content_hash` field removed
)
```

Canonical JSON means: sorted object keys at every level, no insignificant
whitespace (`separators=(",", ":")`), ASCII escaping (`ensure_ascii=True`), and
no NaN/Infinity. The hash covers every other field, including provenance and
nested metadata. Editing any field without regeneration is a stale artifact and
must be rejected by the consumer.

This rule is identical for `jcheng.device_snapshot.v1` and
`jcheng.scenario_requirements.v1`. It is the rule implemented by
`jcheng_devices.snapshot.artifact_content_hash` and
`jcheng_scenarios.requirements.artifact_content_hash`.

### 4.2 Source hash

The source declaration hash is separate and is never substituted for the
artifact self-hash:

| Artifact | Source hash field | Meaning |
|---|---|---|
| device snapshot | `source_hash` | canonical content hash of the source device profile |
| scenario requirements | `provenance.scenario_content_hash` | canonical hash of the scenario declaration documents |

A pin compares a source hash to a source hash. A stale-artifact check compares
`content_hash` to the recomputed self-hash. `deployable` is not a hash and is
not a deployment permission.

### 4.3 Device snapshot fields

Required: `schema`, `source_device`, `device_version`, `source_hash`,
`content_hash`, `generated_by`, `source_path`, `capabilities`, `joints`,
`attributes`, `safety_overlay`, `notes`.

`attributes` carries `category`, `role`, `dof`, `control_modes`,
`kinematics_declared` and optional `data_status`. `dof` is `null` when the
profile does not declare kinematics; it is never derived from the model name or
joint count.

### 4.4 Joint and parameter representation

- Device profiles and snapshots use **degrees** for joint limits:
  `{name, role, limits: {min_deg, max_deg}}`.
- Radians are the only unit in runtime robot profiles and recipes; a consumer
  converts degrees to radians explicitly.
- Capability declarations use a descriptor list
  `[{name, type, required, unit?, description?}]`; feedback uses
  `[{name, type, unit?, description?, rate_hz?}]`.
- A requirement threshold uses `{op, value, unit}` with `op` in
  `>=, <=, >, <, ==, !=`. A requirement without a threshold is prose and is
  `unverified`; a consumer must not invent a value.
- The capability vocabulary is dotted lower-case:
  `arm.position_control`, `arm.joint_feedback`,
  `end_effector.position_control`, `sensor.rgb_stream`, `sensor.depth_stream`,
  `sensor.laserscan`, `base.velocity_intent`.
  Scenario requirement IDs (`manipulation.arm.dof`, ...) are requirement
  vocabulary, not device capability IDs.

## 5. Cell composition and matching result

A scenario may require several roles (`arm`, `gripper`, `camera`, `base`,
`sensor`, `teleop`). One device snapshot fills one role. The consumer must:

1. require the role for a required device requirement; a missing required role
   fails closed (`NO_DEVICE_FOR_ROLE`);
2. require the concrete `interface` on that role's device; a missing interface
   fails closed (`INCOMPATIBLE_CAPABILITY`);
3. evaluate a threshold only against a declared device fact; a missing fact is
   `unverified`, never `matched`;
4. defer algorithm-owned requirements to `deferred_to`; never match them
   against a device.

Result fields and meanings:

| Field | Meaning |
|---|---|
| `artifact_valid` | schema, identity and hashes validated |
| `capability_match_status` | `matched`, `matched_with_unverified`, `unverified` or a fail-closed error |
| `capability_satisfied` | every required capability declared and matched |
| `offline_execution_allowed` | allowed to run an isolated mock experiment |
| `deployment_ready` | verified deployment conditions; always false in the offline reference |
| `motion_authorized` | system runtime authorization; always false in the offline reference |
| `deployable` | deprecated capability-only alias; never deployment permission |

No matching result grants real hardware execution. The system runtime profile,
lease, deadman, stop latch and limits remain the authority.

## 6. Versioning and compatibility

- Artifact schema major version is in the name (`...v1`). Additive optional
  fields are allowed in v1; removing/renaming a field, changing a hash rule or
  changing a unit is a v2 change.
- A consumer must reject an unknown major version, a stale self-hash, a
  malformed source hash and an unresolved required role.
- `vocabulary_status` is `local_draft` today. On acceptance of this proposal it
  becomes `proposed`; it becomes `contracted` only after the interface owner
  records an accepted version. Until then, no document may call the vocabulary
  a formal public standard.
- The proposal version is `1.0.0`; the artifact versions remain
  `jcheng.device_snapshot.v1` and `jcheng.scenario_requirements.v1`.

## 7. Golden vectors

`tests/fixtures/offline_artifact_contract_v1.json` contains canonical documents
and their expected self-hashes. `tests/test_offline_artifact_contract.py`
recomputes each hash and checks that a one-field edit changes it. The vectors
are contract evidence, not device facts or scenario acceptance criteria.

## 8. Acceptance record

Accepted on 2026-11-28. Evidence:

| Condition | Evidence |
|---|---|
| Interface-owner approval | JerichoSwaine, review `APPROVED` on jcheng-interfaces PR #20, 2026-11-28T06:27:30Z |
| Merge | PR #20 merged as `a142641b4fb256aa2368abe778bb6c5b010d1c23` |
| Golden vectors | `tests/test_offline_artifact_contract.py` passes; 22 interfaces tests on the candidate |
| Producer/consumer confirmation | devices PR #7 (`a006f5f`), applications PR #20 (`0be306e`) and `.github` PR #37 (`f9e77eb`) were approved by the same owner and merged |
| Approval record | this section and `docs/CONTRACT.md` §4 |

Scope of acceptance:

- accepted: the offline artifact semantics in this proposal, contract version
  `1.0.0`;
- not accepted: ROS IDL, DDS, HTTP/gateway schemas, runtime robot profiles or
  any real hardware motion authority;
- the capability vocabulary may now be recorded as `contracted` by the scenario
  owner (jcheng-scenarios PR);
- no schema relocation or runtime contract-hash change is implied.

## Related

- [Contract](../CONTRACT.md)
- [Base intent proposal](base-intent-and-lease-holder.md)
- [Devices source of truth](https://github.com/JCHENG-Robotics/jcheng-devices/blob/main/docs/SOURCE_OF_TRUTH.md)
- [Scenario capability matching](https://github.com/JCHENG-Robotics/jcheng-scenarios/blob/main/docs/CAPABILITY_MATCHING.md)
- [Reference integration](https://github.com/JCHENG-Robotics/jcheng-applications/blob/main/docs/REFERENCE_INTEGRATION.md)
