# 契约审计：`arm_interfaces`、Studio API、gateway 与安全执行路径

> 状态：**M2.1 审计稿，待签字。**
> 基线：`jcheng-manipulation v1.0.0`（提交 `b3411e4`，2026-11-23）。
> 方法：只读源码、配置、测试与证据；不迁移代码，不修改基线。
> 门禁：本文件批准前，`jcheng-interfaces` 不定义最终 IDL/Schema。

## 1. 审计摘要

现有系统不是“没有接口”，而是**同一语义在四层里各有一套表达**：

1. `arm_interfaces` 只有两个类型：归档学习用的 `ArmMove.action` 与生产用的
   `ValidateTrajectory.srv`。
2. Studio 后端有一套 HTTP/WS 业务 API，租约、预览 token、幂等与安全 gate
   都在后端进程内。
3. 机器人端 gateway 有一套 HTTP 运动 API，但它**没有租约/会话概念**，
   只靠共享 token；持有 token 可直接下发运动。
4. 安全语义分散在 `armpi_safety`、后端 gate、gateway `MotionGuard` 和
   fast CLI 自检中；完成判定在“计时”“命令缓存”“总线实测”之间不一致。

结论：

- **`ArmMove` 不进入新契约**：它是归档学习产物，单位未声明，仅 `arm_basics`
  自用。
- **`ValidateTrajectory` 的语义保留，但接口必须重做**：调用方不能再放宽起点
  门限，速率必须与位置差分交叉校验，报告要结构化。
- **Studio `/api/*` 不逐字保留**：新契约为 `/v1/*`，旧后端在迁移期只做客户端/
  适配器。
- **gateway `/motion/*` 不作为外部契约**：它只属于系统层的硬件桥内部接口。
- **新契约必须比旧接口更严格**：总线实测、fail-closed、停止中止在飞执行、
  禁止原始寄存器/EEPROM 写入。

## 2. `arm_interfaces` 字段级盘点

### 2.1 `ArmMove.action`

来源：`ros2_ws/src/arm_interfaces/action/ArmMove.action:1-7`。

| 段 | 字段 | 类型 | 现有含义 | 问题 |
|---|---|---|---|---|
| Goal | `target_angle` | `float64` | 目标角度 | 文件未声明单位；`arm_move_server.cpp:39` 按“度”判断 `abs(angle) > 180` |
| Result | `success` | `bool` | 是否成功 | 纯软件仿真，无硬件语义 |
| Result | `final_angle` | `float64` | 最终角度 | 单位未声明 |
| Result | `message` | `string` | 文本 | 无结构化错误码 |
| Feedback | `current_angle` | `float64` | 当前角度 | 单位未声明 |

生产/消费方：

- 唯一 server/client 在 `ros2_ws/src/arm_basics`（`arm_move_server.cpp:18-23`、
  `arm_move_client.cpp:14`），是纯软件仿真，不发布硬件命令。
- `arm_basics` 不在 CI 的 7 包构建列表中，属于 8 周学习归档。

**审计决定：** 不迁移、不进入 `jcheng_interfaces`。如未来需要单步运动，用
`JOINT_STEP`（弧度）表达；不保留“度”的歧义。

### 2.2 `ValidateTrajectory.srv`

来源：`ros2_ws/src/arm_interfaces/srv/ValidateTrajectory.srv:1-17`。

| 段 | 字段 | 类型 | 现有含义 | 问题 |
|---|---|---|---|---|
| Request | `trajectory` | `moveit_msgs/RobotTrajectory` | 待校验轨迹 | 把 MoveIt 类型带入安全契约；新契约不应依赖 MoveIt |
| Request | `max_start_state_distance_rad` | `float64` | 0 表示用配置默认值 | **调用方可放宽** 0.08 rad 起点门限（`policy.py:491-496`） |
| Response | `approved` | `bool` | 通过/否决 | 可保留 |
| Response | `code` | `string` | 首个失败码 | 只有单个码，信息不足 |
| Response | `violations` | `string[]` | 人类可读违规 | 无机器可读结构 |
| Response | `report_json` | `string` | JSON 完整报告 | 无 Schema；消费者需自行解析 |

唯一 server：`armpi_safety`（`armpi_safety/node.py:96-100`）。
调用方：

- `armpi_grasp_planner`：可选（`--safety-service`，空则跳过）。
- `tools/phase2/real_moveit_execute.py`：默认强制。
- `tools/phase2/execute_plan_json.py`：强制。

现有检查（`armpi_safety/policy.py`）：

- 状态新鲜度 ≤0.5 s、五关节齐全、有限、限位。
- 轨迹形状、时间戳严格递增、时长 ≤30 s、点数 ≤5000。
- 每点位置限位；速度/加速度（显式值优先，否则差分）。
- 起点与最新状态差 ≤0.08 rad（可被请求覆盖）。
- TCP 工作空间包围盒；FK 不可用则 fail closed。
- TCP 桌面平面间隙 ≥10 mm。
- 失败码：`STATE_INVALID`、`JOINT_LIMIT`、`VELOCITY_LIMIT`、
  `ACCELERATION_LIMIT`、`TABLE_CLEARANCE`、`WORKSPACE`、`START_STATE`、
  `DURATION`、`TIMESTAMP`、`TRAJECTORY_INVALID`、`MULTIPLE`
  （`policy.py:805-822`）。

**审计决定：**

- 语义保留到 `ValidateMotion`，但：
  - 请求改为 `MotionCommand`（自有 `JointTrajectory`，不依赖 `moveit_msgs`）。
  - **删除调用方起点覆盖字段**；起点门限只由 profile 决定。
  - 显式速度/加速度必须与位置差分交叉校验；不接受“全填 0”绕过。
  - 结果使用结构化 `ValidationReport`；`report_json` 只作为可选诊断字段，
    不作为权威。
- 旧 `ValidateTrajectory` 由系统层适配器映射；基线仓库不改。

## 3. Studio 后端 API 盘点

来源：`armpi-debug-studio/backend/app/api/routes.py`、
`application/*_ops.py`、`domain/models.py`、`safety/*`。

### 3.1 认证、会话与权威

| 项 | 事实 | 证据 |
|---|---|---|
| 认证 | 可选 `ARMPI_BACKEND_TOKEN`；`/api/health` 豁免；`X-Armpi-Token` 或 `?token=`；`hmac.compare_digest` | `main.py:148-176` |
| 用户/角色 | 无；`session_id` 是客户端 localStorage 随机 UUID | `frontend/src/session.ts:1-10` |
| 绑定 | 默认 `127.0.0.1:8000`；非 loopback 必须给 token | `config.py:71-78` |
| 租约 | 进程内单租约；默认 60 s；任务可请求 600 s；20 s heartbeat；**无 revoke 路由** | `safety/lease.py:36-121` |
| 预览 token | 30 s、单次、绑定命令哈希；刻意排除 `from_rad` 与 profile 时长 | `safety/tokens.py:42-77`、`service.py:575-595` |
| 幂等 | 300 s、进程内；同 key 不同载荷 409 | `service.py:76,602-627` |
| 权威范围 | 只覆盖“经过后端”的调用；gateway 无租约，直连可绕过 | `gateway/motion.py`、`server.py:225-251` |

### 3.2 路由清单（分组）

| 组 | 方法/路径 | 作用 |
|---|---|---|
| 只读 | `GET /api/health`、`/state`、`/connection`、`/safety`、`/diagnostics` | 健康、状态、连接、安全检查、诊断 |
| 外设 | `GET /api/peripherals`、`/peripherals/camera/snapshot`、`/peripherals/aux-camera/snapshot` | 电池、主相机、D435i 辅助画面 |
| 控制权 | `POST /api/control/acquire`、`/heartbeat`、`/release` | 租约 |
| 运动 | `POST /api/motion/preview`、`/motion/execute`、`/motion/stop` | 预览 token、执行、软件停止 |
| 任务 | `POST /api/task/plan`、`/task/verify` | G8 计划、夹持验证 |
| 底盘 | `POST /api/chassis/pulse` | 开环脉冲 |
| 审计 | `GET /api/events`、`/events/export.csv` | 只追加事件 |
| 离线 | `GET/POST /api/trajectories*`、`/experiments*`、`/visual*` | G2/G3/G4 |
| 实时 | `WS /api/ws/state`、`/api/ws/events` | 10 Hz 状态、事件流 |

### 3.3 请求模型

| 模型 | 字段 | 约束/说明 |
|---|---|---|
| `TargetIn` | `joint`、`target_rad`、`duration_s` | joint 1–64；rad；时长 float |
| `ProfileIn` | `vmax_rad_s`、`amax_rad_s2`、`dt_s` | (0,4.0]、(0,20]、[0.025,0.5] |
| `PreviewIn` | `session_id`、`targets[1..12]`、`profile?`、`fast` | session 1–128 |
| `ExecuteIn` | 继承 `PreviewIn` + `lease_id`、`preview_token`、`command_id`、`idempotency_key?` | 执行必需 token |
| `LeaseIn` | `session_id`、`ttl_s?` | ttl 1–3600 |
| `HeartbeatIn` | 继承 `LeaseIn` + `lease_id` | 续租 |
| `ReleaseIn` | `lease_id`、`session_id` | 释放 |
| `StopIn` | `session_id`、`lease_id?`、`command_id?` | stop 不要求租约 |
| `ChassisPulseIn` | `session_id`、`lease_id`、`vx`、`vy`、`duty`、`duration_s` | 无 Pydantic 范围，服务层再校验 |

### 3.4 响应模型

| 模型 | 关键字段 |
|---|---|
| `Health` | `status`、`mode`、`version`、`schema_version`、`source_label`、`capabilities` |
| `RobotState` | `robot_id`、`mode`、`connection_state`、`source_label`、`control_owner`、`received_at`、`monotonic_ms`、`ros_time_ns`、`joints[]`、`faults[]`、`mapping_version`、`limit_version`、`mapping_verified`、`capabilities`、`stop_state`、`last_command_id`、`gripper` |
| `JointState` | `name`、`servo_id`、`target_rad/raw`、`position_rad/raw`、`truth`、`validity`、`sample_age_ms`、`source`、限位、`limit_verified` |
| `GripperState` | `joint`、`servo_id`、`available`、`target/position`、`truth/validity`、`min_rad/max_rad`、`open_raw/close_raw`、`measured_min/max_raw`、`completion="timed"`、`notes` |
| `SafetyReport` | `ready`、`checks[]`（`check_id/label/passed/blocking/detail/severity`）、`blockers`、`warnings`、`mode`、`generated_at` |
| `PreviewResult` | `command_id`、`session_id`、`valid`、`targets`、`errors`、`warnings`、`preview_token`、`expires_at`、`mapping_version`、`evaluated_at`、`pose` |
| `CommandRecord` | `command_id`、`session_id`、`status`、`targets`、`created_at`、`updated_at`、`error_code`、`details`、`stage_history` |
| `StopResult` | `state`、`command_id`、`detail`、`evidence`、`requested_at`、`observed_at` |
| `ConnectionReport` | `segments[]`、`serial_available`、`driver_online`、`gateway_online`、`feedback_fresh`、`notes` |

### 3.5 命令状态机

`Requested → Validated → Dispatched → Observed → Completed`；
`Failed`/`Unknown` 分支；`Acknowledged` 明确不可达；`Dispatched → Completed`
非法（`domain/state_machine.py:21-34`）。

执行写入顺序（`application/motion_ops.py:190-443`）：

```text
lease.check
  → validate targets
  → pose gate
  → consume preview token
  → command/session ownership
  → safety supervisor gate
  → adapter dispatch
  → state transitions
```

### 3.6 后端安全 gate

`SafetySupervisor.evaluate` 的阻塞项（`safety/supervisor.py:70-325`）：

`mode_supported`、`gateway_online`、`driver_online`、`feedback_fresh`、
`mapping_loaded`、`mapping_verified`、`control_lease`、`no_active_fault`、
`not_executing`、`hardware_motion_enabled`、`joints_available`、
`stop_state_clear`。

警告项：`supervised_commissioning`、`pose_takeover`、`measured_feedback`、
`gripper_feedback`。

已知缺口：

- 后端不订阅 `/safety_stop`；硬件快照 `stop_state` 固定 `None`
  （`adapters/hardware.py:765`），因此 `stop_state_clear` 在硬件上恒通过。
- 租约只在后端进程内；gateway 不识别租约/session。
- FK/工作空间/桌面/低姿态 yaw 只在后端（`safety/pose_gate.py:106-238`）。
- `revoke()` 存在但没有路由暴露（`safety/lease.py:113-115`）。
- 预览 token 绑定 `mapping_version/hash`，但 gateway 不校验映射版本。

## 4. Gateway 盘点

来源：`armpi-debug-studio/ros2_gateway/armpi_debug_gateway/`。

### 4.1 传输与认证

| 项 | 事实 |
|---|---|
| 框架 | 纯 Python `ThreadingHTTPServer`；无 WebSocket/SSE/ROS action |
| 端口 | 8765 只读（systemd 常驻）；8766 pose/motion（默认禁用，手动启动） |
| 认证 | 共享 `X-Armpi-Token`；`hmac.compare_digest`；非 loopback 无 token 拒绝启动 |
| 传输 | 明文 HTTP；无 TLS/CORS/每 IP 限流；body ≤256 KiB |
| 运动启用 | 必须同时有 token、`--enable-motion`、`--motion-config` |

### 4.2 路由

| 方法/路径 | 作用 |
|---|---|
| `GET /health`、`/state`、`/battery`、`/camera/*`、`/aux-camera/*`、`/tf` | 只读遥测 |
| `GET /pointcloud/meta`、`/pointcloud` | 一次性点云抓取 |
| `GET /motion/status` | `MotionGuard` 状态、limits、measured |
| `POST /motion/dispatch` | 机械臂/夹爪/密集 profile 命令 |
| `POST /motion/stop` | 机械臂 hold |
| `POST /chassis/pulse` | 四通道底盘脉冲 |

### 4.3 `/state` 的三层位置语义

| 字段 | 来源 | truth | 说明 |
|---|---|---|---|
| `joints` | `/joint_states`/`controller_manager` | `commanded` | 命令回显 |
| `measured` | `/controller_manager/servo_states` | `commanded` | 厂商命令缓存，不是总线读数 |
| `actual` | `GetBusServoState` | `measured_on_demand` | 真实总线读数 |

响应还包含 `measured_ready`、`measured_truth: "commanded"`、`actual_source`、
`truth: "commanded"` 与 notes（`gateway/node.py:486-518`）。

### 4.4 `/motion/dispatch` 请求

| 字段 | 规则 |
|---|---|
| `command_id` | 必需、≤128 |
| `duration_s` | 有限；普通命令在 `[min_duration, max_duration]`；profile 可短于单命令下限 |
| `joints[]` | 非空；step 恰好 1 个；pose 恰好 5 臂关节或恰好 1 个夹爪；不能混用 |
| `joints[].joint` | 必须在配置关节内 |
| `joints[].servo_id` | 必须匹配配置 |
| `joints[].target_pulse` | 整数，在 min/max 内 |
| `joints[].target_rad` | 与 pulse 一致（误差 ≤1.5 pulse） |
| `joints[].completion` | `position` 或 `timed` |
| 测量反馈 | 必须有 `raw_position`，年龄 ≤`feedback_max_age_ms` |
| `profile` | 逐段 0.025–0.5 s、≤400 点、总 ≤6 s；首段起点、速度、加速度、末点校验 |
| `fast` | 允许快速夹爪时序 |

响应：`status=dispatched`、`command_id`、`mode`、`duration_s`、
`position_unit=pulse`、`topic`、`verification=pending|cache`、`profile`、
`fast`、`joints[]`、`measured`、`published_at`
（`gateway/node.py:668-703`）。

### 4.5 执行档

| 档 | 机制 | 完成判定 |
|---|---|---|
| step | 单关节；导出默认 0.10 rad/1.0 s/只允许单关节；网关硬上限 0.35 rad | 总线 ±8 脉冲 |
| pose | 5 臂关节或单夹爪；0.5 rad/s；`max_step_rad` 可到 3.61（全行程跨度） | 总线 12 脉冲 |
| fast | 4.0 rad/s、20 rad/s²、≤400 点、总 ≤6 s | 总线读数 + 稳定判据 |
| gripper | 原始 pulse + timed 完成；速度 100–120 raw/s | 总线读数 |

### 4.6 `/chassis/pulse`

请求 `vx`、`vy`、`duty`、`duration_s`；响应包含 `status`、
`verification=open_loop`、`topic`、`mode`、`wheels`、`nominal_travel_mm`、
`subscribers_matched`、`messages`、`elapsed_s`、`started_wall`、`ended_wall`。
Studio 上限 duty ≤10、0.2–2.0 s；网关硬上限 duty ≤20、wheel ≤30、≤3.0 s。

### 4.7 `/safety_stop`

`std_msgs/Bool`，`TRANSIENT_LOCAL`；gateway 在上升沿锁存 `MotionGuard`、
发布机械臂 hold、拒绝新命令。**不中止在飞 dense profile/底盘脉冲**；
只有 gateway 消费，fast CLI/raw-bus 不消费。

### 4.8 错误码族

- `MOTION_BAD_REQUEST`、`MOTION_BUSY`、`MOTION_DISABLED`、
  `MOTION_FAST_DISABLED`、`MOTION_PROFILE_DISABLED`、
  `MOTION_PROFILE_START`、`MOTION_PROFILE_VELOCITY`、
  `MOTION_PROFILE_ACCEL`、`MOTION_STALE_FEEDBACK`、`MOTION_OUT_OF_LIMIT`、
  `MOTION_STEP_EXCEEDED`、`MOTION_VELOCITY_EXCEEDED`、
  `MOTION_SCHEMA_VERSION`、`MOTION_SERVO_IDS`、`MOTION_MODES`。
- `CHASSIS_BAD_REQUEST`、`CHASSIS_BUSY`、`CHASSIS_DISABLED`、
  `CHASSIS_DUTY`、`CHASSIS_WHEEL_DUTY`、`CHASSIS_DURATION`、
  `CHASSIS_UNMATCHED`。

### 4.9 已知缺口

- 没有租约/session；共享 token 可直接运动。
- `--motion-config` 路径任意；网关只做结构校验。
- pose 的 `max_step_rad=3.61` 是全行程跨度，不是小步限幅。
- 无 FK/工作空间/桌面门禁；直连网关可绕过。
- `/safety_stop` 不中止在飞执行；gateway 在安全节点缺失时 fail-open。
- 完成判定依赖 `GetBusServoState`，但状态流本身是缓存。

## 5. 安全执行路径盘点

### 5.1 路径表

| # | 路径 | 入口 | 守卫 | 完成判定 | 主要缺口 |
|---|---|---|---|---|---|
| 1 | MoveIt CLI | `real_moveit_execute.py`、`execute_plan_json.py` | `ValidateTrajectory`（必需） | MoveIt controller 定时 `succeed()`，不读总线 | 完成不是总线确认；仅工具强制 |
| 2 | Fast CLI | `fast_motion.py`、`fast_motion_e2e.py` | 无 `armpi_safety`；S 曲线 + joint2 边界 + 总线 settle | 总线 settle | `--vmax` 无硬上限；绕过安全 |
| 3 | Studio G6 step | 后端 → gateway `/motion/dispatch` | 后端租约/token；gateway motion policy | 总线 ±8 | 直连 gateway 可绕过后端 |
| 4 | Studio G7 pose | 后端 → gateway pose scope | 后端 FK/桌面/yaw；gateway 关节/速度 | 总线 12 | gateway 无 FK/桌面门禁 |
| 5 | Studio G8 task/fast | 后端 `/task/plan` + `/motion/execute` | 后端 profile + gateway profile | 总线 + 稳定 | 停止不中止在飞 |
| 6 | Chassis pulse | gateway `/chassis/pulse` | gateway chassis policy | `open_loop` | 无里程计；停止不归零在飞 |
| 7 | 脚本直写 | `pulse_move.py`、`servo_hold.py`、`joint_limit_survey.py` 等 | 仅脚本自检 | 总线 read | 无统一守卫 |
| 8 | 厂商直发 | `/grasp`、手柄、`/cmd_vel`、`startup_check` | 无 | 厂商行为 | 软件层无法否决 |

### 5.2 `armpi_safety` 检查

- 状态新鲜度 0.5 s、五关节齐全、有限、限位。
- 轨迹形状/时间戳/时长/点数。
- 每点位置限位；速度/加速度（显式优先，否则差分）。
- 起点 0.08 rad（可被请求覆盖）。
- TCP 工作空间；FK 不可用 fail closed。
- TCP 桌面间隙 10 mm。
- 锁存只对“已收到过状态”的违规生效；被拒绝的轨迹不锁存。
- 启动时无状态会发布 `stop=true` 但不锁存。
- 只否决 MoveIt CLI；不执行、不发布硬件命令。

### 5.3 后端 gate

见 3.6。关键点：`stop_state` 在硬件快照恒为 `None`，`/safety_stop` 不在环；
FK/桌面门禁只在后端。

### 5.4 Gateway `MotionGuard`

- 单条 arm 命令串行；`MOTION_BUSY`。
- `/safety_stop` 锁存拒绝新命令。
- measured 年龄 ≤500 ms。
- step/速度/pose 关节集合/profile 逐段校验。
- 完成：`GetBusServoState` 容差；失败 `unknown`。
- 无租约；不校验来源。

### 5.5 Fast CLI 与底盘

- `fast_motion.py` 直接发 `/arm_controller/follow_joint_trajectory`；夹爪 raw
  `/ros_robot_controller/bus_servo/set_position`；默认 4.0/20，`--vmax` 无硬上限。
- 底盘 20 Hz duty 脉冲后发零；无交叉互锁；停止不归零在飞脉冲。
- 厂商 `startup_check`、`/grasp`、手柄均无统一守卫。

### 5.6 停止、复位与未知

- 停止是“保持/置零”，不是急停；UI 只写“停止请求”。
- `MOTION_OUTCOME_UNKNOWN` 在后端可锁存；dispatch 超时路径不一定锁存。
- gateway `mark_verified` 失败只置 `unknown` 并清空 active；无独立锁存。
- 无硬件急停/抱闸/独立编码器/自碰撞模型。

## 6. 重复/冲突矩阵

| 概念 | 现有位置 | 冲突 | 新契约决定 |
|---|---|---|---|
| 角度单位 | `ArmMove.target_angle`（度）、`target_rad`、pulse | 度/rad/pulse 混用 | 契约统一 rad；pulse 只在硬件适配器 |
| 关节限位 | xacro、MoveIt `joint_limits.yaml`、`safety_limits.yaml`、`joint_mapping.yaml`、`takeover.yaml`、`vendor_servo_map.py` | 多文件重复 | 单一 robot profile + 生成 + 哈希 |
| step 上限 | safety 0.35、gateway 导出 0.10、pose 3.61 | 同名不同值 | 命名 profile + 路径绑定 + 生成 |
| 速度/加速度 | MoveIt 1.2/0.5、pose 0.5、fast 4.0/20 | 多档混用 | `moveit/step/pose/fast` 命名 profile |
| 伺服 ID | `vendor_servo_map.py`、`bus_pulses.py`、gateway `motion.py`、后端 `takeover.py`/`task.py` | 多处复制 | robot profile 单一来源 |
| 夹爪 | raw 170/700、measured 167/640、URDF -2.22..0、takeover open/close | 符号/单位冲突 | 契约正向 0–2.22 rad；适配器映射 |
| 底盘 duty | Studio 10、gateway 20、`mecanum` 60 | 原始 duty 混用 | 契约归一化 -1..1；profile 上限 |
| 真值 | `joints`/`measured`/`actual`、`truth` 枚举 | 缓存冒充实测 | `truth=measured|commanded` 必填 |
| 完成 | timed、cache、bus、open_loop | 语义不一致 | `verification=bus|timed|open_loop` 必填 |
| 停止 | Bool `/safety_stop`、`stop_motion` hold、`StopState` | 只阻止新命令 | `SafetyState` + 中止在飞 + 底盘归零 |
| 租约 | 后端进程内单租约；gateway 无 | 直连可绕过 | 系统级 `ControlLease` |
| 错误码 | `ErrorCode`、`MOTION_*`、`CHASSIS_*`、safety codes | 多套命名 | 统一 `error-codes` 注册表 + 映射 |
| 版本 | `mapping_version`、`limit_version`、profile 文件 | 无运行时握手 | `contract_hash` + `profile_hash` |

## 7. 兼容性映射

| 现有 | 新契约 | 关系 | 处理 |
|---|---|---|---|
| `ArmMove.action` | 无 | 归档学习 | 弃用；不迁移；如需要 `JOINT_STEP` |
| `ValidateTrajectory.srv` | `ValidateMotion.srv` | 语义保留、结构重做 | 适配器转换；删除调用方起点覆盖 |
| `moveit_msgs/RobotTrajectory` | `JointTrajectory` | 类型替换 | 系统层适配器转换 |
| Studio `POST /api/motion/preview` | `POST /v1/motion/validate` | 预览 | 旧 API 适配或弃用 |
| Studio `POST /api/motion/execute` | `POST /v1/motion/execute` | 执行 | 旧后端降级为客户端 |
| Studio `/api/control/*` | `/v1/leases` | 控制权 | 上移到系统层 |
| Studio `POST /api/motion/stop` | `POST /v1/motion/stop` | 停止 | 软件停止，不要求租约 |
| Studio `POST /api/chassis/pulse` | `ExecuteMotion` `BASE_PULSE` | 底盘 | 归一化 duty + profile |
| Studio `/api/state` | `/v1/state` | 状态 | `truth`/`verification` 显式 |
| Studio `/api/ws/*` | `/v1/ws/*` | 实时 | 版本化信封 |
| Gateway `/motion/dispatch` | 内部 | 硬件桥 | 不作为外部契约 |
| Gateway `/chassis/pulse` | 内部 | 硬件桥 | 不作为外部契约 |
| `/safety_stop` Bool | `SafetyState` | 停止 | 迁移期双向镜像；新模块只读新契约 |
| `/joint_states` | 遥测 | 缓存 | 标 `commanded`；完成用总线 |
| 原始 `set_position` | 禁止 | 绕过 | 仅硬件桥内部；guard 监控 |

## 8. 破坏性变更与 ROS 类型哈希

1. **新包、新类型**：`jcheng_interfaces` 与 `arm_interfaces` 不共享类型；
   任何字段变化都会改变 ROS 2 type hash，消费者必须按锁文件重建。
2. **单位规范化**：所有关节/位姿使用 rad/m/s；删除“度”语义。
3. **删除调用方放宽**：`max_start_state_distance_rad` 不再出现；起点门限由
   profile 固定。
4. **真值语义**：`truth` 与 `verification` 成为必填；缓存不能作为完成依据。
5. **停止语义**：`SafetyState` 锁存 + 中止在飞 + 底盘归零；旧 Bool 只是镜像。
6. **租约必需**：执行路径必须有租约；直连 gateway 的内部接口不对外。
7. **权限/安全**：不提供原始 pulse、任意 duty、EEPROM/力矩写入。
8. **错误码**：统一注册表；旧码保留映射，不保证文本一致。
9. **`ArmMove` 弃用**：不进入新契约。
10. **`ValidateTrajectory` 弃用**：新系统只使用 `ValidateMotion`。

## 9. 弃用与迁移计划

| 阶段 | 动作 |
|---|---|
| M2 | 本审计签字；定义 `jcheng_interfaces` v0.1；不修改基线 |
| M3 | 系统 Mock 栈；实现 `ValidateTrajectory`/Studio API 适配器（只读/测试） |
| M4 | 机器人只读接入；`/safety_stop` 镜像；旧 gateway 只读 |
| M5–M6 | 新系统执行；旧 gateway 降为只读回滚路径；Studio 后端改为客户端 |
| M7 | 首个能力模块；确认无旧 API 依赖 |
| M8 | 移除旧适配器；`arm_interfaces` 不再被新系统使用；基线保持只读 |

不修改 `jcheng-manipulation v1.0.0` 的标签、证据或实验历史。

## 10. 新契约必须保留/加强的安全不变量

1. 单一运动入口 `ExecuteMotion`；能力模块只提交意图。
2. 每次执行需要有效租约；作用域/优先级/TTL/deadman 可审计。
3. 安全节点只否决/锁存，不执行运动。
4. 总线实测是完成判定的唯一依据；缓存只能标 `commanded`。
5. 安全心跳缺失/过期即 `STOP_LATCHED`，禁止 fail-open。
6. 停止中止在飞轨迹/底盘脉冲；底盘归零、机械臂保持。
7. 校验不能被调用方放宽；显式速率与位置差分交叉校验。
8. 配置/profile/契约哈希不匹配：拒绝使能。
9. 未知结果锁存；总线复核后才能复位。
10. 不提供原始 pulse、任意 duty、EEPROM/力矩写入。
11. MoveIt 只规划；控制器执行链路不作为第二入口。
12. 厂商启动检查/`/grasp`/手柄不在生产路径；guard 检测。

## 11. v0.1 建议清单（待审计签字后定稿）

### 11.1 消息

`ContractVersion`、`CapabilityManifest`、`SafetyState`、`ControlLease`、
`MotionCommand`、`MotionFeedback`、`MotionResult`、`RobotState`、
`JointTrajectory`、`JointTrajectoryPoint`、`BasePulse`、`GripperCommand`、
`TeleopCommand`（预留）、`ValidationReport`。

### 11.2 服务

`AcquireLease`、`RenewLease`、`ReleaseLease`、`RevokeLease`、
`ValidateMotion`、`GetSafetyState`、`ResetSafety`、`ArmSystem`、
`DisarmSystem`、`GetCapabilities`。

`ValidateMotion` 响应建议：

```text
bool approved
string reason_code
string[] violations
ValidationReport report
string validation_id
builtin_interfaces/Time expires_at
```

`ValidationReport` 建议字段：`schema_version`、`approved`、`reason_code`、
`check_ids[]`、`violations[]`、`duration_s`、`point_count`、
`workspace_checked`、`table_checked`、`max_velocity_rad_s`、
`max_acceleration_rad_s2`、`checked_at`。不再依赖无 Schema 的 `report_json`。

### 11.3 Action

`ExecuteMotion`：goal `MotionCommand`；result `MotionResult`；
feedback `MotionFeedback`。

### 11.4 Schema 与绑定

`capability-manifest`、`robot-profile`、`safety-profile`、
`evidence-record`、`acceptance-report`、`lockfile`、`error-codes`、
OpenAPI `/v1`、WebSocket `/v1`、`jcheng_contracts` Python 包。

### 11.5 明确不进入契约

- 原始舵机 pulse/寄存器/EEPROM。
- 任意电机 duty（只允许 profile 边界内的 `BasePulse`）。
- 直接厂商话题。
- 绕过租约的调试执行。
- `moveit_msgs` 类型（由适配器转换）。

## 12. 开放问题

1. `ValidationReport` 结构化字段是否足够替代 `report_json`？是否保留
   `report_json` 作为可选诊断？
2. `ArmMove` 是否立即标记弃用（推荐），还是保留一个适配器？
3. `POSE` 的 `frame_id` 默认 `base_link`、`tip_link` 必填，是否同意？
4. 夹爪契约使用正向 0–2.22 rad（推荐），还是归一化 0–1？
5. 底盘 duty 使用归一化 -1..1（推荐），还是原始 duty？
6. 遥操作流契约在 v0.1 定义、试点时启用，是否同意？
7. HTTP 新 API 用 `/v1` 干净路径（推荐），还是保留 `/api` 兼容前缀？
8. 租约优先级值 100/60/40/20/10 是否固定，还是可配置？
9. 错误码是保留旧码做别名（推荐），还是只保留新码 + 映射表？
10. `RobotState` 是否包含相机/电池状态，还是只保留运动与安全状态？

## 13. 签字

| 角色 | 姓名/账号 | 结论 | 日期 |
|---|---|---|---|
| 契约整理 | JCHENG Robotics 工程会话 | 提交审计稿 | 2026-11-23 |
| 接口评审 | `JerichoCheng` | 待签字 | |
| 系统/安全评审 | `JerichoCheng` / `JerichoSwaine` | 待签字 | |
| Owner 批准 | `JerichoCheng` | 待签字 | |

**签字前不创建 `.msg`/`.srv`/`.action` 或最终 Schema。**
