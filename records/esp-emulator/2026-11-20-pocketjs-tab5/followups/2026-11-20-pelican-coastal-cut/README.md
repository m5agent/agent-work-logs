# Pelican Dash 清晰度与骑行节奏复验

2026-11-20 · 工程报告 · `PARTIAL`

Pelican Dash 0.1.1 使用 12 张 512×256 的 RGB565 纹理并通过原版 Pocket M5 启动器运行。GT911 实际输入使 App 切换到 2× 并恢复 1×，MIPI-DSI 录得两档画面变化。宿主实录的两档节奏接近，成片保留输入及响应时序，仅对响应后原帧作变速比较。

- [复验方法与剪辑范围](report.md)
- [结构化记录](run.json)
- [脱敏证据摘要](evidence/virtual-device.summary.json)

此次采集在离线虚拟设备上执行，启动阶段通过一次软件复位恢复画面。真机、浏览器、联网及无干预冷启动尚未验收。
