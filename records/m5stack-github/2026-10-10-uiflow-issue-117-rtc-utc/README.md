# UIFlow MicroPython #117: RTC sync uses local time instead of UTC

- 日期：`2026-10-10`
- 结果：`PASS`（StopWatch 实机 + 固件构建；StamPLC 未单独复测）
- 工作类型：`issue` + `code_change` + `hardware_test`
- 问题来源：https://github.com/m5stack/uiflow-micropython/issues/117
- PR：https://github.com/m5stack/uiflow-micropython/pull/119
- 源码版本：`m5stack/uiflow-micropython@69846518a8b0893987ba0512558c4b01c9161454`
- 环境：macOS arm64 + Docker/ESP-IDF v5.5.4；StopWatch（RX8130）UART-REPL 实机

## 结论

`M5.begin()` 通过 `setSystemTimeFromRtc()` 把 RTC 内容按 UTC 读入系统时间，但
`rtc_sync()` 使用 `localtime_r()` 把本地时间写回 RTC。TZ 非 UTC 时，RTC 时间和
系统时间每次启动都会叠加时区偏移。

修复为 `gmtime_r()`，让 RTC 写路径与读路径一致。StopWatch 实机基线复现了 UTC+9
写入；修复后的应用在两次 `M5.begin()` 后系统时间与 RTC 寄存器保持不变。

## 关键证据

- `evidence/hardware-summary.txt`：基线 RTC 小时从 `0x11`（11 UTC）变为
  `0x20`（20 本地，UTC+9）；修复后为 `0x04` 且两次 `M5.begin()` 不变。
- `evidence/restore-summary.txt`：测试后恢复原 Wi-Fi 镜像，应用分区前缀 SHA256
  与原始 artifact 一致。
- `evidence/build-summary.txt`：StamPLC 完整固件构建 PASS；StopWatch UART-REPL
  应用构建 PASS。
- `evidence/host-repro.txt`：host 模型同时展示旧逻辑每轮 +9 小时漂移和修复后稳定。
- `patches/0001-m5unified-sync-rtc-using-utc.patch`：最小修复 patch。

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/`：host、构建、实机和恢复证据
- `patches/`：修复 patch

## 未覆盖项

- 未在 StamPLC 本体上复测，使用 StopWatch 验证同一 `M5.Rtc`/`rtc_sync()` 代码路径。
- 未做长期掉电/电池备份测试。
- 真实硬件测试使用了本地 UART-REPL 构建；测试后已恢复原 Wi-Fi 镜像。
