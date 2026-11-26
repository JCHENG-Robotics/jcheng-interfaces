# Piper X robot profile — proposal for a CAN-arm profile (v0.2)

> Status: **proposal only**, 2026-11-26. No IDL, JSON Schema, contract hash,
> lock file or robot config is changed by this document. A profile change is a
> contract change and needs the audit/tag procedure in
> [`VERSIONING.md`](../VERSIONING.md) and [`CONTRACT.md`](../CONTRACT.md).
> Author: ZCode (research agent), for J. Cheng. Reviewer: pending.

## 1. Why v1 does not fit

`schemas/robot-profile.v1.schema.json` is a **bus-servo** profile:

| v1 requirement | Piper X reality |
|---|---|
| `joints[].servo_id` (integer ≥ 1, required) | No servo IDs; the arm is a CAN device with joint indices 1…6 |
| `gripper.servo_id` (required) | No gripper servo ID; the gripper is a prismatic joint driven through the arm |
| `measured_open_pulses` / `measured_closed_pulses` (required arrays) | No pulse telemetry; position is in radians/metres |
| `profiles.base` (duty/duration) | Not applicable to this arm (the chassis is a separate capability) |
| `workspace.tip_link` | Usable: should be `tcp_link` |
| `source_hashes` | Usable: pin the URDF and gripper xacro |

Filling v1 with fake `servo_id=1…6` or pulse arrays would fabricate hardware
semantics, which the contract forbids. The schema needs a second profile kind,
or v1 needs a compatible extension.

## 2. Facts the profile must carry

From `agx_arm_urdf@680fa925` (MIT) and `agx_arm_ros@747d0722` (MIT); the full
table is [`joint_map.yaml`](../../../jcheng-simulation/docs/robots/piper_x/joint_map.yaml):

- 6 revolute joints `joint1`…`joint6`, axis `0 0 1` in each joint frame.
- Limits: J1 ±2.6179938, J2 0…3.1415926, J3 -2.9670597…0, J4 ±1.553343,
  J5 ±1.553343, J6 ±2.9670597 rad.
- Gripper: `gripper` prismatic 0…0.1 m (master), `gripper_joint1` 0…0.05 m
  (mimic +0.5), `gripper_joint2` -0.05…0 m (mimic -0.5).
- Tip frame: `tcp_link`, fixed to `link6`; the offset is **unmeasured**.
- Source hash: URDF `sha256:93eb2a84…`, gripper xacro `sha256:88561fe4…`.
- Public specification J6 ±165° vs URDF ±170°: a safety limit must be confirmed
  by firmware/bus read, not inferred from the URDF.

## 3. Proposed v0.2 shape (illustrative, not a valid v1 document)

```yaml
schema_version: 2
robot: piper_x
profile_version: 0.1.0-draft
kind: can_arm                 # new: can_arm | bus_servo
baseline_ref:
  repo: agilexrobotics/agx_arm_urdf
  commit: 680fa925cd00db7e2628563d2edc5540963045de

joints:
  - name: joint1
    index: 1                  # new: required for can_arm; 1-based
    lower_rad: -2.6179938
    upper_rad: 2.6179938
    max_velocity_rad_s: 5.0   # URDF declaration, not measured
    max_acceleration_rad_s2: 5.0
  # joint2 … joint6 follow the same shape

gripper:
  type: parallel_prismatic    # new: parallel_prismatic | bus_servo
  master_joint: gripper
  stroke_m: 0.1
  lower_m: 0.0
  upper_m: 0.1
  mimic_joints:
    - {name: gripper_joint1, multiplier: 0.5, offset: 0.0}
    - {name: gripper_joint2, multiplier: -0.5, offset: 0.0}

workspace:
  frame: base_link
  tip_link: tcp_link
  lower: [TBD, TBD, TBD]
  upper: [TBD, TBD, TBD]

tcp_offset:
  xyz_m: [TBD, TBD, TBD]      # new; unmeasured for Piper X + gripper
  rpy_rad: [TBD, TBD, TBD]
  status: unmeasured
```

`TBD` values are deliberately not numbers: the proposal must not invent a
workspace or TCP. A v2 schema can make `workspace` optional for a draft profile,
or keep it required and fail closed until measured.

## 4. Compatibility and release mechanics

- A schema that requires new fields or changes `servo_id` semantics is a
  **breaking** change. Under `0.y.z`, any IDL structure change bumps the minor
  version and changes the contract hash (`VERSIONING.md:3`).
- Therefore the expected version is **0.2.0**, with a new tag, a regenerated
  `interface_manifest.json`, and matching `configs/contract.yaml` +
  `locks/ecosystem.lock.yaml` updates (root `AGENTS.md` contract rules).
- v1 profiles must remain loadable and unchanged. Do not mutate
  `robot-profile.v1.schema.json` in place; add `robot-profile.v2.schema.json`
  or a versioned union with an explicit `kind`.
- The `jcheng-system` runtime profile for Piper X would be a generated instance
  of the new schema, not a hand-edited YAML. Its `source_hashes` must include
  the URDF and the generated plant config.
- No IDL field may expose raw CAN frames, registers, `servo_id`, `raw`,
  `register`, `eeprom` or `motor_duty`; `tools/check_no_hardware.py` enforces
  this for `*.msg/*.srv/*.action`. Keep the CAN mapping in `jcheng-system`.

## 5. Open questions

1. **Joint index order**: does the vendor SDK index `joint1`=1 … `joint6`=6, and
   is the sign convention identical to the URDF? Verify with a read-only bus
   session before writing the profile.
2. **Gripper convention**: is `gripper=0` open or closed? The URDF says 0…0.1 m;
   the MoveIt SRDF calls `0.1` `gripper_open` and `0.0` `gripper_close`, but the
   vendor SDK may use the opposite direction. The adapter must own the sign.
3. **J6 limit**: ±165° spec vs ±170° URDF; choose the conservative soft limit
   until firmware confirms.
4. **TCP**: measure `link6` → fingertip; do not reuse the 0.1425 m standard
   Piper example.
5. **Acceleration**: `joint_limits.yaml` declares 5.0 rad/s² for all joints; this
   is not a measured limit. A runtime profile should use a lower, reviewed value.

## 6. What this proposal does not do

- It does not add or change any `.msg`, `.srv`, `.action` or JSON Schema.
- It does not grant motion authority; `ExecuteMotion` remains the only entry.
- It does not make the vendor driver a JCHENG component.
- It does not certify Piper X safety, accuracy or repeatability.

## 7. Related

- Source audit: [`piper-x-assets.md`](../../../jcheng-research/references/manipulation/piper-x-assets.md)
- Report: [`20261126-piper-x-simulation-data-map.md`](../../../jcheng-research/reports/20261126-piper-x-simulation-data-map.md)
- Joint table: [`joint_map.yaml`](../../../jcheng-simulation/docs/robots/piper_x/joint_map.yaml)
- Current profile schema: [`robot-profile.v1.schema.json`](../../schemas/robot-profile.v1.schema.json)
- Versioning: [`VERSIONING.md`](../VERSIONING.md)
