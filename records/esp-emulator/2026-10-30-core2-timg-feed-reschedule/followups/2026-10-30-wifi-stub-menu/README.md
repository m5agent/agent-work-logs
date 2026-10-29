# Core2 legacy WiFi stub menu follow-up

- 日期：`2026-10-30`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03`
- 源码版本：`m5agent/m5stack-esp-emulator@1b2a376e`
- 环境：macOS Apple Silicon、Python 3.12、Device Service `/api/v1`、QEMU virtual Core2

## 结论

在包含 classic-panel DMA 修复的 diagnostic QEMU 上，只把
`wifiWebCfg.config_by_web` stub 为返回 true，legacy firmware 就能渲染完整
`320x240` App/Flow/Setup 菜单：

- nonblack pixels：`76,760 / 76,800`
- colors：`417`
- frame SHA256：
  `a4f683468cfb9edc70468efaabd23c226abbed7a3cdeaf6a397cab09c52a6078`

原厂镜像的专用 `wifi` 分区为空。因此 display/LVGL/menu 路径已有诊断
PASS，剩余原厂 blocker 是真实 WiFi 配置和 normal-WDT 生命周期。
`RUNTIME-03` 仍为 `OPEN`。

## 关键证据

- 原厂 normalized firmware SHA256：
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- WiFi stub normalized firmware SHA256：
  `f4966a4a2a3983cc15f5752a28e9a04ef990f63ef868c3ce7ce8de3349871c1b`
- Diagnostic QEMU SHA256：
  `7d03bb183a34cbbf8960a75e95703f92c2fec7fe6e14dad98707e9431caf83a4`
- Serial markers：BOARD/APIKEY、boot.py、WiFi stub installed/configured
- Frame：完整 UIFlow Core2 主菜单

## 文件

- `report.md`：执行、根因边界和验证层级
- `run.json`：机器可读摘要
- `evidence/verification.summary.json`：脱敏证据

## 未覆盖项

- 原厂 `wifiWebCfg` 与专用 WiFi 分区
- normal-WDT 稳定启动、REPL/setup 和用户应用
- physical hardware、RF、电气与物理 cache/PSRAM timing
