# Proposal — add an `intent_source` capability class

> Status: **Proposal only**, 2026-11-26. No schema, manifest, contract hash or
> consumer is changed by this document. It asks the `jcheng-interfaces`
> maintainers to add one value to `capability-manifest.v1.schema.json`.

## 1. Problem

The capability manifest safety classes are `motion_source`, `observer` and
`offline` (`schemas/capability-manifest.v1.schema.json`). `jcheng-teleop` is
none of them once its M2 transport exists:

- It is **not** a motion source: it never calls `ExecuteMotion`, never opens a
  device and has no motion authority. The system layer is the only origin of
  motion.
- It is **not** an observer: it publishes a bounded intent stream
  (`/jcheng/intent/teleop` on domain 42), it does not merely read telemetry.
- It is **not offline** once the intent publisher is a runtime surface: the
  current manifest says `class: offline` with an empty `runtime` only because
  the M2 publisher is a test harness and the production lease adapter does not
  exist yet.

The result is a governance gap: a repo can ship a domain-42 publisher while its
manifest truthfully (today) declares an empty runtime, or it can abuse
`motion_source`/`observer` to declare the stream. Neither is acceptable.

## 2. Decision requested

Add `intent_source` to the `safety.class` enum and allow a manifest with that
class to declare domain 42 `publishes` (the reserved intent stream). A minimal
change:

```json
"safety": {
  "class": {"enum": ["motion_source", "observer", "intent_source", "offline"]}
}
```

No other field changes. `requires_lease` stays `const true`, `scopes`,
`max_rate_hz` and `deadman_ms` keep their bounds.

### Semantics

| Class | May publish | May call `ExecuteMotion` | Device access |
|---|---|---|---|
| `motion_source` | motion commands inside the privileged system | yes (system layer only) | through the system bridge |
| `intent_source` | **intent only** (e.g. `TeleopCommand`) to the system gateway/intake | no | none |
| `observer` | read-only telemetry/no motion | no | none |
| `offline` | nothing at runtime | no | none |

`intent_source` is a **capability-plane** class. It does not grant motion
authority: the system lease, deadman, limits and stop latch still decide. A
manifest with this class must declare:

- `runtime.ros_domains: [42]` (schema already only allows 42);
- `publishes: ["/jcheng/intent/teleop"]` (the reserved stream);
- `requires_lease: true`, a `max_rate_hz` within the system intake bound and a
  `deadman_ms` within 1..500.

### Why not reuse `observer` or `motion_source`

- `observer` would make a publisher look read-only; a scanner or reviewer
  cannot distinguish a telemetry tap from an intent stream.
- `motion_source` would collide with the system layer's role and invite the
  claim that teleop is a motion authority. The org taxonomy and
  `SAFETY_MODEL.md` say the opposite.

## 3. Impact

- A **minor schema change** (enum addition) requires a new interfaces tag,
  `interface_manifest.json` regeneration and matching `configs/contract.yaml` +
  `locks/ecosystem.lock.yaml` updates in the consumers. The v0.1.0 tag and hash
  are not mutated.
- Consumers: `jcheng-teleop` (manifest class + runtime declaration, after
  approval), `.github` taxonomy wording, CI schema checks. The system layer
  needs no code change; it validates the stream, not the class.
- Existing manifests with `motion_source`/`observer`/`offline` remain valid; no
  migration is required.

## 4. Interim state in `jcheng-teleop`

Until this proposal is approved and tagged:

- `capability.yaml` stays `class: offline` with an empty runtime. The ROS
  publisher under `ros2_ws/` is explicitly a **test-only** M2 transport: no
  operator input adapter, no lease adapter, no production deployment.
- The repo must not claim a runtime surface it has not admitted.
- `docs/M2_CLOSEOUT.md` records the gap and this proposal as the resolution.

## 5. Open questions

- Should the class be added to the v1 schema as an enum addition, or only in a
  v2 schema with a migration note? An enum addition is backward compatible for
  readers that treat unknown classes as an error only at admission time.
- Does the system layer's own manifest use `motion_source` today? If not, the
  class table above should be reconciled with the system repo before tagging.
- Should `publishes` be constrained to the reserved stream per class, or stay a
  free string list with review? A per-class allow-list is stronger but needs a
  registry of admitted topics.
