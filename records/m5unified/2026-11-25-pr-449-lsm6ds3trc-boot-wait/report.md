# M5Unified #449 评审报告：LSM6DS3TR-C 启动等待移到上电处

## 背景

M5Unified develop 的 `LSM6DS3TRC_Class::begin()` 在第一次读寄存器前统一等待
`vTaskDelay(pdMS_TO_TICKS(15) + 1)`，而 IMU 探测会依次试 `0x6A`、`0x6B` 两个地址。对于探测链
在此之前没找到 IMU 的板子（无 MPU6886 / BMI270，或老批次 SH200Q），两个地址各付一次等待，
启动变慢约 32 ms（Arduino 1000 Hz tick 下 16 ms×2）。

PR #449 的做法：

1. `LSM6DS3TRC_Class::begin()` 先读一次 WHO_AM_I；无应答立即 `imu_spec_none`，不再先等。
   有应答才保留原来的 15 ms + 1 tick 等待并再次读 WHO_AM_I 校验 ID。
2. 把等待移到真正给传感器上电的位置：
   - CoreP4X `Power_Class::begin()`：给 M5IOE1 G12（MBUS/TF/传感器 3V3 轨）上电后，若上电前
     输出锁存和引脚电平不是都为高，等 15 ms。
   - `cfg.external_imu`：`M5.begin()` 在 Ex_I2C 上做 IMU 探测前统一等 15 ms，因为
     `Power.setExtOutput()` 可能刚给 Port A 上电。
3. PR 明确声明行为变化：自己给 LSM6DS3TR-C 上电再直接调 `M5.Imu.begin()` 的代码，需要先等
   15 ms。

改动 3 文件 +22/-1：`src/M5Unified.inl`、`src/utility/Power_Class.inl`、
`src/utility/imu/LSM6DS3TRC_Class.inl`。

## 机制换算

- 被移除的成本：每个地址 `pdMS_TO_TICKS(15) + 1`。IDF 默认 `CONFIG_FREERTOS_HZ=100` 时
  `pdMS_TO_TICKS(15)=1`，加 1 等于 2 tick ≈ 20 ms（实测 19.2–19.4 ms）；Arduino 1000 Hz 时
  是 16 ms。两个地址即 ~40 ms 或 ~32 ms，和作者表里的 31–32 ms 同源。
- 驱动保留的等待仍适用于“有器件应答”的情况，因此本 PR 不改变在位器件的寄存器流程，只改变
  无器件时的代价。

## 验证方法

### 探针固件

`code/main.cpp`（同 `evidence/probe-main.cpp`）用 ESP-IDF v6.1 构建，链接 PR head 或 develop 的
M5Unified，做四件事：

1. 计时 `M5.begin()` 全程；
2. 打印 `getBoard()` / `Imu.getType()` / In_I2C、Ex_I2C 使能状态；
3. 扫 In_I2C / Ex_I2C 的 0x08–0x77，确认板上实际应答的地址；
4. 直接构造 `m5::LSM6DS3TRC_Class`，在 0x6A、0x6B 各计时 3 次 `begin()`；再调 3 次
   `M5.Imu.begin(&M5.In_I2C, board)` 计时完整探测链。

直接构造驱动只用于测“无器件时 begin() 的固定等待”，不涉及 IMU 寄存器功能。

### 虚拟设备

本机 Device Service 共 36 个 profile。使用：

- `basic-v27`：QEMU `m5basic`，ESP32-D0WDQ6-V3，ILI9342C，外设 `partial`；i2c 扫描只有
  `0x48`、`0x75`（电源相关器件），没有 0x68/0x69/0x6C/0x6A/0x6B。
- `nanoc6`：QEMU `esp32c6`，ESP32-C6FH4，无显示，外设 `simulated`；I2C 扫描无任何器件。

两块板都**没有** LSM6DS3TR-C 模型，因此虚拟验证覆盖的是 PR 要修的“探测链遇不到该 IMU”路径，
不覆盖在位路径。P4 只有 `tab5` profile，其 IMU 是 BMI270，没有 CoreP4X profile。

镜像以 `kind=merged` 导入，4 MB flash，会话 runtime `qemu`，每版跑 3 次独立复位。所有计时值
来自 QEMU，绝对值不能当作硬件启动时间，只能比较 head/base 差值。

### 结果

`evidence/measurements.csv`：

| 虚拟板 | 版本 | `M5.begin()` | 单地址 LSM begin (0x6A) | 完整 IMU 探测 |
| --- | --- | --- | --- | --- |
| basic-v27 | head | 599.606 ms | 253 µs | 300.807 ms |
| basic-v27 | base | 639.606 ms | 19.403 ms | 340.807 ms |
| nanoc6 | head | 923.950 ms | 25.170 ms | 745.081 ms |
| nanoc6 | base | 953.950 ms | 44.325 ms | 775.081 ms |

- basic-v27 的端到端差值 40.0 ms 与两个地址各 19.4 ms 的等待在 tick 取整范围内吻合。
- nanoc6 的单地址差值 19.2 ms 也吻合；端到端差 30.0 ms 比 2×19.2 略小，和 C6 虚拟 I2C
  无应答本身约 25 ms、tick 边界落在 QEMU 定时器上的量化有关，未强行归因。
- 三次会话结果逐次一致（basic-v27 与 nanoc6 各自 3 次 head、3 次 base）。

### `cfg.external_imu` 路径

basic-v27 上以 `internal_imu=false, external_imu=true` 构建同探针：

- head 619.601 ms，base 639.601 ms。
- head 比“同版仅内部 IMU”的 599.606 ms 多 20 ms，说明 `M5Unified.inl` 新增的 15 ms（2 tick）
  等待确实执行；
- 相对 base 仍快 20 ms：base 在 Ex_I2C 上要付两个地址的 2×20 ms，head 只付新增的 20 ms。

## 构建

`evidence/build-summary.txt`：

- head `041ed8c` / base `b7eaa4b`，ESP-IDF v6.1，`CONFIG_FREERTOS_HZ=100`。
- esp32c6、esp32、esp32p4 三目标各构建 head/base，均为 0 条 `warning:`。
- P4 构建使用 M5GFX develop `5873de4`（0.3.0 tag 没有 `board_M5UnitPoEP4X`）；esp32/c6 使用
  M5GFX 0.3.0。P4 构建的意义是让改动后的 CoreP4X `Power_Class` 分支真正参与编译。
- 未做 Arduino 构建，作者的 Arduino CI 结论未在本机复跑。

## CoreP4X 代码级核对

`evidence/corep4x-power-path.txt`：

- `M5Unified::begin()` 先 `Display.init()`，再 `_begin()`；`_begin()` 第一句是 `Power.begin()`。
- M5GFX develop 的 `corep4x_power_on` 在 `pmic_ops.hpp:126-136` 设置 M5IOE1（0x4F）的
  `0x06` 寄存器 bit `0x08`，即 pin 11 = `M5IOE1_Class::gpio12`，随后 `delay_ms(150)`。
- 所以正常 CoreP4X 启动到 `Power.begin()` 时该轨已上电 ≥150 ms，`rail_was_on` 为真，
  `Power.begin()` 的 15 ms 不会执行；只有 M5GFX 未上电该轨时才会补等待。
- `Power.begin()` 的读回失败只会让 `rail_was_on` 为假、多等 15 ms，不会跳过必要等待。
- IMU 探测顺序是 MPU6886 → BMI270 → LSM6DS3TR-C → SH200Q，所以有可用 MPU6886/BMI270 的板子
  根本到不了 LSM 探测；作者表中 Basic 的收益对应老批次 SH200Q（README I2C 表：BASIC
  是 MPU6886 0x68 或 SH200Q 0x6C），与 PR 正文括号中的说明一致。

## 记录说明

- `evidence/serial-*.txt` 已去掉 CRLF 与行尾空白，数值和行序未改。
- `evidence/pr449.diff` 是 git 原始 diff，含 3 行 `+ `（空上下文行），
  `git diff --check` 只对该文件报 trailing whitespace。

## 非阻塞观察

1. **在位时可能双付等待**：在新等待生效且 LSM6DS3TR-C 确实在位的组合（外部 IMU；或 M5GFX
   未给 G12 上电的 CoreP4X），驱动成功后仍执行原有的 15 ms + 1 tick，因此该路径比改动前多
   约 15–20 ms。对“启动时间”目标不是净收益，但只影响很窄的组合。
2. **余量不一致**：新增等待是精确 15 ms，驱动自身用 `pdMS_TO_TICKS(15) + 1`。外部 IMU 路径
   首次探测失败即返回、不重试，处于 15 ms 边缘的器件会被判为不存在。建议与驱动一致加 1 tick
   余量，或失败后重试一次。

两点都不影响“无器件板子不再多付 32 ms”的主结论，已在评论中作为建议提出。

## 证据边界与风险

- 虚拟验证只证明“无 LSM6DS3TR-C 时 begin() 的固定等待被移除”，不证明在位器件的
  WHO_AM_I、软复位、70 ms 陀螺启动、采样丢弃流程。
- CoreP4X 的 G12 实际电平、锁存读回、15 ms 在真实电源轨上的充分性均未实测；作者本人也写明
  没有 CoreP4X + LSM6DS3TR-C 的板子。
- QEMU 绝对值（~600/950 ms）远大于作者硬件表（265–1350 ms 量级中的对应项），不可直接比较。
- 风险集中在第三方“自己上电再调 `M5.Imu.begin()`”的写法：PR 已声明需要先等 15 ms，但没有
  同步到代码注释/文档；这是兼容性提示，不是本 PR 的运行时缺陷。
- 回滚方式： revert 这 3 个文件即可，无持久化状态或协议变化。

## 处理结果

只读评审：未 push、未 close、未改 m5stack/M5Unified。发布 1 条英文评论（与条目语言一致）：
<https://github.com/m5stack/M5Unified/pull/449#issuecomment-7157030974>。
