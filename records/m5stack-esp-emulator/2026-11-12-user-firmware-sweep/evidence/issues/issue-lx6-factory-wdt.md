## 现象

经典 ESP32（LX6）两款官方厂测固件在启动期稳定触发 task watchdog 并 abort + 重启，无限循环：

| 设备 | 固件 | firmware_id | SHA-256 | 触发时间 | 会话 |
| --- | --- | --- | --- | --- | --- |
| Atom-Lite | Atom-Lite Factory Test | 1897200000000002325 | `1c8fa292e31819c4…` | 28.6 s | `5c5bb1fe5ad14035ab6ff207f49828f8` |
| Atom-Matrix | Atom-Matrix Factory Test | 1897200000000002655 | `24892fcf5d5f8c97…` | 12.5 s | `5fc707061bfd46d5b9ba90e3643a00e3` |
| Atom-Matrix v1.1 | 同上 | 同上 | 同上 | 12.5 s | `1faac27f57974f3ca8f3d7bb816db330` |

串口摘录：

```
E (12544) task_wdt: Task watchdog got triggered. The following tasks did not reset the watchdog in time:
E (12544) task_wdt:  - IDLE (CPU 0)
E (12544) task_wdt: Tasks currently running:
E (12544) task_wdt: CPU 0: main
E (12544) task_wdt: CPU 1: ipc1
E (12544) task_wdt: Aborting.
abort() was called at PC 0x400fb4b0 on core 0
Backtrace: 0x40084151:0x3ffbed7c |<-CORRUPTED
Rebooting...
```

Atom-Lite 变体同样在 `IDLE (CPU 0)`、`CPU 0: main` 状态下超时，只是时间点更晚（28.6 s）。

## 分析

`main` 任务持续占用 CPU 而不让出，IDLE 0 得不到调度；两款固件都是官方厂测（LED 矩阵/SK6812、按键、IR 等板级自检），在真机上不会 watchdog。这类形态通常对应 guest 在**轮询某个外设状态位/等待一个不会被模拟器触发的事件**，例如 RMT 完成、IR 接收或 GPIO 中断。

`atom-lite` / `atom-matrix` 的 QEMU 串口另有 `esp32_i2c: slave mode not implemented` 与 `no address byte in TX FIFO` 告警，也在同一批经典 ESP32 板型出现，可作为排查方向之一（但尚无直接证据把 watchdog 归因到 I2C）。

## 影响

- Atom-Lite / Atom-Matrix / v1.1 的官方厂测固件不可用，无法用它们在模拟器上验收 RGB 灯、按键、IR 等板级功能。
- 失败表现为固件 abort 重启，容易被误判为固件缺陷。

## 期望 / 验收

1. 定位 `main` 的阻塞点（RMT/IR/GPIO/I2C 轮询），给出寄存器级或 trace 证据。
2. 验收：Atom-Lite 与 Atom-Matrix 厂测固件能连续运行 ≥120 s 不触发 watchdog，并完成厂测流程（至少能观察到灯阵/按键路径的行为）。
3. 回归：现有经典 ESP32 RMT/Neopixel 与 UIFlow2 用例不退化。

## 边界

- virtual-device 验证；未做真机对照，不涉及电气/光学测量。
- 未修改固件与设备 profile。
