# StopWatch / StickS3 / Core2 UIFlow2 音频与 Core2 输入收尾

- 日期：`2026-10-28`
- 结果：`PASS`（限定 virtual-device validation；完整接口面仍为 `PARTIAL`）
- 工作类型：`code_change` + `virtual_device_validation`
- 问题来源：用户要求继续复测三台 UIFlow2 接口、集中修复并关闭已解决问题
- 源码版本：[`m5agent/m5stack-esp-emulator@0d4f53a3`](https://github.com/m5agent/m5stack-esp-emulator/commit/0d4f53a32e67c830c4c01e756f9f034f596eb345)
- 环境：macOS arm64；UIFlow2 v2.5.3；visible Device Service；QEMU `03d74d53…`

## 结论

三台 Mic `record`/`recordWavFile`、Speaker raw 和连续
`playWav → playWavFile` 在最终 runtime 上通过。Core2 A/B/C/PWR 四条原生输入
路径的 `setCallback.WAS_HOLD` 与 `removeCallback` 也通过。

修复两个运行时问题：

- `0062` 将 ESP32-S3 I2S DMA completion 与 PCM evidence capture 窗口分开；
- `0063` 将 Core2 A/B/C 接到 FT5x06 下方触控条，同时保留 `key:p` 到
  AXP2101 PWR 事件路径。

同时修正 Core2 裁剪 PDM 音频的测试 oracle：无窗矩形 DFT 会把同一信号误报为
395/425 Hz，归一化自相关稳定给出约 443.8 Hz。

## 关键证据

- 三台 Mic `record` 与 WAV 主频均在 5% fixture 门限内；
- 三台 Speaker WAV/file 与 raw 主频为 659–662 Hz；
- Core2 A/B/C 坐标分别为 `(53,260)`、`(160,260)`、`(266,260)`；
- A/B/C/PWR 回调均收到状态 `[2]`，remove 后无新事件；
- 平台回归 `1351` 项 `OK`，`1` 项既有 skip；
- 四个生成器检查与 `git diff --check` PASS；
- 当前 GitHub open issue 为 `0`，没有关闭任何 issue。

## 文件

- `report.md`：根因、修改、证据和边界
- `run.json`：机器可读记录
- `evidence/results.json`：最终 runtime、音频和输入结果
- `evidence/regression-summary.txt`：验证命令与清理状态
- `patches/`：`0062` 与 `0063` 最小运行时修复

## 未覆盖项

- 物理麦克风、扬声器、触控压力、PMIC 电气和真机为 `NOT RUN`。
- ESP-NOW peer TX/RX/IRQ 仍受 OpenMAC 模型缺口限制。
- Core2 全部 28 类 M5UI 文档方法矩阵仍为 `REVIEW`。
- 最终 runtime 的六音频会话并发中 StopWatch Mic 在 guest READY 前超时，
  单独重跑通过；该基础设施超时不作为固件 PASS 或失败。
