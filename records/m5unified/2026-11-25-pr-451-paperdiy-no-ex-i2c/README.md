# M5Unified #451 评审：PaperDIY 无外部 I2C，且无端口时不启动 Ex_I2C

- 日期：`2026-11-25`
- 结果：`PARTIAL`（virtual-device validation + code-level verification；
  真实 PaperDIY 硬件与“引脚复用被改写”的电气后果均为 `NOT RUN`）
- 工作类型：`pr-review`
- 条目：[m5stack/M5Unified#451](https://github.com/m5stack/M5Unified/pull/451)，
  作者 `ainyan03`，英文，OPEN；评审前 comments / reviews 均为 0
- 源码：`m5stack/M5Unified` PR head `bf06bc4ef325a2776d23348c08f3bb6976a59e5c`
  （base `b7eaa4b` = develop；diff 1 文件 +4/-2）
- 交叉条目：[m5stack/M5GFX#447](https://github.com/m5stack/M5GFX/pull/447)
  （head `a5fdf82`，base develop `72001da`），作者要求两者一起合并
- 环境：macOS arm64；ESP-IDF v6.1 + xtensa-esp-elf 15.2.0；本机 Device Service
  36 个 profile 中的 `paperdiy`（QEMU `m5paperdiy`、ET047TC1 540×960、partial）与
  `cores3`（QEMU `m5cores3`、ILI9342C 320×240、simulated）

## 结论

未发现阻塞问题。改动做两件事：把 PaperDIY 的外部 I2C 引脚置空（内部 I2C 因此留在端口 1，
与 M5GFX 板级目录一致），以及在 `_begin_rtc_imu()` 里只对“确实有端口”的 `Ex_I2C` 调
`begin()`。第二点修的是第一点带来的副作用：置空端口后 `Ex_I2C` 保持 port -1，而板级探测阶段
已经用 M5GFX 的软件端口在 G41/G42 上读过 PM1，`init(-1)` 会复用这套残留引脚重新把内部总线
的引脚改成 GPIO 开漏。

虚拟设备 A/B 把这两点都测到了（同一探针固件，只有“是否带护栏”不同）：

| 虚拟板 | 固件 | in_port | ex_enabled | `getPin(port_a_sda)` | `begin()` 后软件端口已初始化 | 内部 PM1 读取 | 画面 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| paperdiy | PR head，默认 cfg | 1 | 0 | -1 | 0 | ok，id=0x2050 | 540×960 已绘制 |
| paperdiy | PR head，`external_rtc/imu=true` | 1 | 0 | -1 | **0** | ok | 已绘制 |
| paperdiy | 去护栏变体，同上 cfg | 1 | 0 | -1 | **1** | ok | 已绘制 |
| cores3（有 Grove） | PR head，同上 cfg | 1 | 1 | 2 | 0（硬件端口 0 已初始化=1） | 不适用（0x6E 不在该板） | 320×240 已绘制 |

- 去护栏变体里 `begin()` 之后软件端口已初始化，说明 port -1 的 `Ex_I2C.begin()` 确实在
  G41/G42 上开了一个软件 I2C（`soft_i2c_init` 只在引脚已备好时返回成功）；带护栏时这一步
  不发生。这就是第二点要防的路径。
- cores3 上 `Ex_I2C` 仍需启动（`isInitialized(0)=1`），证明护栏没有把“有 Grove 端口的板子”
  一起跳过，不存在对现有板型的启动回归。
- 两块虚拟板在软件端口被初始化后仍能读 PM1，说明 QEMU 不建模引脚复用/GPIO 矩阵，**电气
  后果本身没有被复现**，只能由源码与“软件端口确实被打开”这一事实支撑。
- 跨仓库一致性：用 M5GFX #447 的板级目录跑 `compare-pintable`，结果是
  `55 board(s), 2750 value(s), 4 target(s)` 全通过；换成 M5GFX develop（未合 #447）则恰好报
  PaperDIY 的 `port_a_pin1/pin2` 两处差异（42/41 对 255/255），与作者“两个一起合”的说法一致。

**非阻塞观察（已写入评论）**：护栏只覆盖 `M5.begin()`。sketch 自己调 `M5.Ex_I2C.begin()` 时，
在无端口的板子上仍会走到同一套残留引脚（本次实测 `ret=1`，即软件端口被打开），这是改动前
就存在的行为，是否也在 `I2C_Class::begin()` 层面拒绝 port<0 值得单独决定。

## 关键证据

- `evidence/paperdiy_pr_externals_serial.txt`：PR head、`external_rtc/imu=true` 的完整串口，
  关键行 `in_port=1 … ex_enabled=0 … pa_sda=-1`、`soft_enabled=0`、两次 PM1 读取 ok。
- `evidence/paperdiy_noguard_serial.txt`：同一 cfg、去掉护栏的变体，唯一差异是
  `soft_enabled=1`。
- `evidence/paperdiy_default_cfg_serial.txt`：默认 cfg（两个 external 都是 false）的运行，
  说明默认路径本来就不进 `_begin_rtc_imu()` 的 `Ex_I2C.begin()` 分支。
- `evidence/cores3_pr_externals_serial.txt`：有 Grove 端口的板子，`i2c_init port0=1 … soft_enabled=0`。
- `evidence/paperdiy_frame.png`（SHA256 `ce54330e78bcdc0037a67455d8a0145d73657a0f675793d732955fcdf28baf46`）：
  540×960 画面，内容是本次探针输出的板号/端口。
- `evidence/compare-pintable.txt`：M5GFX #447 与 develop 两次对比的输出。
- `evidence/build-summary.txt`：工具链、四个镜像的 SHA256 与变体说明、构建告警数。
- `evidence/pr451.diff`、`evidence/pr451-status.json`：改动范围与 PR 状态。
- `evidence/device-profiles.txt`：本机相关 profile（paperdiy、cores3、papermono、papers3 等）。

## 文件

- `report.md`：完整报告（机制、验证方法、A/B、边界）
- `run.json`：结构化记录
- `code/`：探针工程（`main.cpp`、`sdkconfig.defaults`）
- `evidence/`：上列原始证据

## 未覆盖项

- hardware validation：`NOT RUN`。没有 PaperDIY 实物；作者报告“`M5.begin()` 能识别板子、
  显示正常”，本次无法复现。
- virtual-device validation 的边界：QEMU 不建模引脚复用/GPIO 矩阵，因此“内部 I2C 引脚被改成
  GPIO 开漏、总线被破坏”的电气后果没有被观测到；只有“软件端口是否被打开”这一软件层事实。
- Arduino 构建与 `Wire`/`Wire1` 实测：`NOT RUN`。只做了 ESP-IDF 构建；端口 1 = `Wire1` 是
  M5GFX `setPins` 的代码事实。
- M5GFX #447 本身（G45/EPD OE、FPC 目录）没有评审，只用了它生成的 pin table 做一致性核对。
- cores3 的 `CONFIG_SPIRAM=n` 是因为该 QEMU profile 不提供 PSRAM（首次带 PSRAM 的镜像在
  `octal_psram` 初始化处 abort），不影响本次结论，但属于环境差异。
