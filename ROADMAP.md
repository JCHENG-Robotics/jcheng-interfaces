# jcheng-interfaces roadmap

> Status: **v0.2.0** as of 2026-11-27. v0.1.0 remains the released tag;
> v0.2.0 is the additive stop-confirmation contract and still needs its tag and
> consumer adoption. Cross-language bindings remain.

## Current state

| Item | State | Evidence |
|---|---|---|
| Contract audit (M2.1) | Complete (2026-11-23) | [docs/CONTRACT_AUDIT.md](docs/CONTRACT_AUDIT.md) |
| v0.1.0 ROS IDL, schemas, bindings | Complete (2026-11-23) | Tag `v0.1.0`; [CHANGELOG.md](CHANGELOG.md) |
| v0.2.0 stop-confirmation schema | Complete, tag pending (2026-11-27) | `StopResponse.confirmation`/`physical_stop`; `interface_manifest.json` |
| Contract hash and manifest | Complete | `interface_manifest.json` |
| Contract CI | Complete | `.github/workflows/ci.yml` (`contract-ci`) |
| TypeScript bindings | Not started | — |
| Consumer adoption | In progress | `jcheng-system` still pins v0.1.0; `jcheng-mobile`/`jcheng-perception` constrain `<0.2` and must adopt v0.2.0 |

## Milestones

| Milestone | Scope | State | Exit criterion | Evidence |
|---|---|---|---|---|
| M1 | Repository skeleton, scope and audit plan | Complete (2026-11-23) | No IDL before the audit | `docs/M1-SCOPE.md` |
| M2 | Contract audit; v0.1.0 IDL/schemas/bindings; CI; signed tag | Complete (2026-11-23) | Audit signed; tag verified | `docs/CONTRACT_AUDIT.md`; `v0.1.0` |
| M2.4 | Additive stop-confirmation schema | Complete, tag pending (2026-11-27) | Schema tests pass; manifest rebuilt | `CHANGELOG.md` `[0.2.0]` |
| M2.3 | TypeScript bindings and cross-language examples | Planned | Generated types match the JSON Schema; parity test | — |
| M3 | Consumer adoption: system runtime, perception IDL promotion | In progress | Every runtime consumer declares the v0.2 hash; no provisional IDL remains | `jcheng-system` `locks/ecosystem.lock.yaml` |
| M8 | Ecosystem v1.0 contract freeze | Planned | v1.0.0 tag, compatibility matrix and deprecation policy | — |

## Next

1. **Tag and adopt v0.2.0.** Merge the additive schema, create the signed
   `v0.2.0` tag, then update `jcheng-system`'s contract/lock pins and the
   `>=0.1,<0.2` constraints in `jcheng-mobile` and `jcheng-perception`.
2. **M2.3 TypeScript bindings.** Generate TypeScript types from the JSON
   Schema and add a parity test.
3. **Promote `jcheng-perception` messages.** The perception package still uses
   provisional `jcheng_perception_msgs`; promoting them is a contract change
   and must follow the audit and version rules.
4. **Second-consumer hand-shake.** Add a contract-hash check to each capability
   repository's CI so a drifted hash fails before deployment.

## Out of scope

- Nodes, runtime services, hardware access or vendor dependencies.
- Defining application-layer workflows; those belong to L4 repositories.
- Changing the frozen `jcheng-manipulation v1.0.0` tags or evidence.

## Dependencies

- `jcheng-system` 0.3.0-dev currently pins v0.1.0; it must move to v0.2.0 with
  hash `sha256:afca22a42f7163e0351d185d5a8577b0b51f2f3da4b92278f161a4a7d2c35b1c`.
- `jcheng-mobile` and `jcheng-perception` currently declare
  `interfaces >=0.1,<0.2`; both must widen or move to `>=0.2,<0.3` before they
  can hand-shake with a v0.2.0 system.
- Any contract change requires a new version and a manifest rebuild.
