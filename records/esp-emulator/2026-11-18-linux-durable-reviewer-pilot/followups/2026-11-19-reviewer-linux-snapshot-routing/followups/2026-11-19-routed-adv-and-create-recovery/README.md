# Reviewer 0.30 原版 ADV 路由与 Core2 创建响应丢失恢复

- 日期为 `2026-11-19`，原生 virtual-device validation，范围为同一托管 Linux 代次。
- 原版 ADV 发音路由终态为 `SIM_VERIFIED`，同库重开保留一条任务、21 条事件和证据。
- Core2 后端创建成功响应未送达，独立 Reviewer 被终止后，启动恢复找到并释放同一会话；原任务保留 `service_error / E_SERVICE_RESTART`。
- 最后六条历史会话均已停止，租约为零，临时角色卸载。未注入虚拟机或持久卷崩溃。

[报告](report.md) · [运行索引](run.json) · [有界证据](evidence/routed-adv-and-create-recovery.summary.json) · [先前路由资格验证](../../README.md)
