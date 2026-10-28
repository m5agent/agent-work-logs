# ESP Emulator Core2 M5UI 与 legacy SSI 报告

## 背景

用户要求使用最新模拟器在 StopWatch、StickS3、Core2 上再次验证可执行的
UIFlow2 接口，并统一处理复测发现的问题。三设备全接口复测已经确认通用
system/shared、通信、音频、ESP-NOW 和已选外设路径；剩余可操作问题中，
Core2 candidate M5UI 的全屏刷新条带可稳定复现。

同时，Core2 legacy `RUNTIME-03` 已有 `0xBB/64 -> 0x05/1` 主循环证据，
需要把 controller transaction 绑定到 guest issuer PC，判断瓶颈位于哪条
执行路径。

## 根因

### M5UI panel DMA 双写

classic ESP32 SPI panel 在 guest 写 `DMA_LINK` 时立即解析 descriptor 并
把完整像素写入 panel。随后 `SPI_CMD` 事务又执行 CPU data-register panel
路径，把 64-byte 寄存器内容和重复 tail 再写一次。

修复前 RAMWR 记录：

- `320x10` RGB565 strip expected `6400` bytes，written `12736` bytes；
- `20x60` image window expected `2400` bytes，written `4736` bytes；
- 54 个 RAMWR window 中 49 个 mismatch。

多写的尾部像素反复覆盖当前 window，形成条带。MADCTL=true、rotation=0
和 READY 后延迟重取帧都没有消除条带，因此不是旋转或 capture timing。

### Legacy SSI issuer PC

80 秒 WDT-off 控制记录 `105,161` transactions，PC 表总数同为
`105,161`，overflow 为 `0`：

- `0x05`：`49,961/49,972` 来自 `0x4006222c`；
- `0xBB/64`：`49,452/49,783` 来自 `0x40093b57`。

`0x4006222c` 位于公开发布的 IDF ESP32 ROM linker symbols
`esp_rom_spiflash_read_user_cmd=0x400621b0` 与
`esp_rom_spiflash_read_status=0x4006226c` 之间。`0x40093b57` 位于
public BIN segment 5，offset `0x167f`；没有 matching legacy ELF/MAP，
因此不声称精确函数名。

同一 frozen QEMU 的 normal-WDT 仍在 `17.253607230 s` 首 reset，TG1
reset 前 `14,998` feed、最大间隔 `3.926687 ms`、零 timeout。该结果
只把调查范围缩到上述路径，不构成产品修复。

## 改动

- `0073-esp32-ssi-command-pc.patch`：增加有界 sparse command/CPU/PC
  table 和 overflow counter，只在显式 freeze 输出。
- `0074-esp32-spi-panel-dma-dedup.patch`：记录当前 command 是否已消费
  panel DMA，跳过重复 CPU-register replay，并增加 opt-in
  `M5SW_PANEL_RAMWR_TRACE`。
- `run_wdt_liveness.py` / `run_pause_sweep.py`：允许显式
  `--service-port`，消除并发诊断中的 ephemeral-port 绑定竞态。
- 更新证据、状态页、Backlog、runtime model gap 和 patch 索引。

## 执行与结果

### Core2 M5UI

同一 candidate/base 在冻结 QEMU
`9bf74439ddbe7225a64eb437290043729fb032525756adb834565ec412f8c197`
上执行：

| 检查 | 修复前 | 修复后 |
| --- | ---: | ---: |
| state oracle | `4/4 PASS` | `4/4 PASS` |
| triangle/image frame oracle | `0/2 PASS` | `2/2 FRAME_PASS` |
| RAMWR exact windows | `5/54` | `54/54` |

修复后 pixel observations：

- triangle `(75,100)` 为 `(57,186,205)`，预期 `(56,184,200)`；
- image 四色点分别精确为红、绿、蓝、黄。

### 三设备 smoke

同一 QEMU 上并发执行：

| 设备 | system | shared corrections |
| --- | ---: | ---: |
| StopWatch | `50 PASS + 1 STATE_PASS` | `7/7 PASS` |
| StickS3 | `50 PASS + 1 STATE_PASS` | `7/7 PASS` |
| Core2 | `50 PASS + 1 STATE_PASS` | `7/7 PASS` |

所有 session 均取得 evidence ZIP，并以 `purge=0` 停止。

### 仓库与 CI

- result commit：`38760a0f968136119fe435b99d031bff611d1406`
- parent commit：`19651bf0cb521ab1e1dbb102895c3bb2578b4f5d`
- local platform suite：`1418` 项，`OK`，`1` skip
- CI run `40766337332`：`network-namespace-policy` 与
  `platform-contracts` 两个 job PASS
- project snapshot、runtime coverage、peripheral catalog、QEMU profiles：
  PASS

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | 0073/0074 QEMU rebuild；patch reverse-check；CI |
| transport | PASS | Device Service visible sessions；serial/frame/evidence ZIP |
| device_response | PASS | system/shared smoke；M5UI state 与 panel RAMWR 计数 |
| data_behavior | PASS | `written == expected` 54/54；SSI PC counts 105,161/105,161 |
| visual_or_physical | PASS（virtual visual） | triangle/image frame oracle 2/2；修复后帧 hash |
| physical hardware | NOT RUN | 无物理 Core2 同路径运行 |

## 验证边界

- Core2 legacy normal-WDT、setup/REPL、startup UI 和非空原厂应用帧仍
  `OPEN`；
- `0073` 的 ROM/IRAM 绑定不是 matching ELF symbol；
- physical DMA/SPI timing、PSRAM/cache、RF、电气和真机视觉未验证；
- stock BLE internal-controller 和外部/加密 ESP-NOW 不继承本次结果。

## 风险与回滚

改动仅影响 classic ESP32 SPI panel 的 DMA/CMD 去重和默认关闭诊断；
ESP32-S3 panel 路径未改。若需要回滚，可 revert public commit
`38760a0f`；QEMU patch 也可分别 reverse `0002`、`0001`。本次未执行
不可逆硬件操作。
