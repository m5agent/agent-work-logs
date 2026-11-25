# M5Unified #451 评审报告：PaperDIY 无外部 I2C，且无端口时不启动 Ex_I2C

## 背景

PaperDIY 是 Paper 家族的 S3 机型，只有两颗 0.5 mm 12P FPC 扩展座，没有 Grove 口。
G42/G41（SYS_SCL/SYS_SDA）是内部 I2C，只到 FPC-I2S 座的 4/5 脚。旧 pin table 把 Port A 也写在
G42/G41 上，于是：

- `Ex_I2C` 与 `In_I2C` 是同一组引脚，甚至同一端口（`_setup_i2c()` 里 `in_scl==ex_scl &&
  in_sda==ex_sda` 时 `in_port = ex_port`，Arduino 下就是 `Wire`）；
- `M5.getPin(port_a_*)` 指向内部总线，`cfg.external_rtc/external_imu`、Unit OLED/LCD 自动探测
  都会来碰这条总线。

PR #451 两个 commit：

1. `b86c927` 把 PaperDIY 的 EX SCL/SDA 两列改成 `255`（无端口），In 列仍是 G42/G41。
   副作用是内部 I2C 从端口 0 移到端口 1（Arduino 下 `Wire` → `Wire1`），与 PaperS3 的做法一致，
   `Wire` 留给 sketch。
2. `bf06bc4` 在 `_begin_rtc_imu()` 里给 `Ex_I2C.begin()` 加 `Ex_I2C.isEnabled()` 前置条件。

作者同时提交 [M5GFX #447](https://github.com/m5stack/M5GFX/pull/447)，其中生成的
`extras/board_spec/generated/m5unified_pin_table/esp32s3.inl` 把该行改成
`{ board_t::board_M5PaperDIY, 42, 41, 255, 255 }`，与 M5Unified 侧逐值一致。

## 机制核对（代码级）

- `M5Unified.inl:119` 新行：In 列 `GPIO_NUM_42/41`，EX 列 `255/255`。
- `M5Unified.inl:1608` 起始的端口选择：S3 上 `in_port = I2C_NUM_1`；只有 In/EX 引脚相同时才降为
  端口 0（`:1609-1611`）。EX 为 255 后 `(uint_fast8_t)ex_scl < GPIO_NUM_MAX` 不成立，`Ex_I2C`
  保持默认 `_port_num = -1`，`setPort()` 不再被调用（`:1636`）。
- `utility/I2C_Class.hpp:132`：`isEnabled()` 就是 `_port_num >= 0`，语义正好是“有没有端口”，
  不是“有没有 begin 过”，所以护栏不会因为顺序问题误判。
- `M5Unified.hpp:256`：`getPin()` 返回 `int8_t`，表里的 `255` 读出来就是 `-1`，与 PR 描述一致。
  `M5Unified.hpp:533` 的 `ex_i2c_enabled` 本来就是
  `sda < GPIO_NUM_MAX && scl < GPIO_NUM_MAX && port >= 0`，Unit OLED/LCD 自动探测早已被它挡住。
- 第二点针对的路径：M5GFX 板级探测用 `detection_i2c_port = -1`（`M5GFX.cpp:136`），
  `probe_i2c_read()` 通过它 `i2c_open()`（`board_detect/probe_hardware.inl:158`）。
  PaperDIY 的 PM1 识别正是用 G41/G42 走这条路（`board_detect/m5/esp32s3.inl:689`）。
  `soft_i2c_setPins()` 把 `pin_sda/pin_scl` 记在 `soft_i2c_context[~(-1)]` 里，`i2c_close()`
  只释放、不清引脚号。之后 `Ex_I2C.begin()` → `init(-1)` → `soft_i2c_init(-1)`
  （`platforms/soft_i2c.inl:367`）会复用 G41/G42：`pinMode(input_pullup)` ×2，再发 9 个 STOP。
  此时内部总线已经被 M5Unified 以端口 1 打开，这套操作把同一组引脚从 I2C 外设手里拿走。
- 当 `cfg.external_rtc/external_imu` 都是默认 `false`（`M5Unified.hpp:155/158`）时，
  `_begin_rtc_imu()` 本来就不进这个分支，所以本次问题的触发条件是 sketch 显式打开外部
  RTC/IMU 探测。

## 验证方法与结果

### 构建

ESP-IDF v6.1，`components/M5Unified` 用 PR head `bf06bc4`，`components/M5GFX` 用 0.3.0 发布版
`28d4794`（该版本已含 PaperDIY 的 `internal_i2c(..., -1)` 板级描述，本次被测的 M5Unified 代码与
pin table 也都在 M5Unified 侧）。为在 IDF 6.1 下编译，本地给 M5GFX 的 `COMPONENT_REQUIRES`
补了 `esp_psram`（`esp_psram.h` 在 6.1 不再由 `hal` 传递），属构建 shim，不改行为。
四个镜像均 0 条 `warning:`。

探针 `code/main.cpp` 在 `M5.begin()` 后打印：板号、`In_I2C` 端口/引脚、`Ex_I2C` 的
enabled/port/pins、`getPin(port_a_sda/scl)`、`m5gfx::i2c::isInitialized(0/1/-1)`，随后读
PM1（0x6E，reg 0x00）两次（中间手动调一次 `M5.Ex_I2C.begin()`），最后画一屏文字。

### A/B

| 镜像 | 板 | cfg.external_* | in_port | ex_enabled | pa_sda | `isInitialized(-1)`（软件口） | PM1 读取 | 画面 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `merged_pr2.bin` | paperdiy | true | 1 | 0 | -1 | 0 | ok 0x2050 ×2 | 540×960 |
| `merged_noguard.bin` | paperdiy | true | 1 | 0 | -1 | **1** | ok 0x2050 ×2 | 540×960 |
| `merged_pr.bin` | paperdiy | false（默认） | 1 | 0 | -1 | 0 | ok | 540×960 |
| `merged_cores3c.bin` | cores3 | true | 1 | 1（port 0） | 2 | 0（`isInitialized(0)=1`） | 不适用 | 320×240 |

结论：

1. pin table 生效：PaperDIY 上 `ex_enabled=0`、`getPin(port_a_sda/scl)=-1`，内部 I2C 在端口 1
   仍能读 PM1（id 0x2050），显示正常。作者描述的“行为变化”与实测一致。
2. 护栏生效：同一 cfg 下去掉护栏，`begin()` 之后软件端口已初始化（1），说明 `Ex_I2C.begin()`
   确实在残留的 G41/G42 上开了软件 I2C；带护栏时为 0。
3. 不误伤有 Grove 的板型：cores3 上 `Ex_I2C` 仍被启动（端口 0 已初始化），`soft_enabled=0`。

### 跨仓库 pin table 一致性

`node cli/spec.js compare-pintable --m5unified <M5Unified>`：

- M5GFX #447 head `a5fdf82`：`passed: 55 board(s), 2750 value(s), 4 target(s)`（连续两次一致）。
- M5GFX develop `72001da`（未合 #447）：恰好 2 处差异，都是 PaperDIY 的
  `port_a_pin1 42 vs 255`、`port_a_pin2 41 vs 255`。

即“两个 PR 必须一起合”的说法成立；CI 不跑这项检查（M5Unified 的 workflow 里只有
`check_inl_sources.py`）。

## 影响面与兼容性

- PaperDIY 上 `Wire`（端口 0）不再被内部总线占用，这是有意的行为变化；按 G41/G42 直接用
  `Wire.begin()` 的旧 sketch 会与 `M5.In_I2C` 争同一组引脚，作者已在正文写明，建议发布说明
  里保留这一条。
- 其余无 Grove 端口的板子（`StampS3Bat`、`PaperMono`、`DualKey`、`NanoC6`、`UnitC6L`）在
  `cfg.external_rtc/imu=true` 时，不再对 port -1 调 `begin()`。原来的调用最多只是把残留的软件
  端口重开一次，不会带来可用功能（`Rtc/Imu.begin(&Ex_I2C)` 后面还有 `isEnabled()` 兜着），
  所以不算能力回退。
- 有 Grove 端口的板子路径不变：`Ex_I2C` 有端口 → 仍 `begin()`（cores3 实测）。

## 未覆盖项与风险

- 真实 PaperDIY 上“内部 I2C 引脚被改成 GPIO 开漏导致 PMIC 失联”的电气后果：QEMU 不建模引脚
  复用，PM1 在软件端口被重开之后仍可读，因此该后果 `NOT RUN`，只能算源码级推断加软件层证据。
- Arduino 工具链与 `Wire1` 实测：`NOT RUN`；`in_port=1` → `Wire1` 是 M5GFX `setPins()` 的代码事实。
- 作者报告的“PaperDIY 实机显示正常”未复现（无实机）。
- M5GFX #447 的 G45/EPD OE 与 FPC 目录改动未评审，只用其生成的 pin table 做一致性核对。
- cores3 镜像用 `CONFIG_SPIRAM=n`（该 QEMU profile 无 PSRAM），PaperDIY 镜像用 8 MB octal PSRAM，
  属环境差异，不影响 I2C/端口结论。

## 回滚

单文件 +4/-2，`git revert` 两个 commit 即回到“Port A 与内部总线同脚、同端口”的旧状态；
M5GFX 侧需同时回滚 #447 里的 pin table 行，否则 `compare-pintable` 会报两处差异。
