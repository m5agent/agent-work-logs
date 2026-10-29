# M5Stack ESP Emulator Core2 legacy boot-to-UI attribution

- 日期：`2026-10-30`
- 结果：`PARTIAL`
- 工作类型：`report`
- 问题来源：[`RUNTIME-03` / PR #47](https://github.com/m5agent/m5stack-esp-emulator/pull/47)
- 源码版本：`m5agent/m5stack-esp-emulator@f1cc974b`（PR #47 merged）
- 环境：macOS Apple Silicon、Python 3.12、Device Service `/api/v1`、QEMU virtual Core2

## 结论

Deterministic timing sweep 在 normal WDT 下把同一 public legacy firmware 从
“BOARD/APIKEY 前 reset”推进到执行完 matching 原厂 `/flash/boot.py`。
`shift=2` + `1 us` fairness cap 在约 `4.66 s` 输出 BOARD/APIKEY、约
`8.50 s` 完成 boot.py，但仍没有 factory UI、REPL 或非空应用帧。

WDT-off 15/20 秒结果停在双核 Waiti，Flash/cache 最后活动约 `9.36 s`；
FRC timer 仍有 callback。显式 UART 诊断捕获
`wifiWebCfg.py::_thread_task -> menu/wifi.py -> m5stack_ui.py:526`，
因此当前首阻断已定位到 boot.py 后的 WiFi 配置/UI 线程等待。`RUNTIME-03`
仍为 `OPEN`。

## 关键证据

- 运行：normal WDT、matching VFS、`runtime=qemu-wifi`、`profile=core2-openmac`
- 固件：normalized Flash SHA256 `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- QEMU：`568079f3b9e818ef1cc29b9e7cd1c5c036af19196668a12174ed79ec96c262ed`
- Frame：`57580743a08a3f4ebdf57240cbcc997002ef63b7234531f946127f1495973f43`（302-byte black PNG）
- 平台回归：`1581 OK + 1 skipped`

## 文件

- `report.md`：完整分析、命令、边界和风险
- `run.json`：机器可读摘要
- `evidence/verification.summary.json`：脱敏验证摘要

## 未覆盖项

- factory startup UI、REPL/setup、非空应用帧
- physical hardware、RF、electrical、physical cache/PSRAM timing
- 最终 WiFi/UI wait 的 root cause
