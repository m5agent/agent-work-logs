# M5Stack ESP Emulator Core2 legacy WiFi config overlay 报告

## 背景

- 来源：`RUNTIME-03` legacy Core2 normal-WDT 启动。
- 现象：原厂 UIFlow 镜像停在 WiFi 配置生命周期，没有进入完整启动 UI。
- 目标：确定配置实际位于哪个 Flash 分区，在不绕过 guest WiFi 代码的前提下
  提供可复现的配置 fixture，并验证默认启动问题是否随之消失。

## 结论

- 状态：`PARTIAL`。
- 根因或关键判断：该固件的 `config` partition 包含带两字节长度和
  one-byte checksum 的 `deviceCfg` JSON；单独的 `wifi` partition 为
  erased。之前的 fixture 路径没有覆盖真正承载配置的 partition。
- 改动范围：仅 Core2 `runtime=qemu-wifi`，仅 session Flash 副本，
  仅完整匹配的 legacy schema。

实现记录 `legacy_wifi_config_applied`、partition offset/size、hashed SSID、
base/effective Flash SHA 和 password 是否提供；不导出 raw SSID/password。
其他设备、runtime 和不匹配的 firmware 保持 byte-for-byte 不变。

## 证据

### 代码或配置

```text
platform/tools/legacy_device_config.py
platform/tools/device_service.py
platform/tests/test_legacy_device_config.py
```

严格条件：

- `config` partition type/subtype/label 匹配；
- JSON 包含 legacy `deviceCfg` 四键；
- 两字节 big-endian length 与 one-byte checksum 有效；
- 写入后 archive 大小不超出 partition。

### 执行

Service overlay lane：

- QEMU：`54e7a7f7cd0ff6f5a1d6343c06563388f49c2b0abbca4cafb850876e57ed1254`
- Original firmware：`4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- Effective Flash：`b30f3014b75f762f50be3284010502e047b3bd0494b0f0b72a673c2756baffd7`
- Password provided：`false`
- API event：`legacy_wifi_config_applied`

标准 runtime 的 43 秒 service lane 证明 Flash overlay 与事件边界；它仍是
blank frame，不用于宣称 guest startup PASS。

Diagnostic default-WDT lane：

```text
BOARD NAME: M5STACK-CORE2
APIKEY marker reached
CORE2_LEGACY_ORIGINAL_BOOT_START
CORE2_LEGACY_ORIGINAL_BOOT_DONE
Cache disabled but cached memory region accessed
```

该 lane 证明配置本身不再阻止 boot markers，但后续 cache/interrupt 路径仍失败。

Diagnostic WDT-disabled lane：

```text
320x240
nonblack_pixels=75373
unique_colors=305
png_sha256=df9ba1849edb7742f7b5672ff14fdfc97a2f351cd5a96b0f429ef9e22dfbf4c3
```

画面显示 `Wi-Fi Connect`、`Connecting to myssid` 和 Core2 `v1.15.4`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall；无 QEMU source 改动 |
| transport | `PASS` | `/api/v1` artifact/firmware/session、session-isolated Flash 与 event |
| device_response | `PARTIAL` | 真实 legacy WiFi 页面可达；没有完成 association/DHCP |
| data_behavior | `PASS` | schema/checksum、幂等、scope、base/effective SHA 与红线测试 |
| visual_or_physical | `PARTIAL` | WDT-disabled virtual frame；physical display `NOT RUN` |
| review | `PASS` | platform `1,596`、docs `50/50`、generators、Ruff 和 scope PASS |

## 验证边界

本记录是 virtual-device validation。默认 WDT 仍触发 cache-disabled panic，
所以 normal-WDT stable startup、setup/REPL、完成应用帧和
`RUNTIME-03` closure 均未达成。没有执行物理硬件、RF、电气、物理
cache/PSRAM timing、DHCP 或 Internet 连接测试。

## 风险与回滚

overlay 只写 session copy；source artifact 不改写。config credential 按
hashed SSID 与 boolean password presence 记录。回滚为 revert source commit
`6094890c`，回滚后 legacy Core2 仍保留未配置 WiFi fixture 的前置缺口。
