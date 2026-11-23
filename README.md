# jcheng-interfaces

JCHENG Robotics 的统一接口契约仓库。

> 状态：**M2 v0.1 定义中；M2.1 审计已签字（2026-11-23）。**
> `jcheng_interfaces` ROS 包与 v0.1 Schema 正在本分支实现；审计见
> [`docs/CONTRACT_AUDIT.md`](docs/CONTRACT_AUDIT.md)。

## 1. 职责

- 一个 ROS 2 包 `jcheng_interfaces`（v0.1）。
- JSON Schema、OpenAPI、WebSocket 协议。
- 纯 Python 契约绑定 `jcheng_contracts`（M2）。
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

## 4. 约束

- 契约不提供原始舵机寄存器、任意占空比、直接厂商话题原语。
- 运动只通过 `ExecuteMotion`；状态必须标注 `truth` 与 `verification`。
- 契约变更先于消费者变更；运行时用契约哈希握手。
- 不修改 `jcheng-manipulation v1.0.0` 的标签、证据或实验历史。

## 5. 许可

许可证审查进行中；本仓库没有 `LICENSE`，默认版权保留。
详见 [LICENSE-REVIEW.md](LICENSE-REVIEW.md) 与 `.github` 仓库的完整清单。
