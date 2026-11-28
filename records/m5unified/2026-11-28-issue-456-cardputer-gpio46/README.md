# M5Unified #456 Cardputer ADV GPIO46 保持输出

- 日期：`2026-11-28`
- 结果：`PARTIAL`
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/M5Unified/issues/456
- 源码版本：`m5stack/M5Unified @ 96576a14247ddc935149145aa6b51943464120f1`（0.3.0）
- 环境：本机 Device Service（`esp32sim` 运行时）、Arduino-ESP32 3.3.13、M5GFX 0.3.0（`28d47949bdc84f30881623476f555398e2194313`）

## 结论

`M5.begin()` 的板卡探测前 GPIO46 电源保持逻辑会把 GPIO46 置为输出并驱动高；板卡识别后，
`board_M5CardputerADV`、`board_M5Cardputer` 和 `board_M5PaperMono` 都不在恢复列表中，因此
GPIO46 保持输出使能。`M5.Mic.begin()` 不会把它改回输入：ESP-IDF 的 I2S GPIO 配置只调用
`gpio_input_enable()`，不调用 `gpio_output_disable()`。这解释了作者观察到的 ES8311 ASDOUT
被 ESP32-S3 对驱的现象。

在虚拟设备上复现并验证了最小修复：把上述三块板加入 `gpio46_backup.restore()` 分支后，
`M5.begin()` 结束时 `GPIO_ENABLE1_REG` bit14 由 1 变为 0，`GPIO_OUT1_REG` bit14 也归零。

## 关键证据

- 修复前，Cardputer ADV（board 24）、Cardputer（board 14）、PaperMono（board 29）在
  `M5.begin()` 和 `M5.Mic.begin()` 之后均为 `en46=1, out46=1`。
- 修复后，同一组虚拟设备在 `M5.begin()` 之后均为 `en46=0, out46=0`。
- 证据等级：`virtual-device validation`（寄存器层）。音频对驱导致的常量样本未在模拟器复现，
  见“未覆盖项”。

## 文件

- `report.md`：完整报告与源码位置
- `run.json`：结构化记录
- `evidence/`：修复前后三块板的串口原始日志
- `patches/0001-restore-gpio46-on-cardputer-papermono.patch`：最小修复
- `code/m5u456/m5u456.ino`：寄存器与麦克风检查 sketch

## 未覆盖项

- 常量麦克风样本：模拟器 GPIO 模型明确不模拟对驱冲突，且本次未注入音频 fixture，因此
  `0xFFFF`/`0xFFF8` 现象本身未在模拟器复现；该现象仍以作者的 OpenOCD 与实机证据为准。
- `hardware validation`：`NOT RUN`。测试中心没有 Cardputer ADV 实机，现有节点不是该机型。
- 未测其他 Arduino-ESP32 / ESP-IDF 版本，未测真实 ES8311 电气波形。
