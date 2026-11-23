# 兼容性矩阵（v0.1）

> 审计已签字（2026-11-23）。完整字段级依据见
> [`CONTRACT_AUDIT.md`](CONTRACT_AUDIT.md) 第 7 节。

| 现有接口 | 新契约 | 关系 | 兼容性 | 处理 |
|---|---|---|---|---|
| `arm_interfaces/action/ArmMove` | 无 | 归档学习 | 不兼容 | 弃用；如需用 `JOINT_STEP` 表达 |
| `arm_interfaces/srv/ValidateTrajectory` | `ValidateMotion` | 语义保留、结构重做 | 载荷不兼容 | 适配器转换；删除调用方起点覆盖 |
| `moveit_msgs/RobotTrajectory` | `JointTrajectory` | 类型替换 | 不兼容 | 系统层适配器转换 |
| Studio `POST /api/motion/preview` | `POST /v1/motion/validate` | 预览/校验 | 语义变化 | 旧 API 适配或弃用 |
| Studio `POST /api/motion/execute` | `POST /v1/motion/execute` | 执行 | 需要租约/token | 旧后端降级为客户端 |
| Studio `/api/control/*` | `/v1/leases` | 控制权 | 语义变化 | 上移到系统层 |
| Studio `POST /api/motion/stop` | `POST /v1/motion/stop` | 停止 | 语义变化 | 软件停止，不要求租约 |
| Studio `POST /api/chassis/pulse` | `ExecuteMotion` `BASE_PULSE` | 底盘 | 单位变化 | 归一化 duty + profile |
| Studio `/api/state` | `/v1/state` | 状态 | 字段变化 | `truth`/`verification` 显式 |
| Studio `/api/ws/*` | `/v1/ws/*` | 实时 | 信封变化 | 版本化信封 |
| Gateway `/motion/dispatch` | 内部 | 硬件桥 | 不对外 | 仅系统层使用 |
| Gateway `/chassis/pulse` | 内部 | 硬件桥 | 不对外 | 仅系统层使用 |
| `/safety_stop`（Bool） | `SafetyState` | 停止 | 镜像期 | 双向镜像，新模块只读新契约 |
| `/joint_states` | `RobotState` | 遥测 | 语义变化 | 标 `commanded`；完成用总线 |
| 原始 `set_position` | 禁止 | 绕过 | 不兼容 | 仅硬件桥内部；guard 监控 |

## 破坏性点

- 新包/新类型：ROS 2 type hash 改变，消费者必须按锁文件重建。
- 单位规范化：全部 rad/m/s；`ArmMove` 的“度”语义不迁移。
- 删除调用方起点覆盖：`max_start_state_distance_rad` 不再出现。
- 真值/完成语义：`truth` 与 `verification` 必填；缓存不能作为完成依据。
- 停止语义：`SafetyState` 锁存 + 中止在飞 + 底盘归零。
- 执行必须持租约；gateway 直连路径不对外。
- 夹爪契约正向 0–2.22 rad；URDF `r_joint` 负号由适配器转换。
- 底盘 duty 归一化 -1..1；原始 duty 由适配器映射。
- 错误码统一注册表；旧码通过 `error-code-mapping.v1.json` 映射。

## 适配器状态

| 适配器 | 目标阶段 | 状态 |
|---|---|---|
| `ValidateTrajectory` -> `ValidateMotion` | M3 | 计划 |
| Studio `/api/*` -> `/v1/*` | M3/M5 | 计划 |
| `/safety_stop` 双向镜像 | M4 | 计划 |
| `/joint_states` -> `RobotState` 标注 | M3 | 计划 |
| 原始 pulse/寄存器隔离 | M3 | 计划 |
