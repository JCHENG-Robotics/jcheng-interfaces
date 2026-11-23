# 契约审计计划（M2 门禁）

> 要求来源：用户附加约束 6。
> 目标：在 `jcheng-interfaces` 正式定版前，审计现有 `arm_interfaces`、
> Studio API、gateway 与安全执行路径，避免重复定义或破坏兼容性。
> 方法：只读审计 + 映射表 + 签字；不迁移现有代码。

## 1. 审计范围

### 1.1 `arm_interfaces`

| 文件 | 现状 |
|---|---|
| `ros2_ws/src/arm_interfaces/action/ArmMove.action` | Goal `target_angle`；Result `success/final_angle/message`；Feedback `current_angle`。仅 `arm_basics` 使用，归档学习路径。 |
| `ros2_ws/src/arm_interfaces/srv/ValidateTrajectory.srv` | Request `moveit_msgs/RobotTrajectory` + `max_start_state_distance_rad`；Response `approved/code/violations/report_json`。`armpi_safety` 唯一 server。 |

审计问题：

- `ArmMove` 是否废弃，还是用 `JOINT_STEP` 表达？
- `ValidateTrajectory` 的 `report_json` 是否保留？新契约是结构化字段还是 JSON 字符串？
- `max_start_state_distance_rad` 是否允许调用方覆盖？审计已发现它可放宽 0.08 rad 起点门限。
- `moveit_msgs` 依赖是否保留，还是改为自有 `JointTrajectory`？

### 1.2 Studio 后端 API

来源：`armpi-debug-studio/backend/app/api/routes.py` 与 `application/*_ops.py`。

审计问题：

- `/api/health`、`/api/state`、`/api/safety`、`/api/control/*`、
  `/api/motion/{preview,execute,stop}`、`/api/chassis/pulse`、`/api/events`、
  `/api/ws/*` 的字段与错误码。
- 租约/预览 token/幂等键/状态机语义是否进入新契约，还是由系统层内部保留？
- 响应体当前没有 `response_model`；新 OpenAPI 是否要补齐？
- 前端 token 查询参数、导出链接缺失 token 等历史问题是否在新 API 修复？

### 1.3 网关

来源：`armpi-debug-studio/ros2_gateway/armpi_debug_gateway/{server.py,node.py,motion.py,chassis.py}`。

审计问题：

- `/state` 的三层位置语义：`joints`（命令回显）、`measured`（命令缓存）、
  `actual`（`GetBusServoState` 实测）。
- `/motion/dispatch` 的请求字段（`joints`、`profile`、`fast`、`target_pulse`、
  `completion`）与 `/motion/status` 的响应。
- `/chassis/pulse` 的 duty 原始单位、方向符号、时长、标定失效。
- `/safety_stop` 的 Bool、TRANSIENT_LOCAL、上升沿锁存语义。
- 网关 token 鉴权与租约缺口（网关无 lease/session）。

### 1.4 安全执行路径

来源：`armpi_safety/policy.py`、`config/safety_limits.yaml`、
`backend/app/safety/*`、`ros2_gateway/motion.py`。

审计问题：

- 四套策略（MoveIt safety、后端 gate、网关 MotionGuard、fast CLI 自检）的检查项、
  顺序、错误码、锁存语义。
- `profiles.moveit/step/pose/fast` 的运行时消费者；哪些是文档/一致性检查。
- `ValidateTrajectory` 的起点/速率/工作空间/桌面检查；可被调用方放宽的字段。
- `/safety_stop` 的消费范围；缺失安全节点时是否 fail-open。
- 停止是否中止在飞轨迹/底盘；`UNKNOWN` 是否锁存。

## 2. 交付物

`docs/CONTRACT_AUDIT.md` 必须包含：

1. **字段清单**：每个现有接口的字段、类型、单位、坐标系、方向、QoS、file:line。
2. **重复/冲突矩阵**：同名不同义、同义不同名、单位/坐标系冲突。
3. **兼容映射**：旧接口 -> 新契约；可保留/需适配/需弃用。
4. **破坏性变更清单**：类型哈希、字段删除/重命名、语义变化。
5. **弃用计划**：`ArmMove`、`ValidateTrajectory`、`/safety_stop` 镜像、
   Studio 旧 API 的时间表与适配器。
6. **安全不变量**：新契约必须保留的检查与锁存语义。
7. **签字**：接口评审 + 系统负责人 + Owner。

## 3. 门禁

```text
docs/CONTRACT_AUDIT.md 存在且 status: approved
        │
        ▼
才能添加 .msg/.srv/.action 与最终 Schema
```

`scripts/check_m1_gate.sh` 在 M1 强制“没有 IDL”；M2 起改为
“有审计签字才允许 IDL”。

## 4. 兼容性原则

- 不为兼容而保留危险字段（例如可放宽起点的请求参数）。
- 旧接口通过系统层适配器映射，不把旧字段塞进新契约。
- 任何语义变化（单位、坐标系、完成判定、停止语义）都是 major。
- ROS 2 类型哈希对字段变化敏感；兼容性以契约哈希为准，不以版本号猜测。

## 5. 审计记录

| 项 | 状态 |
|---|---|
| `arm_interfaces` 审计 | 待做 |
| Studio API 审计 | 待做 |
| gateway 审计 | 待做 |
| 安全路径审计 | 待做 |
| 重复/冲突矩阵 | 待做 |
| 兼容/弃用计划 | 待做 |
| 签字 | 待做 |
