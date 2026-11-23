# 兼容性矩阵（模板）

> 契约审计签字前不填写最终结论。

| 现有接口 | 新契约 | 关系 | 兼容性 | 处理 |
|---|---|---|---|---|
| `arm_interfaces/action/ArmMove` | 待定 | 归档学习 | 不兼容 | 不迁移；如需用 `JOINT_STEP` 表达 |
| `arm_interfaces/srv/ValidateTrajectory` | 待定 | 语义保留 | 载荷不兼容 | 适配器转换 `moveit_msgs` |
| Studio `POST /api/motion/preview` | 待定 | 预览/校验 | 待审计 | 旧 API 适配或弃用 |
| Studio `POST /api/motion/execute` | `ExecuteMotion` | 执行 | 待审计 | 旧后端降级为客户端 |
| Studio `POST /api/control/*` | 租约服务 | 控制权 | 语义变化 | 上移到系统层 |
| Gateway `POST /motion/dispatch` | 内部 | 厂商桥 | 不对外 | 仅系统层使用 |
| Gateway `POST /chassis/pulse` | `BASE_PULSE` | 底盘 | 单位/边界待审计 | 归一化 + profile |
| `/safety_stop`（Bool） | `SafetyState` | 停止 | 镜像期 | 双向镜像，新模块只读新契约 |

## 待审计的破坏性点

- `ArmMove` 的 `target_angle` 单位（代码按“度”判断，文件未声明）。
- `ValidateTrajectory.max_start_state_distance_rad` 可放宽安全门限。
- `/joint_states` 与 `/controller_manager/servo_states` 的命令缓存语义。
- 夹爪 `r_joint` 的 URDF 负向与契约正向。
- 底盘原始 duty 与归一化 duty。
