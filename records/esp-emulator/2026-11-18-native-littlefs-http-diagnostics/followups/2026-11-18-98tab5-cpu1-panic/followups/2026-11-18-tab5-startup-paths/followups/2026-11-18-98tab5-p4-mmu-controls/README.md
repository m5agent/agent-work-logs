# 98TAB5 原版冷启动故障与 P4 双核缓存对照

- 日期为 2026-11-18。原版自然启动仍是 PARTIAL。独立 SDK 对照通过。
- 原版为 98TAB5 1.3.0。通过隔离 Device Service 1.91.0 的原生 esp-emu 1.1.0 执行，属于 virtual-device validation。
- 无卡和合成 NHD 各冷启动复现 33 次软件复位，均无完整画面，串口逐字节一致。
- 两类 ESP-IDF 双核对照正常执行。CPU0 使一页 L2 缓存失效或映射后释放 Flash 物理页零，CPU1 从另一映射页的读取均正确。原版早期启动问题仍待归因。

[报告](report.md) · [执行记录](run.json) · [原版回执](evidence/98tab5-c7e-stock-natural-and-panic.summary.json) · [双核对照回执](evidence/98tab5-p4-two-hart-cache-control.summary.json)
