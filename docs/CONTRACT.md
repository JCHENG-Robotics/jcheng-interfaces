# 契约原则（v0.1）

> v0.1 已定义：字段以 `ros2_ws/src/jcheng_interfaces/` 与 `schemas/` 为准。
> 本文件只记录不可协商的原则；审计与兼容性见
> [`CONTRACT_AUDIT.md`](CONTRACT_AUDIT.md) 与
> [`COMPATIBILITY.md`](COMPATIBILITY.md)。

## 1. 分层

| 层 | 载体 | 版本 |
|---|---|---|
| ROS IDL | `jcheng_interfaces` 包 | 契约哈希 + SemVer |
| HTTP/OpenAPI | `schemas/openapi/` | URL `/v1` |
| WebSocket | `schemas/ws/` | 协议版本字段 |
| Python | `jcheng_contracts` | 跟随契约 |
| TypeScript | 生成 | 跟随 OpenAPI（M2.3） |
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

## 3. 审计已决定

- `ArmMove` 立即弃用；如需要单步运动，用 `JOINT_STEP`（rad）。
- `ValidateTrajectory` 语义保留到 `ValidateMotion`，但删除调用方起点覆盖；
  `ValidationReport` 结构化，`report_json` 只作为可选诊断。
- 遥操作流 `TeleopCommand` 在 v0.1 预留，试点时启用。
- 夹爪契约正向 0–2.22 rad；URDF `r_joint` 负号由适配器转换。
- 底盘 duty 归一化 -1..1；厂商原始 duty 由适配器映射。
- HTTP 使用干净 `/v1`；旧 `/api/*` 由适配层处理。
- 操作者字段命名为 `operator_id`，避免 C++ 保留字 `operator`。
- 错误码以新注册表为准，旧码保留映射。

## 4. 离线工件契约（提议，未接受）

`jcheng-devices`、`jcheng-scenarios` 与 `jcheng-applications` 之间的
`device_snapshot.v1` / `scenario_requirements.v1` 语义已由
[`proposals/offline-artifact-contract-v1.md`](proposals/offline-artifact-contract-v1.md)
提议，状态为 **Proposed**：

- 工件 `content_hash` 是去掉自身字段后的 canonical JSON 自哈希；
- 源声明哈希单独存放（设备 `source_hash`、场景 `provenance.scenario_content_hash`）；
- 设备快照关节单位是度，运行时 recipe 是弧度；
- 角色组合缺失必需角色 fail closed，缺失设备事实为 `unverified`；
- `capability_satisfied` / `offline_execution_allowed` 不等于
  `deployment_ready` 或 `motion_authorized`；
- 未获批准前，能力词汇仍为 `local_draft`，不得称为正式公共标准。

接受条件与 golden vectors 见提案与
[`../tests/fixtures/offline_artifact_contract_v1.json`](../tests/fixtures/offline_artifact_contract_v1.json)。
