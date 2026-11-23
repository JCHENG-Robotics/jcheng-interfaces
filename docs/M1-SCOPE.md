# M1 范围

## 允许

- 仓库说明、契约审计计划、版本/兼容性文档。
- CI 骨架（`m1-gate`）。
- 目录占位（`ros2_ws/src`、`schemas`、`tests`）。
- 许可证审查状态说明。

## 不允许

- 任何 `.msg` / `.srv` / `.action`。
- ROS 包（`package.xml`、`CMakeLists.txt`）。
- JSON Schema / OpenAPI / WebSocket 最终定义。
- Python/TypeScript 绑定或生成代码。
- 从 `arm_interfaces` 或 Studio 复制代码。

## 出口条件

- `scripts/check_m1_gate.sh` 通过。
- CI `m1-gate` 通过。
- 没有 `LICENSE`（许可证审查 pending）。
- 契约审计计划已评审；M2 才能开始定义 IDL。

## M2 入口

- 完成 `docs/CONTRACT_AUDIT.md` 并签字。
- 确定 `jcheng_interfaces` 的消息/服务/action 清单。
- 确定与 `arm_interfaces`、Studio API、gateway 的兼容/弃用映射。
- 建立 `interface_manifest.json` 与契约哈希 CI。
