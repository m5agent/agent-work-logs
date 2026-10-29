# M5Stack ESP Emulator Core2 TIMG watchdog feed rescheduling 报告

## 背景

- 来源：`RUNTIME-03` legacy Core2 normal-WDT 启动。
- 现象：guest 周期性写 `WDTFEED`，但 TG0 stage-1 仍在固定 virtual time
  触发 system reset。
- 目标：检查 feed 是否真正替换 watchdog stage timer，而不是只验证 feed
  MMIO 被执行。

## 结论

- 状态：`PARTIAL`。
- 根因或关键判断：classic ESP32 TIMG watchdog 的 arm 路径使用
  `timer_mod_anticipate_ns()`。QEMU 该 API 会保留更早的 pending deadline；
  feed 将 current stage 重置为 0 后，旧的后续 stage deadline 不应继续有效。
- 改动范围：只将 stage timer 改为 `timer_mod_ns()`；不关闭 watchdog、
  不修改 timeout 或中断配置、不 warp 虚拟时钟。

`RUNTIME-03` 没有关闭：同固件长窗仍触发 TG0 stage-1 reset。该记录只关闭
watchdog stage timer replacement 语义。

## 证据

### 代码或配置

旧路径：

```c
timer_mod_anticipate_ns(&ws->stage_timer, ns_now + ns_to_timeout);
```

新路径：

```c
timer_mod_ns(&ws->stage_timer, ns_now + ns_to_timeout);
```

### 执行

- 环境：Device Service `/api/v1`、`runtime=qemu-wifi`、
  `profile=core2-openmac`、deterministic `-icount shift=2`。
- Patch：`patches/0001-esp32-timg-feed-reschedule.patch`。
- 固件：normalized SHA256
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`。
- 诊断 QEMU SHA256：
  `7d03bb183a34cbbf8960a75e95703f92c2fec7fe6e14dad98707e9431caf83a4`。

8 秒虚拟时点的 live frame：

```text
320x240
nonblack_pixels=3651
unique_colors=36
png_sha256=35aedd447284a3e812e6cd9bec3e3167559a50f2c121eb43482dcfc7ab108fcc
```

长窗控制：

```text
TG0 stage-1 timeout near 15.56 s
TG0WDT_SYS_RESET
factory UI / REPL / stable application frame: NOT OBSERVED
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU source rebuild; patch forward/reverse contract |
| transport | `PASS` | real `/api/v1` artifact/firmware/session path |
| device_response | `PARTIAL` | guest rendered a live frame before later reset |
| data_behavior | `PASS` | watchdog timer replacement call and regression contracts |
| visual_or_physical | `PARTIAL` | virtual nonblack frame; physical display/timing `NOT RUN` |
| review | `PASS` | platform `1583 OK + 1 skip` and documentation generators |

## 验证边界

本记录是 virtual-device validation。它不证明 physical watchdog timing、
cache/PSRAM timing、电气、RF 或 hardware behavior。短窗 live frame 不代表
legacy 应用完整启动，也不能替代 normal-WDT 稳定运行门禁。

## 风险与回滚

该补丁只改共享 TIMG watchdog timer replacement 语义。回滚为 revert
`91dca3a6`；回滚后回到可能保留旧 pending stage deadline 的模型行为。
