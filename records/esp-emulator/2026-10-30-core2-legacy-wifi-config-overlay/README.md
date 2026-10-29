# M5Stack ESP Emulator Core2 legacy WiFi config overlay

- 日期：`2026-10-30`
- 结果：`PARTIAL`（virtual-device validation）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03` legacy Core2 WiFi configuration path
- 源码版本：`m5stack-esp-emulator @ 6094890cc5a615fcbad1a2fd378202bcbf7b2d03`
- 交付：PR #51 已合并为 `9f200d0c288eeee6e4160fa9a521b2c9470f86e6`
- 环境：macOS arm64、Python 3.12、Device Service `/api/v1`、QEMU virtual Core2

## 结论

Core2 `runtime=qemu-wifi` 现在可以在 session-isolated Flash 副本中严格识别
classic UIFlow `deviceCfg`，写入请求选择的 WiFi 网络，并记录 hashed SSID、
base/effective Flash SHA 和 password 是否提供。非匹配分区、schema、长度或
checksum 不会被修改。

同一 effective Flash 在 WDT-disabled 诊断控制下渲染了真实
`Connecting to myssid` WiFi 页面。默认 watchdog 下仍会在 boot markers 后触发
`Cache disabled but cached memory region accessed`，因此本记录关闭的是配置
fixture 前置，不是 `RUNTIME-03`。

## 关键证据

- Original normalized firmware：
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- Service effective Flash：
  `b30f3014b75f762f50be3284010502e047b3bd0494b0f0b72a673c2756baffd7`
- Config partition：
  `6d5f7fb3eca7fb7823f32053f8efd2c7885645a524cc71d10b1b67a0c22d108d`
- Diagnostic WiFi frame：
  `320x240`、`75,373` nonblack pixels、`305` colors
- Frame SHA256：
  `df9ba1849edb7742f7b5672ff14fdfc97a2f351cd5a96b0f429ef9e22dfbf4c3`
- Legacy config tests：`7/7 PASS`
- Platform full suite：`1,596` run，`1,595 PASS + 1 skip`

## 文件

- `report.md`：实现、运行证据、边界和回滚
- `run.json`：机器可读记录
- `evidence/verification-summary.json`：脱敏检查摘要
- `evidence/frame-connecting-summary.png`：WDT-disabled 诊断 WiFi 页面
- `patches/`：不适用；改动已作为源码提交交付
- `code/`：不适用；测试位于源码仓库 `platform/tests/`

## 未覆盖项

- normal-WDT 稳定启动、setup/REPL 和完整应用帧
- DHCP、access-point association、Internet connectivity
- physical hardware、RF、物理 cache/PSRAM timing 和电气测量
