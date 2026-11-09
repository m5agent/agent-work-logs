# Cardputer ADV MP3 Player v1.0.0 启动复核

- 日期：2026-11-09
- 总体结果为 `PARTIAL`。
- 工作类型：固件运行报告
- 问题来源：公开发布的合并镜像在 Cardputer ADV 虚拟设备上未显示应用画面。[v1.0.0 发布页](https://github.com/TurbulentGoat/cardputer-adv-mp3-player/releases/tag/v1.0.0)
- 源码版本：MP3 Player `fa967592011e9e8495ef3f540422eac4d6169adc`，ESP Emulator `dd2eb35d2e6a909992268089ddc37e27970d4a92`。
- 环境：Device Service 原生 QEMU，ESP32-S3，Cardputer ADV profile。

## 结论

默认 QEMU 板级接线触发了固件所用 Arduino I2C HAL 的自锁。相同固件、ROM 和 SD 镜像只改动仿真板的四处外接模块挂载后，5 秒采样时已显示应用的无卡提示。这个诊断版本挂载 SD 仍失败，MP3 播放和真机行为未验证。

## 关键证据

- 上游发布镜像为 885,600 字节，SHA-256 为 `c5918ff914a51b0dc4398f331c8306c25e26a4b157592d3e7d9c0dff2d0c5e45`。
- 基线串口停在 ROM 向二级 bootloader 跳转的 `entry 0x403c8898`。240×135 的帧有 0 个非黑像素。
- 独立诊断会话采样到两个 CPU 的 PC 均在 app0 的 IRAM 段内。另外三个会话的栈与内存证明，`loopTask` 持有 I2C1 mutex 时又无限等待同一把锁。[执行摘要](evidence/execution-summary.redacted.json)

## 文件

- [完整报告](report.md)
- [结构化结果](run.json)
- [脱敏执行证据](evidence/execution-summary.redacted.json)

## 未覆盖项

Cardputer ADV 真机及其物理 SD、声音与电气行为为 `NOT RUN`。现有测试中心没有匹配的真机夹具。

## 后续修复

[裸板接线与 SPI SD 修复复验](followups/2026-11-09-cardputer-adv-model-fidelity/) 使用同一原版固件独立验证，保留上面的原始黑屏结果。

[主线交付与常驻审核 dry-run](followups/2026-11-09-cardputer-adv-main-and-dry-run/) 记录同哈希快照复审、按键后读卡和虚拟播放。
