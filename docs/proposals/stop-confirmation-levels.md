# Proposal — stop confirmation levels in `StopResponse`

> Status: **accepted and implemented in v0.2.0** (2026-11-27). The additive
> schema is in `schemas/openapi/jcheng-gateway.v1.yaml`; `VERSION` is `0.2.0`
> and `interface_manifest.json` carries the new hash. The tag is pending.
> The original proposal (2026-11-26) made no schema or tag change.
> Origin: `jcheng-system` execution-model revision R5 and the P0 C2 probe.

## 1. Problem

`POST /v1/motion/stop` returns `StopResponse { accepted, safety, message }`.
`accepted: true` is currently read by clients as "the stop happened". It only
means the gateway accepted the request: the gateway may not have confirmed that
the backend hold/zero command took effect, and the platform can never confirm a
**physical** stop (no e-stop, brake, independent encoder or force sensing).

The application's supervisor therefore has to treat HTTP 200 as "stop
requested", never as safety evidence. The system-side revision records the same
distinction as R5 and is blocked on this contract shape.

## 2. Current facts

| Item | Current shape |
|---|---|
| Request | `StopRequest { operator_id, reason }` |
| Response | `StopResponse { accepted: boolean, safety: SafetyState, message: string }` |
| Meaning of `accepted` | request accepted; not backend or physical confirmation |
| Physical stop | not measurable on this platform |

## 3. Proposed additive fields

Keep `accepted`, `safety` and `message`. Add:

```json
"confirmation": "request_accepted",
"physical_stop": "unverified"
```

| Field | Values | Meaning |
|---|---|---|
| `confirmation` | `request_accepted` | S1: the gateway latched the software stop and accepted the request |
| | `backend_confirmed` | S2: the hold/zero command returned and the motion session is terminal `ABORTED`; the gateway will not issue further motion |
| `physical_stop` | `unverified` (const) | S3 is not measurable; never claim it |

Rules:

- `accepted: true` with `confirmation: request_accepted` is the current
  behaviour and remains valid during the transition.
- `backend_confirmed` may only be set when the gateway's hold/zero call returned
  without error and the session reached terminal `ABORTED`. A failed hold, a
  stop race or a late `COMPLETED` cannot be `backend_confirmed`.
- `physical_stop` is always `unverified`. A future hardware change that adds a
  measurement would need a new contract, not a reinterpretation of this field.
- A client must never infer S2 from HTTP 200, from `accepted`, or from the
  safety latch alone.

## 4. Client behavior after approval

- `jcheng-system` sets `confirmation` explicitly and never upgrades S1 to S2.
- `jcheng-applications` records the level in its run record and CLI; its
  supervisor still treats S1 as unconfirmed and never reports a physical stop.
- `jcheng-studio` displays the level with the same vocabulary.
- A `stop_error` in the application means the request path failed (no S1/S2);
  it is not a physical-stop result.

## 5. Compatibility and rollout

1. Review the field names and the required/optional choice.
2. Add the fields additively to `StopResponse`; bump the contract, regenerate
   `interface_manifest.json`, and update `configs/contract.yaml` and
   `locks/ecosystem.lock.yaml` in the same change.
3. The gateway populates `confirmation`; old clients ignore it.
4. The application parses it when present and keeps working with the old
   response.
5. No tag is moved and no hash changes in this proposal PR.

## 6. Test plan after approval

- Schema validation and manifest regeneration.
- System C1/C2/C2p: idle stop is S1; stop during execute returns S1 then, after
  the terminal `ABORTED`, S2; a late `COMPLETED` cannot be S2.
- Stop-race: a stop that cannot confirm the backend stays S1.
- Application supervisor: S1/S2 recorded separately; no S2 from HTTP 200.
- Studio renders S1/S2/S3 without treating any as an e-stop.

## 7. Resolved in v0.2.0

- `confirmation` and `physical_stop` are **required** in v0.2.0; clients pinned
  to v0.1.0 must adopt the new hash.
- `physical_stop` is a const string, currently `unverified`. A future
  measurement needs a new contract, not a reinterpretation.
- S2 requires the hold/zero call to return without error **and** the session to
  reach terminal `ABORTED`. It does not require a bus read.
- The ROS action cancel path is not changed in v0.2.0; mapping it to the same
  vocabulary remains a system/runtime task.
- A failed hold is an error (non-200) and is never S2. Whether the error
  envelope also carries S1 is left to the system error contract; the gateway
  must not upgrade it to S2.
- `requested_at` is optional; producers that emit it use an ISO 8601
  timestamp. It is included because the system already emits it.
