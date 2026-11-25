# M5Unified #452 评审：无引脚的 I2C 总线不再动作，isEnabled() 表示“有引脚”

- 日期：`2026-11-25`
- 结果：`PARTIAL`（virtual-device validation + code-level verification；
  真实硬件计时表与 PC/SDL 构建为 `NOT RUN`）
- 工作类型：`pr-review`
- 条目：[m5stack/M5Unified#452](https://github.com/m5stack/M5Unified/pull/452)，
  作者 `ainyan03`，英文，OPEN；评审前 comments / reviews 均为 0
- 源码：`m5stack/M5Unified` PR head `17fc0aecacad235037a1e68a4f5f90c5e3860dbd`
  （base `0ca3a4374766e1d09a92342e811bbffb2b991502` = develop，即已合并的 #451）；
  改动 4 文件 +24/-5
- 上游上下文：#451 评审（本仓库 `m5unified/2026-11-25-pr-451-paperdiy-no-ex-i2c/`）
  当时提出的非阻塞观察“sketch 自己调 `M5.Ex_I2C.begin()` 仍会复用残留引脚（实测 ret=1）”
  正是本 PR 要收口的部分
- 环境：macOS arm64；本机 ESP-IDF v6.1 + xtensa-esp-elf 15.2.0（本地构建，
  Docker 镜像拉取不可用，见 `evidence/build-summary.txt` 的构建差异说明）；
  本机 Device Service 36 个 profile 中的 `paperdiy`（QEMU `m5paperdiy`，board 34）、
  `cardputer`（QEMU `m5cardputer`，board 14）与 `sticks3`（QEMU `m5sticks3`，board 26 对照）

## 结论

未发现阻塞问题。PR 声称的两件事都在虚拟设备上按原方向复现，并被改动消除：

1. **板子没有外部 I2C 引脚时（PaperDIY，board 34）**：改动前 `Ex_I2C` 虽然
   `isEnabled()==false`（旧定义 `port >= 0`），但 `begin()` 没有护栏，会把 port -1 交给 M5GFX
   的软件 I2C 槽 0，复用板级探测留下的内部总线引脚（G41/G42）。同一探针固件实测：
   `Ex_I2C.begin()` 返回 **1**，随后 112 地址扫描耗时 **107 ms**，说明真的在那些引脚上跑了总线；
   改动后 `begin()` 返回 **0**、扫描 **0 ms**，而 `In_I2C` 不受影响（`begin()=1`，扫描 78/79 ms
   仍能找到 0x6E）。
2. **板子没有内部 I2C 引脚时（Cardputer，board 14）**：改动前 `In_I2C` 处于
   `port=2 / sda=-1 / scl=-1`，旧 `isEnabled()` 仍返回 **1**，于是 `M5.begin()` 在这条不存在的
   总线上找内部 RTC/IMU（`begin_ms=2165`）；改动后 `isEnabled()` 为 **0**，探测被跳过
   （`begin_ms=1875`，−290 ms）。方向与作者硬件计时表里的 −61 ms 一致，量级不同属正常
   （虚拟设备不复刻真实 I2C 超时）。

对照：`sticks3` 上两个总线都真实存在，改动后 `In_I2C(47/48)` 与 `Ex_I2C(9/10)` 都保持可用，
`Imu.isEnabled()=1`，内部/外部扫描分别命中 3/4 个地址——`isEnabled()` 语义收紧没有把“确实有总线”
的板子一起关掉。

两条**非阻塞观察**（已写入评论）：

- `isEnabled()` 现在只看引脚。`_setup_i2c()` 在内部 SCL 未定义时会写下
  `setPort(I2C_NUM_MAX, in_sda, in_scl)`；目前 55 行 pin table 里 SDA/SCL 都是成对置空的
  （`evidence/pintable-consistency.txt`：0 行半置空），所以不会误判；若将来某行只置空其一，
  `isEnabled()` 会对一个 `m5gfx::i2c::init()` 必然拒绝的端口报 true。可选加固，不是阻塞项。
- M5Unit OLED 自动探测分支仍要求 `cfg.unit_oled.i2c_port >= 0`，因此“负端口 + 有效引脚”的
  `Ex_I2C` 能通过 `isEnabled()` 却仍进不了该自动探测。这是改动前就有的限制，本 PR 没有回退它，
  只是与 PR 描述里“软件端口也算启用”一句略有落差，供作者决定是否需要跟进。

## 关键证据

同一份探针固件（`code/probe-main.cpp`）分别链接 develop（pre）与 PR head（post），
经本机 Device Service 导入合并镜像后启动，串口标记一致：

| 虚拟板 | 固件 | `In_I2C`（port/sda/scl） | `In enabled` | `Ex`（port/sda/scl） | `Ex begin()` | `Ex` 扫描 | `Bare begin()` | `M5.begin` ms | 显示 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| paperdiy | pre `0ca3a43` | 1/41/42 | 1 | -1/-1/-1 | **1** | 0 个 / **107 ms** | **1** | 530 | 0（无 PSRAM） |
| paperdiy | post `17fc0ae` | 1/41/42 | 1 | -1/-1/-1 | **0** | 0 个 / **0 ms** | **0** | 543 | 0（无 PSRAM） |
| cardputer | pre | 2/-1/-1 | **1** | 0/2/1 | 1 | 0 个 / 87 ms | 1 | **2165** | 1 |
| cardputer | post | 2/-1/-1 | **0** | 0/2/1 | 1 | 0 个 / 83 ms | **0** | **1875** | 1 |
| sticks3 | post（对照） | 1/47/48 | 1 | 0/9/10 | 1 | Ex 4 个 / 77 ms，In 3 个 / 77 ms | 0 | 1030 | 1，`Imu=1` |

- `paperdiy` 的 `Ex begin()` 1→0 与扫描 107 ms→0 ms 是第 1 点的直接证据：改动前确实在内部
  总线的引脚上执行了真实的 I2C 事务，改动后完全没有触碰。
- `cardputer` 的 `In enabled` 1→0 是第 2 点的直接证据；`M5.begin` 差值来自被跳过的 RTC/IMU 探测。
- `Bare`（默认构造的 `I2C_Class`，port -1、无引脚）在三块板上都从 `begin()=1` 变为 `0`，
  与 PR 描述“默认构造的总线什么也不做”一致。

## 文件

- `report.md`：完整报告（改动面、逐条核对、未覆盖项）
- `run.json`：结构化记录
- `evidence/serial-*.txt`：五份串口全文（含 M5GFX 板级探测与探针标记）
- `evidence/pintable-consistency.txt`：55 行 pin table 的 SDA/SCL 成对性检查
- `evidence/build-summary.txt`：构建环境、镜像 SHA256、本地构建差异
- `evidence/device-profiles.txt`：三块虚拟板的 profile 摘录
- `evidence/pr452.diff`、`evidence/pr452-status.json`：被评审的 diff 与条目状态
- `code/`：探针工程源码与配置

## 未覆盖项

- 真实硬件：没有 PaperDIY/Cardputer/Stamp 系列实机，作者的 `begin_ms` 计时表未复现，
  仅观测到同方向的虚拟设备差值。
- PC/SDL 构建：PR 说 PC 构建下 `begin()` 从 SDL stub 的 true 变为 false，本次未构建
  PlatformIO_SDL 验证（code-level：`sdl/common.hpp` 的 `init()` 直接 `return {}`）。
- 作者的计时表里 6 块无内部总线板（StampC3/C3U/S3/P4、NanoC6/H2）未逐块跑：本机 36 个
  profile 里没有这些机型可启动的 M5Unified 目标，只有 Cardputer 同类路径。
- `paperdiy` 本次镜像未开 PSRAM，M5GFX 报 `M5PaperDIY need OPI-PSRAM enabled`、面板不可用
  （`displays=0`）；被测的 I2C 逻辑与面板无关，但“画面正常”这一点本轮没有证据。
- `cardputer` 的 Cardputer/ADV 变体探测在虚拟设备上无人应答（M5GFX 日志
  `Cardputer variant unanswered; using M5Cardputer`），最终板号仍是 14，不影响本次总线结论。
