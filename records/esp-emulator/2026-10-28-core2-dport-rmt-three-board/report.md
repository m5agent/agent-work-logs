# Core2 DPORT/RMT 修复与三设备 UIFlow2 回归报告

## 背景

Core2 公开 legacy `UIFlow_Core2 v1.15.4` Long 启动在修复共享 I2C、timer、
WDT mask、SSI 和 pending SPI remap 后仍失败。已知 late state 与 display
completion 有关，但最新 runtime 还会在更早的 DPORT handoff 和
Neopixel/RMT 初始化处暴露两个独立模型缺口。

同时，用户要求在 StopWatch、StickS3、Core2 上再次尽可能覆盖当前 UIFlow2
接口，确认最终 QEMU 没有回归。

## 根因与修复

### DPORT high-priority interrupt ordering

经典 ESP32 DPORT flash/cache handoff 用 peer CPU 的 level-4 中断和共享 SRAM
start/end flags 协调。单线程 TCG icount 给每个 vCPU 较大指令预算，发送端
可以在接收端观察上一组 flags 前清标志并启动下一轮，形成 CPU0 等 start、
CPU1 等 end 的调度诱导死锁。

`0065` 按 CPU 跟踪 level-4/5 handler：

- handler 在 `memw` 发布 start flag 后让出；
- sender 经 `retw` 返回 end 路径时让出；
- level-5 返回 level-4 时保留 active；
- 离开 level 4、RFI/RFE 或 reset 时清除；
- 状态机仅在 TCG icount 启用时工作。

guest 指令、virtual time、中断级别和协议 flag 未修改。

### classic ESP32 RMT

旧 QEMU 对 `0x3ff56000` RMT region 返回未实现值。legacy Neopixel translator
读取 `conf0.mem_size=0`，分配零字节 buffer，串口报：

```text
E (...) rmt: RMT translator buffer create fail
OSError: Error initializing Neopixel interface
```

`0066` 模型化 8 个 channel、RMT 寄存器、2 KiB RMTMEM、`conf0.mem_size`、
memory-mode TX、threshold、`TX_END`、INTMATRIX source 47 和有界 symbol
capture。该模型不是 GPIO waveform 或电气时序模型。

## 执行

- QEMU profile：`m5core2`；
- accelerator：`tcg,thread=single,tb-size=128`；
- icount：`shift=5,align=off,sleep=off`；
- Device Service：独立 lease，`purge=0` 停止；
- final QEMU SHA256：
  `2026673273b5bced2c2696ac4850a48f5ea47d8e9c80d6ceb2cf15f68c36d29f`；
- legacy firmware normalized Flash SHA256：
  `152127c808b9212e3a5b55dd9e0a2d24e71b902e225452b67db381c76caba1cc`。

### Core2 DPORT/RMT 控制

- 五轮独立 `5 s` WDT-off 首启动 `5/5 PASS`；
- 五轮两核 PC 均已离开旧固定 deadlock 地址；
- RMT trace 观察到四次 channel 7 TX，每次 49 symbols；
- Serial 越过 Neopixel 错误并到达 `BOARD NAME`/`APIKEY`。

### Legacy late state

- normal WDT：stage-0 `7.249439902 s`、stage-1 `17.249439902 s`、
  first reset `17.249530334 s`，原因 `TG0WDT_SYS_RESET`；
- WDT-off 68 秒：CPU0 `0x40087984`、CPU1 `0x40095b31`；
- PNG：320x240、302 bytes、0 nonblack pixels，
  SHA256 `57580743a08a3f4ebdf57240cbcc997002ef63b7234531f946127f1495973f43`。

### 三设备 UIFlow2

| 设备 | System runtime | Shared corrections | Device group |
| --- | ---: | ---: | ---: |
| StopWatch | `50 PASS + 1 STATE_PASS` | `7/7` | `6/6` |
| StickS3 | `50 PASS + 1 STATE_PASS` | `7/7` | `5/5` |
| Core2 | `50 PASS + 1 STATE_PASS` | `7/7` | `6/6` |

17 个设备组 case 均为 attempt 1、`retry_used=false`。共享候选覆盖
BLE 16/32-bit UUID 和 Modbus RTU request/response/error bytes。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU 精确增量重建；`0065/0066` retained-tree reverse apply check |
| transport | `PASS` | Device Service serial/frame/evidence；三设备 group 数据面 |
| device_response | `PASS` | system runtime、shared corrections、设备组检查 |
| data_behavior | `PASS` | UIFlow2 51/7/device-group checks；RMT channel 7 symbol count |
| visual_or_physical | `PARTIAL` | 设备组帧 oracle PASS；legacy 68 秒帧明确为黑帧；物理 `NOT RUN` |

回归：

- platform `1359` tests，`OK (skipped=1)`；
- 三设备组共 17/17 PASS；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot PASS；
- `git diff --check`、Ruff `E9/F`、core2/xtensa/RMT 定向测试 PASS。
- GitHub CI run `40671894357` 的 `network-namespace-policy` 和
  `platform-contracts` 两个 job PASS。

## 验证边界

本轮是 `virtual-device validation`。不证明物理硬件、真实 LED 波形、RF、
声学、光学或电气行为。RMT 初始化成功不等于 legacy 应用完成启动。

`RUNTIME-03` 仍 `OPEN`。后续需从 `APIKEY` 后首个未完成 guest/controller
路径继续，并在 normal WDT 下获得 display completion、setup/REPL 和非空帧。

## 风险与回滚

无物理设备操作或不可逆数据变更。源码回滚为 revert commit
`805925d8336fac28652d5bddfa1df0ec4b1606b8`；单独移除 `0065/0066` 会恢复
DPORT 调度死锁和 Neopixel RMT 初始化失败，不作为建议回滚。
