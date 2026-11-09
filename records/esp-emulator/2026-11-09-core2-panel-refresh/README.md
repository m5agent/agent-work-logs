# Core2 原生模拟器显示刷新与触摸回归

- 日期 `2026-11-09`
- 结果 `PARTIAL`，原生候选构建、显示及触摸回归通过，范围见下文
- 工作类型 `code_change`
- 问题来源 Core2 的高频 SPI 写入可重复触发整屏宿主刷新
- 源码基线 `m5agent/m5stack-esp-emulator@70ca46258598294eb5e5852115b1dfce386d8754`，候选为补丁 `0167-core2-panel-refresh.patch`
- 环境 macOS arm64、原生 QEMU、Device Service、官方 Core2 UIFlow2 v2.5.4 与同一测试脚本

Core2 改用已有的约 60 Hz 虚拟时钟刷新，合并短时间内的面板更新。候选与基线的 320×240 验证画面一致，点击和四方向拖动的原始与逻辑坐标逐点一致，并经 FT5x06 I²C 回读核验。结论覆盖此次虚拟设备控制固件。

- [报告](report.md)
- [机器可读记录](run.json)
- [脱敏坐标和输入摘要](evidence/stock-control.summary.json)
- [候选验证画面](evidence/probe-screen.png)
- [可重建的来宾探针](code/main.py)

本记录未执行物理设备或浏览器 WASM 验证，也未测量物理刷新率或通用性能。源码补丁保存在模拟器仓库。
