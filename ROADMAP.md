# jcheng-interfaces roadmap

> Status: **v0.1.0** as of 2026-11-24. Contracts are defined and released;
> consumer adoption and cross-language bindings remain.

## Current state

| Item | State | Evidence |
|---|---|---|
| Contract audit (M2.1) | Complete (2026-11-23) | [docs/CONTRACT_AUDIT.md](docs/CONTRACT_AUDIT.md) |
| v0.1.0 ROS IDL, schemas, bindings | Complete (2026-11-23) | Tag `v0.1.0`; [CHANGELOG.md](CHANGELOG.md) |
| Contract hash and manifest | Complete | `interface_manifest.json` |
| Contract CI | Complete | `.github/workflows/ci.yml` (`contract-ci`) |
| TypeScript bindings | Not started | — |
| Consumer adoption | In progress | `jcheng-system` consumes v0.1.0; `jcheng-perception` still carries provisional messages |

## Milestones

| Milestone | Scope | State | Exit criterion | Evidence |
|---|---|---|---|---|
| M1 | Repository skeleton, scope and audit plan | Complete (2026-11-23) | No IDL before the audit | `docs/M1-SCOPE.md` |
| M2 | Contract audit; v0.1.0 IDL/schemas/bindings; CI; signed tag | Complete (2026-11-23) | Audit signed; 15 tests pass; tag verified | `docs/CONTRACT_AUDIT.md`; `v0.1.0` |
| M2.3 | TypeScript bindings and cross-language examples | Planned | Generated types match the JSON Schema; parity test | — |
| M3 | Consumer adoption: system runtime, perception IDL promotion | In progress | Every runtime consumer declares the v0.1 hash; no provisional IDL remains | `jcheng-system` `locks/ecosystem.lock.yaml` |
| M8 | Ecosystem v1.0 contract freeze | Planned | v1.0.0 tag, compatibility matrix and deprecation policy | — |

## Next

1. **M2.3 TypeScript bindings.** Generate TypeScript types from the JSON
   Schema and add a parity test. Prerequisites: none; the schema is stable at
   v0.1.0.
2. **Promote `jcheng-perception` messages.** The perception package still uses
   provisional `jcheng_perception_msgs`; promoting them is a contract change
   and must follow the audit and version rules.
3. **Second-consumer hand-shake.** Add a contract-hash check to each capability
   repository's CI so a drifted hash fails before deployment.

## Out of scope

- Nodes, runtime services, hardware access or vendor dependencies.
- Defining application-layer workflows; those belong to L4 repositories.
- Changing the frozen `jcheng-manipulation v1.0.0` tags or evidence.

## Dependencies

- `jcheng-system` 0.3.0-dev consumes v0.1.0 with hash
  `sha256:0b8d72ced7f54d444d6851d8b99a51a78e2bed3f687324f51a15f76557f24b42`.
- `jcheng-mobile` and `jcheng-perception` declare `interfaces >=0.1,<0.2`.
- Any contract change requires a new version and a manifest rebuild.
