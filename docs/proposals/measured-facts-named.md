# Proposal — named measured facts in `MotionResult`

> Status: **proposal** (2026-11-26). No schema, tag or contract-hash change is
> made in this PR. This document asks for a contract review.
> Origin: `jcheng-applications` S3 v0 declared facts.

## 1. Problem

`MotionResult.measured_positions` is a positional array of numbers. It carries
no joint names and no gripper measurement. The application's declared-fact
format can therefore express only `measured_positions[index]`, and a recipe
author must know the robot profile order. Two concrete consequences:

- a `gripper_closed` fact cannot be expressed at all;
- an index-based fact silently reads a different joint if the profile order
  changes, even though `profile_hash` is present.

The S3 v0 implementation uses positional index facts and documents the
constraint. The richer fact vocabulary in the task-engine design
(`{ joint: gripper_joint, at_most_rad: 0.15 }`) is blocked on this contract.

## 2. Current facts

| Field | Current shape |
|---|---|
| `MotionResult.measured_positions` | array of numbers, positional, profile order |
| `MotionResult.bus_verified` | boolean; the values are a bus read only when true |
| `MotionResult.safety.profile_hash` | binds the result to a profile |
| Gripper measurement | not present in `MotionResult` |

## 3. Proposed additive fields

Keep `measured_positions` unchanged for compatibility. Add, only when
`bus_verified` is true:

```json
"measured_joints": { "joint1": 0.031, "joint2": 0.002 },
"measured_gripper_rad": 0.10
```

- A mapping from the profile's joint names to radians. The system must reject
  a result whose names do not match the `profile_hash` profile, and must not
  invent a missing joint.
- `measured_gripper_rad` is optional; absent means "not measured", not zero.
- Both fields are optional in the schema for a transition period; consumers
  must ignore them if absent.
- `measured_positions` remains the positional view; the two views must agree
  when both are present.

## 4. Why not only positional

- The application cannot validate an index against a joint name without
  importing the robot profile, which is a system-side artifact.
- A gripper fact is impossible.
- A profile reorder would silently change task selection.

## 5. Compatibility and rollout

1. Review this proposal; decide the field shape (map vs list of
   `{name, position_rad}`) and whether the gripper is a named joint.
2. Add the schema additively, bump the contract, regenerate
   `interface_manifest.json`, and update `configs/contract.yaml` and
   `locks/ecosystem.lock.yaml` in the same change.
3. The gateway populates the fields only from a verified bus read.
4. `jcheng-applications` adds a named/gripper fact projection after the
   contract lands; positional facts remain supported.
5. A v0.1 consumer that does not know the fields ignores them.

## 6. Safety

- These values are **measurement for task facts**, not a safety function. The
  system layer remains the only origin of motion and keeps the lease, deadman,
  limits and stop latch.
- A fact can only select a pre-declared, pre-authorized branch; it can never
  create motion, widen a scope or retry a failed step.
- `profile_hash` mismatch or missing verification makes the fact `UNKNOWN`,
  which never selects a branch.

## 7. Open questions

- Map or ordered list? Duplicate-name handling?
- Is the gripper a named joint in `measured_joints` or a separate field?
- Units: radians only; no pulse values in the contract?
- Should `/v1/state` expose the same named view?
- Sampling time / staleness: reuse `completed_at`, or add a measurement stamp?
- Which profile version owns the names, and how is a rename handled?

## 8. Test plan after approval

- Schema validation and manifest regeneration.
- Mock gateway returns named and positional views; they agree.
- A name not in the profile is rejected; a missing joint is not invented.
- Application fact tests for named joint, gripper absent and profile mismatch.
- No hardware is required for the schema/mock tests; L5 only for a later
  supervised session.
