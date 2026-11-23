# 契约草案原则（非最终）

> 本文件只记录原则；字段与消息在契约审计签字后才定义。

## 1. 分层

| 层 | 载体 | 版本 |
|---|---|---|
| ROS IDL | `jcheng_interfaces` 包 | 契约哈希 + SemVer |
| HTTP/OpenAPI | `schemas/openapi/` | URL `/v1` |
| WebSocket | `schemas/ws/` | 协议版本字段 |
| Python | `jcheng_contracts` | 跟随契约 |
| TypeScript | 生成 | 跟随 OpenAPI |
| 配置/证据 | JSON Schema | Schema 版本 |

## 2. 规则

1. 单一运动入口 `ExecuteMotion`；能力模块只提交意图。
2. SI 单位：`rad`、`rad/s`、`rad/s²`、`m`、`s`。
3. 位姿显式 `frame_id` 与 `tip_link`。
4. 状态显式 `truth=measured|commanded`；完成显式 `verification=bus|timed|open_loop`。
5. 每个租约申请与运动命令携带 `ContractVersion`（含 `contract_hash`）。
6. 幂等键；重放返回同一结果。
7. 失败关闭；未知字段/枚举/版本拒绝。
8. 契约不提供原始舵机寄存器、任意占空比、直接厂商话题原语。
9. 审计可重建；结果带 `evidence_id`。
10. 控制决策用本机单调时钟；跨主机时间戳只作记录。

## 3. 待审计后决定

- `ValidateTrajectory` 是否保留 JSON 报告字段。
- `ArmMove` 的弃用方式。
- 遥操作流契约是否在 v0.1 定义、试点时启用。
- 夹爪弧度符号（契约正向 vs URDF `r_joint` 负向）。
- 底盘 duty 归一化与厂商原始 duty 的换算位置。
- Studio 现有 `/api/*` 的兼容层边界。
