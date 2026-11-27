# Proposal — base intent, base state and lease-holder semantics

> Status: **Proposal only**, 2026-11-27. No IDL, schema, manifest, contract hash
> or consumer is changed by this document. It requests review before any
> contract implementation.

## 1. Problem

The mobile base has no capability-plane contract. Nav2 publishes
`geometry_msgs/Twist` on `/cmd_vel`; the vendor `mecanum` node subscribes to the
same absolute topic and publishes motor speeds, with no lease, deadman or
timeout. The runtime authority audit records this as a P1 bypass. The arm has
`ExecuteMotion`; the base has nothing equivalent, so the two cannot share the
system lease, stop latch or audit trail.

The lease also has no holder identity. `RenewLease` and `ReleaseLease` do not
prove who owns the lease, so any caller with the gateway token can renew or
release another client's motion.

## 2. Decision requested

Add two messages and three lease fields. This is an additive minor change; no
existing field is removed or renumbered.

### 2.1 `BaseIntent.msg` (capability plane, domain 42)

```text
std_msgs/Header header
string lease_id
string holder
string command_id
uint64 seq
float64 linear_x_mps
float64 linear_y_mps
float64 angular_z_radps
float64 max_duty_normalized    # 0.0..1.0, system clamps
uint32 deadman_ms              # requested; system clamps to its bound
string source                  # "nav2" | "teleop" | "scripted"
ContractVersion contract
```

Rules:

- The intent is **not** motion authority. `jcheng-system` still owns the lease,
  deadman, limits, stop latch and the only hardware path.
- `holder` identifies the client; it is not authentication. Authentication is
  SROS2/token at the transport, plus the system lease check.
- `seq` must increase per `(lease_id, command_id)`; a duplicate `command_id`
  with the same `seq` is idempotent; an older `seq` is rejected.
- `deadman_ms` is a request; the system clamps it to its own bound (≤ 500 ms).
- `max_duty_normalized` is a request; the system clamps it to the deployed
  chassis limit.
- A zero linear/angular intent is a stop request, not a hold.

### 2.2 `BaseState.msg` (observation plane, read-only)

```text
std_msgs/Header header
float64 linear_x_mps
float64 linear_y_mps
float64 angular_z_radps
float64 applied_duty_normalized
string zero_reason    # NONE | NO_LEASE | LEASE_EXPIRED | HOLDER_MISMATCH |
                      # DEADMAN | STOP_LATCHED | TIMEOUT | CONTRACT_MISMATCH | FAULT
bool stop_latched
ContractVersion contract
```

`BaseState` is telemetry, not a command. Studio and ops may read it; they may
not derive authority from it.

### 2.3 Lease holder fields

Add `string holder` to `AcquireLease`, `RenewLease` and `ReleaseLease`.
Semantics:

- `AcquireLease` records the holder; `holder` is required and non-empty.
- `RenewLease` and `ReleaseLease` must carry the same holder; mismatch → 403,
  no state change.
- A holder cannot renew or release another holder's lease.
- Administrative revoke requires a separate admin token/scope and is audited;
  it is not a normal client operation.
- Stop is accepted without a lease and is never blocked by an expired motion
  lease. Stop latches; only an authorized reset clears it.
- A lease revoked or expired transitions all scoped motion to zero/stop; a
  subsequent valid intent requires a new lease.

## 3. Authority matrix

| Action | Intent producer | Executor | Gate |
|---|---|---|---|
| Arm joint/gripper | applications / teleop | system `ExecuteMotion` | lease + deadman + limits + stop |
| Base velocity | mobile / teleop | system base authority | lease(base) + holder + deadman + timeout + stop |
| Stop | any client | system | always accepted; latches |
| Lease issue/renew/release | operator client | system | holder match; admin revoke separate |

The base may use a different action/message from the arm; it must share the
same lease manager, arbiter, deadman and stop latch.

## 4. Compatibility and release

- Additive messages and fields only; no IDL field is removed or renumbered.
- Requires a new interfaces minor release and tag; the contract hash changes.
- Consumers: `jcheng-mobile` (producer), `jcheng-system` (consumer/validator),
  `jcheng-studio` and `jcheng-ops` (read-only `BaseState`), `jcheng-teleop`
  (optional producer once its base intent exists).
- A consumer must not pin the proposal; it pins the released tag and hash.
- Until the release, implementations use a repository-local core type and do
  not publish a production DDS contract.

## 5. Security and non-goals

- No device access, no direct motor topic, no motion authority in this
  contract.
- Domain 42 carries intent only; the hardware bridge remains domain 0.
- The contract does not replace SROS2, the system lease, the stop latch or the
  hardware watchdog.
- It does not claim functional-safety certification or an emergency stop.
- It does not define a common action for all devices; arm and base may differ.

## 6. Open questions

1. `holder` format: free string, UUID, or authenticated principal id?
2. Default base deadman and timeout: 200 ms provisional, or a different bound?
3. `max_duty_normalized` vs m/s: keep both, or only SI units with a deployed
   conversion?
4. QoS: reliable depth 1 with deadline/lifespan, or best-effort?
5. Is `BaseState` needed in v1, or can studio read the system telemetry stream?
6. Does base intent need a trajectory/acceleration field for smooth Nav2
   handoff, or is velocity sufficient for v1?

## 7. Impact if rejected

- The mobile base keeps `/cmd_vel` as an unleased intent; the P1 bypass cannot
  be closed with a contract-grade interface.
- The system can still implement a repo-local base intake for mock tests, but
  the production path remains non-contractual.

## Related

- [Capability intent source proposal](capability-intent-source.md)
- [Repository boundary specification](https://github.com/JCHENG-Robotics/.github/blob/main/docs/repo-boundaries.md)
- [Runtime authority audit](https://github.com/JCHENG-Robotics/.github/blob/main/docs/boundary-consolidation/02-runtime-authority-audit.md)
