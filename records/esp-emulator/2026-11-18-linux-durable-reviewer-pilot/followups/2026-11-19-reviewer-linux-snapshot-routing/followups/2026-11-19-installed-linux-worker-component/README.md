# 可安装 Linux worker 组件的原版 Core2 验证

- 日期为 `2026-11-19`，原生 virtual-device validation。
- 独立安装的组件运行原版 Core2 2048，完成八次合法移动、覆盖四个方向，终态为 `SIM_VERIFIED`。
- 同卷两代正常关闭并重启读取，七个保留证据载荷逐字节一致，租约为零、临时角色已卸载。
- 首次重启预检因无实际监听时的 bind 失败而拒绝，修正后的安装命令复验通过；该次失败保留。
- 最终本地实现提交为 `5eacb1b7ae76d8bc3764caa7b45b23185f553ebe`。生产切换与其他原版应用在本安装上的验证为 `NOT RUN`。

[报告](report.md) · [运行索引](run.json) · [有界证据](evidence/installed-linux-worker-component.summary.json) · [此前受管路由验证](../../README.md)
