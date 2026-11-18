# Dial R1F30 原版旋钮复测

- 日期为 2026-11-18。验证类型为 virtual-device validation。
- 固定原版 vinylM5Dial 1.0 R1F30 合并 BIN、Device Service 1.99.0、Dial 原生运行与 PORT.B 七轨 N9301 AudioPlayer 夹具。
- 发布版 5 ms 选曲 5/6，8 ms 为 6/6，默认 35 ms 归位 11/11。发布版的一次 5 ms 正转交付全部 64 条边沿，最后停在第 6 轨且没有发新索引指令。
- 单独的只读诊断运行在一次 5 ms 错选中捕获两个完整相位未被读取。实际 GPIO 读值按固件状态表得到 +60，准确预测 UART 指令选择的第 7 轨。
- 既有 8 ms 错选没有在这两轮复现。真机旋钮、发声、浏览器和 Reviewer 路径未执行。未提交 Burner。

[执行报告](report.md) · [机器记录](run.json) · [逐动作摘要](evidence/dial-r1f30-199-pc-comparison.summary.json)
