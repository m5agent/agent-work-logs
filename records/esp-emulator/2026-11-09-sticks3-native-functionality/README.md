# StickS3 PM1、USB、BLE HID 和 Wi-Fi 控制器验证

- 日期 `2026-11-09`
- 结果 `PARTIAL`，各功能的实测范围见下表
- 工作类型 `issue`
- 源码基线 `67a2bf6b7511e3344eae2b04cf904fd70d64a79c`
- 最终源码 `560005a20dc3e29d826561856ab58e21b10f2d79`，PR `见后续交付记录`
- 环境为 macOS arm64、原生 QEMU `m5sticks3`、独立 Device Service 和 H4 对端。各次执行分别记录运行时 SHA-256。

| 问题 | 已观测行为 | 仍待验证 |
| --- | --- | --- |
| [#201 PM1 IAP](https://github.com/m5agent/m5stack-esp-emulator/issues/201) | 原版固件触发 IAP，写入并校验 20,480 字节。坏 CRC 被拒绝。PWR 进入 ROM 下载并返回 Flash 启动。独立与集成复跑均捕获原版固件的 HWCDC 完成输出。 | 间歇启动与末尾输出稳定性、物理 PM1 烧录、掉电和时序 |
| [#202 USB OTG](https://github.com/m5agent/m5stack-esp-emulator/issues/202) | 原版 Bit Pirate 完成虚拟 USB 枚举、CDC line coding 和双向 bulk 传输，主机收到 `HIZ>`。同时读取了 HID report descriptor。 | USB HID 报告交换、Buffer DMA、MSC、host mode 和物理 USB |
| [#203 BLE HID](https://github.com/m5agent/m5stack-esp-emulator/issues/203) | StickS3 UART1 H4 夹具完成 SMP、报告订阅和两条按键报告。现有 NUS 回归通过。 | 原版 AirMouseS3 没有可用的原生 S3 控制器传输，仍为 `PARTIAL` |
| [#204 Wi-Fi monitor](https://github.com/m5agent/m5stack-esp-emulator/issues/204) | SDK 探针经 MAC/DMA/IRQ 收到限定 beacon，并发起一次无害 Probe Request。原版 M5Gotchi 的扫描对照为 `[1,1]` 与 `[0,0]`。原版 Evil 扫描在无线电关闭时返回空列表。 | 原版 Evil-StickS3 的 monitor 工作流、任意 TX 字节捕获和物理 RF |

[完整报告](report.md)记录首次 PM1 主机退出和 guest spinlock reset，后续成功运行另列。 [结构化结果](run.json) · [公开证据摘要](evidence/validation-summary.json)

源码改动由项目 PR 提供。工作记录保留源固件、规范化 Flash、运行时、帧和证据 SHA-256。证据摘要已省略本机路径、私有端点和执行标识，未附原始固件或运行日志。
