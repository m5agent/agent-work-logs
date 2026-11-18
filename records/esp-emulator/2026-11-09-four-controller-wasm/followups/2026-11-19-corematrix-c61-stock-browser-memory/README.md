# CoreMatrix C61 原版浏览器内存读回

- 日期 `2026-11-19`（UTC+08:00）
- 结果 本地浏览器启动和 32 KiB 读写对照 `PASS`，8 MiB PSRAM `NOT VALIDATED`
- 环境 本地导出的浏览器页面、Chromium、C61 QEMU WASM、CoreMatrix 官方 UIFlow2 v2.5.4 原版
- 工作类型 虚拟设备验证

同一原版在 16×16 矩阵输出 36 个非黑像素的启动图案。通过页面编辑器向该会话的 USB Raw REPL 发送试验程序，32 KiB 普通缓冲区的 8 个采样页回读无误。普通 1 MiB 缓冲区报 `MemoryError`，SPI RAM 能力查询返回空列表。当前结果覆盖该固件在这套运行时公开的堆行为，外部 PSRAM 的容量与读写路径仍待验证。

浏览器独立观察到 1 个引擎 Worker 和 4 个 pthread Worker。停止后活跃 Worker 为零，界面 iframe 已移除。

[报告](report.md) · [结构化记录](run.json) · [脱敏证据](evidence/corematrix-stock-browser-memory.summary.json) · [前次同板型浏览器验证](../../README.md)

本地导出浏览器为本轮执行范围。当前托管站、原生 Device Service、板上按键与真机均未执行。Burner 未提交。
