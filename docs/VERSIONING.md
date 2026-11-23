# 版本策略

- `0.y.z`：初始开发期；任何 IDL 结构变化提升 minor，并改变契约哈希。
- `1.0.0` 起：
  - major：删除/重命名字段或消息、修改类型/单位/坐标系/语义、修改 action/srv 结构。
  - minor：新增消息/字段/服务/action/错误码；源码兼容，但 ROS 2 类型哈希变化。
  - patch：仅文档/注释/生成器修复；契约哈希不变。
- 运行时以 `contract_hash` 精确匹配为准；SemVer 只用于人类说明。
- 锁文件钉提交、标签、契约哈希、镜像摘要与机器人配置哈希。
- 详细规则见 `jcheng-manipulation/docs/ecosystem/05-versioning-lock-release.md`。

## 发布前检查

- [ ] `interface_manifest.json` 可重建且哈希一致。
- [ ] 与上一发布标签的 diff 符合 SemVer。
- [ ] JSON Schema / OpenAPI 通过校验。
- [ ] 与现有接口的兼容映射已更新。
