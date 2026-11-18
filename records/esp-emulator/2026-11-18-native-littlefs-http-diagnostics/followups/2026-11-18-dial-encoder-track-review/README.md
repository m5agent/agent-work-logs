# Dial 原版快转与选曲审核复核

- 日期为 2026-11-18，结果 `PARTIAL`，类型为应用复测与审核证据复核。
- Dial 原生虚拟设备使用七首索引曲目的 AudioPlayer U197 / N9301，接到 PORT.B。通过 Device Service 运行固定原版 BIN。
- R1F30 在 35 ms 下 18/18 选对，在 5 ms 下 14/18。两种间隔的测试都交付了完整边沿数。公开 R1F27 两个源码构建的对照表现相同。
- 早期 Reviewer 使用空 UART 光标，从设备的默认曲目编号开始比较。最终版本通过真实播放基线和 UART 回读，把完整边沿交付、刻意错误的期望值和原版快转漏选分开判定。

[报告](report.md) · [运行清单](run.json) · [证据索引](evidence/README.md) · [前次原版诊断](../../README.md)

- [Device Service 1.97.0 同原版 8 ms 漏选](followups/2026-11-18-dial-197-original-cadence/README.md)
- [Device Service 1.98.0 的 8 ms 复现和 5 ms 实际采样](followups/2026-11-18-dial-198-original-poll-causality/README.md)
