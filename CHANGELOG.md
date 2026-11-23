# Changelog

## 0.1.0 (2026-11-23)

- M2.1 契约审计签字（`docs/CONTRACT_AUDIT.md`）。
- 建立 `jcheng_interfaces` ROS 2 包：核心消息、服务与 `ExecuteMotion` action。
- 建立 v0.1 JSON Schema、OpenAPI `/v1`、WebSocket 协议与错误码注册表。
- 建立 `jcheng_contracts` Python 绑定、manifest 生成与契约哈希。
- 建立 M2 契约 CI（Humble + Jazzy、Schema parity、硬件原语扫描）。
- 没有运行节点、没有硬件依赖、没有修改 `jcheng-manipulation v1.0.0`。

## 版本规则

- `0.y.z`：初始开发期；任何 IDL 结构变化都提升 minor 并改变契约哈希。
- `1.0.0` 起：破坏性变更提升 major；新增字段/消息提升 minor；仅文档/生成器修复为 patch。
- 具体规则见 `docs/VERSIONING.md` 与设计文档 `05-versioning-lock-release.md`。
