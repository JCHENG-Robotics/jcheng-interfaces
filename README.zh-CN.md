# jcheng-interfaces

JCHENG Robotics 的统一接口契约仓库。

> 状态：**实验性** — v0.1.0（2026-11-23）。契约审计已签字；15 项契约测试通过；
> 已打签名标签 `v0.1.0`。不包含节点、硬件访问或厂商依赖。
> 本文为英文主文档的中文对照；如有歧义，以 [README.md](README.md) 为准。

## 1. 职责

- 一个 ROS 2 包 `jcheng_interfaces`：14 msg / 10 srv / 1 action。
- JSON Schema、OpenAPI `/v1`、WebSocket `/v1` 与错误码注册表。
- 纯 Python 契约绑定 `jcheng_contracts`。
- 契约哈希 `contract_hash` 与 `interface_manifest.json`。
- 兼容性检查与契约文档。

**不包含：** 节点、硬件访问、厂商依赖、业务逻辑。

## 2. 为什么先审计

现有基线已经有一套分散的接口：

- `arm_interfaces/action/ArmMove.action`、`srv/ValidateTrajectory.srv`。
- Studio 后端 `/api/*`（预览、执行、停止、租约、事件）。
- 网关 `/motion/*`、`/chassis/*`、`/state`、`/safety_stop`。
- `armpi_safety` 的 `ValidateTrajectory` 与 `/safety_stop` 消费语义。

如果直接定义新契约，容易重复命名、改变单位/坐标系、破坏兼容性或丢失安全语义。
因此 M1/M2 的门禁是：**先审计，后定版**。

- [契约审计计划](docs/CONTRACT_AUDIT_PLAN.md)
- [契约审计（M2.1，已签字）](docs/CONTRACT_AUDIT.md)
- [M1 范围](docs/M1-SCOPE.md)
- [M2 范围](docs/M2-SCOPE.md)
- [契约原则（v0.1）](docs/CONTRACT.md)
- [版本策略](docs/VERSIONING.md)
- [兼容性矩阵](docs/COMPATIBILITY.md)

## 3. v0.1 目录

```text
ros2_ws/src/jcheng_interfaces/    # 14 msg / 10 srv / 1 action
schemas/                          # JSON Schema / OpenAPI / WS / error codes
python/jcheng_contracts/          # Python 绑定与 manifest 工具
tests/                            # 契约/兼容性/parity 测试
tools/                            # manifest / schema / 硬件原语检查
interface_manifest.json           # 逐文件哈希 + 契约哈希
```

v0.1 已构建并通过 15 项本地契约测试；契约哈希由
`interface_manifest.json` 固定。TypeScript 绑定尚未生成（后续 M2.3 补充）。

## 4. 依赖

- ROS 2 Humble 或 Jazzy（CI 使用 Humble）
- Python ≥ 3.10：`jsonschema`、`PyYAML`、`pytest`（仅测试）
- 无硬件、无设备、无运行时节点

## 5. 快速开始

```bash
# 契约测试（纯 Python，无需 ROS）
python3 -m pytest -q

# 契约门禁
python3 tools/generate_manifest.py --check
python3 tools/check_schemas.py
python3 tools/check_no_hardware.py

# 构建 ROS 接口包
source /opt/ros/humble/setup.bash
colcon build --base-paths ros2_ws/src --packages-select jcheng_interfaces
source install/setup.bash
ros2 interface show jcheng_interfaces/msg/MotionCommand
```

`tools/generate_manifest.py --write` 在契约变更后重建清单；CI 用 `--check`
拒绝过期清单。

## 6. 约束

- 契约不提供原始舵机寄存器、任意占空比、直接厂商话题原语。
- 运动只通过 `ExecuteMotion`；状态必须标注 `truth` 与 `verification`。
- 契约变更先于消费者变更；运行时用契约哈希握手。
- 不修改 `jcheng-manipulation v1.0.0` 的标签、证据或实验历史。

## 7. 验证状态

| 结论 | 状态 | 证据 |
|---|---|---|
| IDL/Schema/OpenAPI/错误码 parity | 已验证（L0–L1） | 15 项契约测试；`contract-ci` |
| 契约哈希与清单一致 | 已验证（L0） | `interface_manifest.json`；`generate_manifest.py --check` |
| 无硬件原语/无运行时节点 | 已验证（L0） | `check_no_hardware.py`；仓库门禁 |
| TypeScript 绑定 | 未提供 | 计划在 M2.3 |

完整报告：[ACCEPTANCE.md](ACCEPTANCE.md)。

## 8. 相关仓库

- [`jcheng-system`](https://github.com/JCHENG-Robotics/jcheng-system) — 契约的主要运行时消费者。
- [`jcheng-mobile`](https://github.com/JCHENG-Robotics/jcheng-mobile)、
  [`jcheng-perception`](https://github.com/JCHENG-Robotics/jcheng-perception) — 能力仓库。
- [`.github`](https://github.com/JCHENG-Robotics/.github) — 生态路线图、变更日志与验收。

## 9. 许可

许可证审查进行中；本仓库没有 `LICENSE`，默认版权保留。
详见 [LICENSE-REVIEW.md](LICENSE-REVIEW.md) 与 `.github` 仓库的完整清单。
