# M5Unified #446：PCF8563 `begin()` 清掉 Timer_control (0x0E) 的 TE

- 日期：`2026-11-21`
- 结果：`PASS`（`virtual-device validation`；CoreInk 实机与 CoreInk 虚拟 profile 为 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：[m5stack/M5Unified#446](https://github.com/m5stack/M5Unified/issues/446)
  「PCF8563の初期化の際にTimer_controlレジスタ(0x0Eh)のTEビットがクリアされてしまう」，
  作者 atgcgcta，日语，OPEN，0 条评论
- 源码版本：`m5stack/M5Unified @ 96576a14247ddc935149145aa6b51943464120f1`（0.3.0）；
  `m5stack/M5GFX @ 28d47949bdc84f30881623476f555398e2194313`（0.3.0）；
  `ESP-IDF v6.0.2 @ 7101770dc6db2667b3c477cc31365dd1acd6db4e`
- 环境：macOS arm64、ESP-IDF v6.0.2、`esp32s3` target、8 MB flash、无 PSRAM；
  Device Service 的 `dial`（M5Dial / QEMU / PCF8563 model）profile

## 结论

报告成立。`PCF8563_Class::begin()` 的 `writeRegister8(0x0E, 0x03)` 每次都会把
Timer_control 的 TE(bit7) 清 0，并把 TD(bits1:0) 改成 0b11（1/60 Hz）。
`M5.begin()` 先执行 `Rtc.begin()`，之后才判断 `cfg.disable_rtc_irq`，所以指定
`false` 也无法避免这次写入；默认 `true` 时后续的 `disableIRQ()` 还会写 0x0E=0x00。

在 M5Dial 虚拟设备上实测：`M5.begin(cfg)` 前的 0x82（TE=1，TD=1 Hz）在
`M5.begin(cfg)` 后变成 0x03（TE=0，TD=1/60 Hz）。按报告者的建议把
`0x0E,0x03` 替换为 `0x00,0x00` 后，`M5.begin()` 后与再次 `Rtc.begin()` 后都保持 0x82。

## 关键证据

- `evidence/serial-original.log`：未修改构建。`POST_BEGIN ... TC=0x03`、
  `AFTER_REBEGIN ... TC=0x03`、`REARM ... TC=0x82`。
- `evidence/serial-fixed.log`：提案修改构建。`POST_BEGIN ... TC=0x82`、
  `AFTER_REBEGIN ... TC=0x82`。
- `evidence/register-readback.txt`：五阶段寄存器读回与 TD 解释。
- `evidence/build-and-run.txt`：构建环境、artifact/firmware SHA256、session ID。
- `evidence/device-service-profile.txt`：无 CoreInk profile，M5Dial 的 RTC 已验证。
- `patches/0001-pcf8563-preserve-timer-control.patch`：可对 base `96576a1`
  通过 `git apply --check` 的一行 patch。
- `code/pcf8563-446/`：ESP-IDF 复现应用、构建步骤、Device Service 执行脚本。
- 已发布回复：<https://github.com/m5stack/M5Unified/issues/446#issuecomment-7053332430>（1 条，日语；issue 仍 OPEN，未 close、未 push、未改上游代码）

## 文件

- `report.md`：根因、验证方法、结果、兼容性、未覆盖项、日语回复正文
- `run.json`：结构化记录
- `evidence/`：issue 元数据、profile 摘要、构建摘要、串口日志
- `patches/`：建议的最小修改
- `code/`：可重建工程

## 未覆盖项

- CoreInk 实机复现与修复确认：`NOT RUN`（无实机）。
- CoreInk 虚拟设备验证：`NOT RUN`（Device Service 中没有该 profile）。
- INT 引脚真实波形、长期周期漂移、功耗：`NOT RUN`。
- 默认 `disable_rtc_irq=true` 路径的实测：`NOT RUN`（仅由代码确认 `disableIRQ()`
  会写 0x0E=0x00）。
- 上游 patch 提交、采纳与 release 落地：`NOT RUN`（只回复，不 push）。
