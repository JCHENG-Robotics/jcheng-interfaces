# M2 范围

> 目标：在契约审计签字后，发布 `jcheng-interfaces` v0.1（IDL + Schema + 绑定 + CI）。
> 约束：不实现节点、不接触硬件、不迁移基线代码。

## M2.1 契约审计（当前）

交付：

- [`CONTRACT_AUDIT.md`](CONTRACT_AUDIT.md)：`arm_interfaces`、Studio API、
  gateway、安全执行路径的字段级盘点、冲突矩阵、兼容映射、破坏性变更、
  弃用计划与 v0.1 建议清单。
- 审计签字：接口评审 + 系统/安全评审 + Owner。

门禁：签字前不创建 `.msg/.srv/.action`、不写最终 Schema。

## M2.2 v0.1 契约

在审计签字后执行：

- `ros2_ws/src/jcheng_interfaces/`：一个 ROS 包，包含
  `ContractVersion`、`CapabilityManifest`、`SafetyState`、`ControlLease`、
  `MotionCommand`、`MotionFeedback`、`MotionResult`、`RobotState`、
  `JointTrajectory`、`JointTrajectoryPoint`、`BasePulse`、`GripperCommand`、
  `TeleopCommand`（预留）、`ValidationReport`；服务与 `ExecuteMotion`。
- `schemas/`：capability、robot-profile、safety-profile、evidence、
  acceptance、lockfile、error-codes、OpenAPI `/v1`、WebSocket `/v1`。
- `python/jcheng_contracts/`：版本、错误码、manifest、校验。
- `interface_manifest.json`：逐文件哈希 + 契约哈希 + ROS type hash。
- 与 `arm_interfaces`/Studio/gateway 的适配映射文档。

## M2.3 CI 与兼容性

- Humble + Jazzy 双发行版 `colcon build`。
- Schema meta-schema 校验；ROS IDL 与 JSON Schema 字段 parity。
- 契约哈希可重建；与上一标签的 diff 符合 SemVer。
- 硬件原语扫描：契约中不得出现原始 pulse/任意 duty/EEPROM 写入。
- `jcheng_contracts` 在 Python 3.10/3.11/3.12 导入通过。
- 示例请求/响应可被绑定解析。

## 不做

- 不实现 `jcheng_system` 节点、网关、硬件桥。
- 不修改 `jcheng-manipulation v1.0.0`。
- 不连接机器人、不发送运动命令。
- 不在审计签字前定义 IDL。

## 出口条件

- 审计签字完成。
- v0.1 包/ Schema /绑定/ manifest 可构建。
- CI 全绿；契约哈希稳定。
- 兼容/弃用映射已记录。
- 无运行时代码、无硬件依赖。
