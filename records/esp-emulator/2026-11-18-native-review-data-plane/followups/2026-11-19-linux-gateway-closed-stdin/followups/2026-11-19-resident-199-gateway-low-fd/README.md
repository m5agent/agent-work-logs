# Device Service 1.99.0 网关低位描述符修复的常驻回读

- 日期为 2026-11-19（UTC+08:00），结果为 `LIVE_VERIFIED`。
- 工作类型为具备同路径虚拟设备验证的协调部署与独立回读。
- Device Service 常驻源码为 `981fdcdf09253b75be960772147258b677775d8c`，替代 `597e03214dc5f442787cec52f1720567e4ed2a00`。 [主分支源码](https://github.com/m5agent/m5stack-esp-emulator/commit/981fdcdf09253b75be960772147258b677775d8c)
- 环境为原生 macOS Device Service 两套角色和 Firmware Reviewer 0.27.0。

工作台和审核侧 Device Service 均恢复可用并接受租约。历史分别保留 55、98 条，Reviewer 保留 129 条历史及抽样证据。两个角色提供的 Device Service OpenAPI 身份一致，Reviewer 进程代码与就绪契约保持一致。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏回读摘要](evidence/resident-readback.summary.json)

[原版 CardputerDict 的隔离 Linux 验证](../../README.md)覆盖实际启动、拒绝与播放。本次常驻验证未启用 Linux 生产路由、未运行生产来宾，实体设备未运行。Burner 未提交。
