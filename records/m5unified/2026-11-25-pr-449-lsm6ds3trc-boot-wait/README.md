# M5Unified #449: LSM6DS3TR-C 的启动等待移到上电处

- 日期：`2026-11-25`
- 结果：`PARTIAL`（virtual-device validation + code-level verification；
  CoreP4X 实机与“LSM6DS3TR-C 在位”的寄存器路径 `NOT RUN`）
- 工作类型：`pr-review`
- 条目：[m5stack/M5Unified#449](https://github.com/m5stack/M5Unified/pull/449)，
  作者 `ainyan03`，英文，OPEN；评审前 comments / reviews 均为 0
- 源码：`m5stack/M5Unified` PR head `041ed8cb320e323ec51e94ef6b4109f0d4467bc9`
  （base `b7eaa4b` = develop tip；diff 3 文件 +22/-1）
- 环境：macOS arm64；ESP-IDF v6.1（`CONFIG_FREERTOS_HZ=100`）；本机 Device Service
  36 个 profile 中的 `basic-v27`（QEMU `m5basic`，ESP32，ILI9342C）与 `nanoc6`
  （QEMU `esp32c6`，无显示）；P4 只有 `tab5`（BMI270），没有 CoreP4X profile

## 结论

未发现阻塞问题。改动把 LSM6DS3TR-C 的 15 ms 启动等待从“每次探测前”移到了两处真正上电的位置
（CoreP4X 的 M5IOE1 G12 3V3 轨、`cfg.external_imu` 的 Ex_I2C 探测前），并让驱动先读
WHO_AM_I、无应答就立即返回。因此在探测链上遇不到这颗 IMU 的板子不再为两个地址各付一次
`15 ms + 1 tick`。

虚拟设备 A/B（同一探针固件，PR head 对 develop，每版 3 次复位，结果逐次一致；两块虚拟板都
没有 LSM6DS3TR-C，正好只测“缺席”路径）：

| 虚拟板 | `M5.begin()` head / base | 单地址 `LSM6DS3TRC_Class::begin()` head / base |
| --- | --- | --- |
| basic-v27 | 599.6 / 639.6 ms | 0.25 / 19.4 ms |
| nanoc6 | 923.9 / 953.9 ms | 25.2 / 44.3 ms |

- basic-v27 上 `M5.begin()` 少 40.0 ms，与两处 19.4 ms（IDF 100 Hz tick 下
  `pdMS_TO_TICKS(15) + 1` ≈ 20 ms）之和在 tick 取整范围内吻合；作者表中的 31–32 ms 对应 Arduino 1000 Hz tick
  的 16 ms×2，机制相同。
- nanoc6 少 30.0 ms；该 QEMU C6 的 I2C 无应答本身要约 25 ms，单地址差值仍是被移除的那段
  等待（19.2 ms），但端到端差值与 tick 边界、QEMU I2C 模型有关，未按 2×19.2 解释。
- `cfg.internal_imu=false, cfg.external_imu=true` 的 basic-v27：639.6 → 619.6 ms。
  新增的 15 ms 等待确实执行（比同版仅内部 IMU 的 599.6 ms 多 20 ms），但相对 develop
  仍快 20 ms，因为省掉了两个地址的 2×20 ms。

CoreP4X 只能做代码级核对：M5GFX develop（`5873de4`）的 `corep4x_power_on` 已经把
M5IOE1 G12（pin 11，reg 0x06 bit 0x08）拉高并以 `delay_ms(150)` 结束，而 `Display.init()`
先于 `_begin()`/`Power.begin()` 执行，所以正常启动时 `rail_was_on` 为真、`Power.begin()`
不再加等待；只有 M5GFX 没上电这条轨时才会等 15 ms。P4 目标带着改动构建通过（0 警告），
esp32 / esp32c6 同样 0 警告。

**非阻塞观察（已写入评论）**：

1. 新等待生效且 LSM6DS3TR-C 确实在位时（外部 IMU，或 M5GFX 未给 G12 上电的 CoreP4X），
   驱动成功后仍会自己再等 `15 ms + 1 tick`，这条路径比改动前多约 15 ms；PR 的计时表没有
   覆盖这一组合。
2. 新增等待是精确 15 ms，而驱动用的是 `pdMS_TO_TICKS(15) + 1`。外部 IMU 路径上首次探测
   失败即返回 `imu_spec_none`、不会重试，处于 15 ms 边缘的器件可能被当成不存在。建议与
   驱动保持同样的 +1 tick 余量（或一次重试）。

## 关键证据

- `evidence/measurements.csv`：14 次会话的 `M5.begin()`、探测耗时、单地址 begin 耗时。
- `evidence/serial-basic-*.txt`、`evidence/serial-c6-*.txt`、`evidence/serial-basic-ext-*.txt`：
  代表性完整串口日志；`evidence/serial-key-lines.txt`：全部会话关键行。
- `evidence/build-summary.txt`：两个版本、六个目标构建结果、镜像 SHA256 与大小。
- `evidence/device-profiles.txt`：本机 36 个 profile，P4 只有 `tab5`（BMI270）。
- `evidence/corep4x-power-path.txt`：G12、`rail_was_on`、探测顺序、二次等待的源码行号。
- `evidence/pr449.diff`、`evidence/pr449-status.txt`：改动范围与 PR 状态。diff 为 git 原始输出，
  含 3 行 `+ `（空上下文行），`git diff --check` 只对该文件报 trailing whitespace；串口日志已
  去掉 CRLF 与行尾空白，数值未改。

## 文件

- `report.md`：完整报告（机制、验证方法、结果、边界）
- `run.json`：结构化记录
- `code/`：探针工程（`main.cpp`、`CMakeLists.txt`、`sdkconfig.defaults`）
- `evidence/`：上列原始证据与 `probe-main.cpp`

## 未覆盖项

- hardware validation：`NOT RUN`。没有 CoreP4X 实机，也没有任何 LSM6DS3TR-C 实物。
- virtual-device validation 的边界：QEMU 的 `basic-v27` / `nanoc6` 都没有 LSM6DS3TR-C 模型，
  只验证了“缺席”路径的耗时；`whoAmI`、软复位、70 ms 陀螺启动、采样丢弃这些在位路径
  完全没有执行。
- CoreP4X 的“在位”路径、G12 实际电平/锁存读回、15 ms 等待在真实电源轨上的位置：
  `NOT RUN`，只有源码核对。
- 真实硬件时序、外部 LSM6DS3TR-C、Arduino 构建：`NOT RUN`（只做了 ESP-IDF 构建）。
- 未验证 QEMU 之外 tick 频率（1000 Hz Arduino）下的绝对毫秒数，只核对了机制与量级。

## 已发布回复

- 待发布（1 条英文评论；PR 保持 OPEN，未 close、未 push、未改他人仓库）
