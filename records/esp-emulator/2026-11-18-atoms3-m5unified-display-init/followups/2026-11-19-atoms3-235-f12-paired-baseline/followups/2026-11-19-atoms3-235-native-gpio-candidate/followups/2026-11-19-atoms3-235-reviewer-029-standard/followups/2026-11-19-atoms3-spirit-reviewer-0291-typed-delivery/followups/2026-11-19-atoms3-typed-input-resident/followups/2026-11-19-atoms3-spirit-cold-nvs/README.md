# AtomS3 Spirit Level 原版校准的冷启动恢复

- 日期 2026-11-19
- 结果 `PASS`，覆盖正常停机保存 Flash 后的校准与清零恢复。
- 工作类型 同版原生虚拟设备验证。
- 问题来源 [AtomS3 #235](https://github.com/m5agent/m5stack-esp-emulator/issues/235)与[常驻版本回读](../../README.md)。
- 源码版本 Device Service 1.99.3 `2a7f979c0c7e67420d8b790a3cfdb692702abf05`。
- 环境 隔离的 macOS 原生 AtomS3 `m5atoms3-st7735`，三个独立访客和同一份 Spirit Level v1.0.0 原版。

## 结果

首次启动在 +0.75g 的模拟倾斜下显示 +36.9°，GPIO41 请求按住 700 ms 后执行归零。认证导出停止后的 Flash，用新访客冷启动，显示平放 −36.9°、相同倾斜 −0.0°。随后 GPIO41 请求按住 2350 ms 触发清零。正常停止、再次导出并冷启动后，恢复平放 +0.0°、同一倾斜 +36.9°。

完整 OTA0 仍与原版规范化镜像相同。校准与清零快照的 82 个字节差异均位于 NVS，活动页、记录头和偏移数据 CRC 均通过。三个访客退出，保留停止历史，Flash 和活动租约已释放。本轮没有运行实机、物理断电、Reviewer 或生产固件。Burner 未提交。

[复验报告](report.md) · [运行记录](run.json) · [脱敏证据摘要](evidence/atoms3-spirit-cold-nvs.summary.json)
