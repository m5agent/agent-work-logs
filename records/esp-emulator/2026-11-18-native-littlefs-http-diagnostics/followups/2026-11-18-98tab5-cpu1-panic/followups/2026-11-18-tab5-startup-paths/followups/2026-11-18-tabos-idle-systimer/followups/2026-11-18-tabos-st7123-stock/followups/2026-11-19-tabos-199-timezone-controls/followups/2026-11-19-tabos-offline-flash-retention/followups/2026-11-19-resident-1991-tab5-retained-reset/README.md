# Device Service 1.99.1 双角色常驻回读

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `LIVE_VERIFIED`
- 工作类型 `service_release`
- 环境 macOS 原生 Device Service 工作台和固件审核设备角色

两套常驻角色均已切换至主分支发布提交 `c9ec0f274579b78d87a4a301147f351e8b7a48fa`，各自通过 HTTP 200 提供 Device Service 1.99.1 OpenAPI，回读字节与发布契约一致。两套角色可接收租约，分别保留工作台 55 条和审核设备 98 条历史。Reviewer 0.28.0 使用原有源码和配置重新启动，保留 130 条任务历史及抽样证据 ZIP，实际 macOS 后端就绪。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏回读摘要](evidence/resident-1991-readback-summary.json)

[原版 Tab5 复位和停机持久化](../../README.md) · [回写未确认的复位拒绝](../2026-11-19-tabos-p4-reset-save-fence/README.md)

原版固件的功能验证在独立原生虚拟设备执行。此次常驻验证覆盖服务、契约和已有历史。生产来宾、真机、Linux 常驻路由和 Pages 发布均未执行。Burner 未提交。
