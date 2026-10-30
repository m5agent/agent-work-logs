# M5Stack ESP Emulator Core2 legacy WDT level delivery report

## 背景

- 来源：公开 `RUNTIME-03` Core2 legacy UIFlow 启动调查。
- 现象：同一 public firmware 在正常 WDT 下于 stage-0 timeout 后进入
  TG0 stage-1 system reset。
- 目标：让 public legacy guest 通过其正常 task-watchdog ISR 路径自行
  feed/clear，不关闭 WDT、不放宽 timeout、不使用 accelerator override。

## 结论

- 状态：normal-WDT startup `PASS`（virtual-device validation）。
- 根因：`0035` 把 WDT level 错按普通 `INT_ST = INT_RAW & INT_ENA` 门控。
  Legacy ESP-IDF 3.3.5 通过 `esp_intr_alloc` 注册 TG0 WDT interrupt，
  设置 `WDTCONFIG0.LEVEL_INT_EN`，但不写 `INT_ENA.WDT`。
- 改动：`0095` 保留普通 timer source 的 `INT_ENA` mask 与 `INT_ST`
  register 语义；仅让 WDT level output 在 `LEVEL_INT_EN=1` 时跟随
  `INT_RAW.WDT`。WDT edge 路径不变。

## 证据

### 代码或配置

```text
if (it == TIMG_WDT_INT && s->wdt.level_int_en) {
    pending = s->int_raw & (1 << it);
}
```

### 执行

- Runtime：`qemu-wifi`、`core2-openmac`、`thread=single`、
  `tb-size=128`、`icount shift=2`。
- Per-vCPU budget：默认 `10 us`。
- Watchdog：normal。
- Firmware：public Core2 UIFlow v1.15.4 image plus strict session-isolated
  `deviceCfg` overlay.
- Execution：visible Device Service API，600-second observation window。

三次独立 run 均记录：

```text
TG0 timeout ... stage=0 mode=1
TG0 wdt-int level-raised int_ena=00000002 int_raw=00000004 int_st=00000000
TG0 WDTFEED
TG0 INT_CLR old=00000004 clear=00000004
```

保留的 trace tail 分别覆盖 guest virtual `315.55-335.55 s`、
`310.55-330.55 s` 和 `320.55-340.55 s`。所有 run 均完成 boot markers、
at least one reconnect lifecycle，并保持 nonempty API Key startup UI。

额外一次 normal-WDT run 在 boot marker 后捕获真实
`Wi-Fi Connect` / `Connecting to myssid` 页面。该 run 也显示 stage-0
level delivery、feed 和 clear，无 stage-1 reset；Ctrl-C 未产生 REPL。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU rebuild；patch forward/reverse checks |
| flash | `PASS` | Device Service imported the public full image and created a session-isolated Flash copy |
| transport | `PASS` | Guest driver executed TG0 task-watchdog ISR, `WDTFEED` and `INT_CLR` |
| device_response | `PASS` | WDT level delivered with masked INT_ST zero; no stage-1 reset |
| data_behavior | `PASS` | boot markers, reconnect lifecycle and real WiFi UI path |
| visual_or_physical | `PASS`（virtual frame） | API Key startup UI and WiFi Connect frame; physical display NOT RUN |
| review | `PASS` | docs/source cross-check against ESP-IDF 3.3.5 and 5.5.4 |
| delivery | `PASS` | PR #55 merged after 4/4 CI PASS |

## 验证边界

- Any physical-hardware, RF, electrical or physical reset timing result is
  `NOT RUN`.
- Setup/REPL and a complete factory application are separate checks.
- The three run PASS is bound to the recorded firmware, QEMU and patch hashes;
  another firmware must be retested.

## 风险与回滚

Change 只影响 classic ESP32 WDT level output；non-WDT timer source 和
masked status 保持不变。回滚方式为在 ordered patch stack 中创建新的
superseding patch，恢复 `0035` 行为；不建议改写历史 patch。
