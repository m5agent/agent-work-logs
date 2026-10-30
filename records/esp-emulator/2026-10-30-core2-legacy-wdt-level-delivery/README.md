# M5Stack ESP Emulator Core2 legacy WDT level delivery

- 日期：`2026-10-30`
- 结果：`PASS`（virtual-device validation；normal-WDT startup scope）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03` Core2 legacy normal-WDT reset
- 源码版本：`m5stack-esp-emulator @ f15fcd7fd3f644c618a79446d115e0f4690ce97c`
- 交付：PR #55 已合并为 `14f21d309b6b53015e5188c9a4beb0f88a1e7324`
- 状态关闭：PR #56 已合并为 `1d16d7c1d06a107e46f000644c9df84517ee534f`
- 环境：macOS arm64、Python 3.12、Device Service `/api/v1`、QEMU virtual Core2

## 结论

`0095-esp32-legacy-wdt-level-delivery.patch` 修正了 `0035` 对 classic
ESP32 TIMG WDT level 的错误门控。Legacy ESP-IDF 3.3.5 的 task watchdog
只配置 `WDTCONFIG0.LEVEL_INT_EN`，不写 `INT_ENA.WDT`；修复后 three
independent normal-WDT Device Service runs 均越过原 stage-1 reset，
执行 WDTFEED/INT_CLR，并稳定运行到 guest virtual 300 秒以上。

同一路径保持原厂 API Key startup UI；附加运行进入真实
`Wi-Fi Connect` / `Connecting to myssid` 页面。Ctrl-C 未得到 REPL prompt，
因此 setup/REPL 和完整 factory application 是独立未覆盖项。

## 关键证据

- Original public firmware：
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- Effective Flash：
  `b30f3014b75f762f50be3284010502e047b3bd0494b0f0b72a673c2756baffd7`
- QEMU binary：
  `001a938503e7b1d813f388022d849c24bab4f5298602211f70042a5184fcb62d`
- Patch SHA256：
  `df008a1f34324c1b4b0d7bc4640f03bb5f9b42b109cfedadfee0b31631411894`
- normal-WDT attempts：`3/3 PASS`
- Trace：`int_ena=2`、`int_raw=4`、`int_st=0`，随后 level raise、
  `WDTFEED`、`INT_CLR=4`；无 TG0 stage-1 reset
- Core2 UIFlow2 设备组：`6/6 PASS`，无 retry
- Platform suite：`1,614` tests，`1,613 PASS + 1 skip`
- PR CI：四项全部 PASS

## 文件

- `report.md`：根因、改动、运行证据、边界和回滚
- `run.json`：机器可读记录
- `evidence/verification-summary.json`：脱敏运行摘要
- `followups/2026-10-30-runtime03-closure/`：RUNTIME-03 stock startup scope 关闭记录
- `patches/`：不适用；patch 与源码 evidence 已在主仓库交付
- `code/`：不适用；contract test 位于主仓库

## 未覆盖项

- setup/REPL 独立交互与完整 factory application
- physical WDT/reset timing、电气、RF 和 physical hardware validation
- 任意 legacy 固件或任意应用从本固件路径继承 PASS
