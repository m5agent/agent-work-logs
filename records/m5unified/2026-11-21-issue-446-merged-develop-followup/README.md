# M5Unified #446 后续：合并后 develop 的 PCF8563 定时器保留行为

- 日期：`2026-11-21`
- 结果：`PARTIAL`
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/M5Unified/issues/446
- 源码版本：`m5stack/M5Unified @ dae3b5d04e6ad5f91ac72a89da09d427a0e20543`（#447 合并后的 develop）
- 环境：macOS arm64；ESP-IDF v6.0.2；M5GFX 0.3.0；本机 Device Service 的 `dial` 虚拟设备（M5Dial / QEMU / PCF8563 寄存器模型）

## 结论

作者 ainyan03 在 #446 报告 #447 已合并进 develop，并请求在可用装置上确认 develop 版行为。
本记录在合并后的 develop（`dae3b5d`，与已评审的 PR head `4a0ebfd` 同一棵树）上，用同一份
最小 sketch 在虚拟 M5Dial 上复测了新增说明的四个行为点：

- `cfg.disable_rtc_irq = false` 时，`M5.begin()` 后 `Timer_control (0x0E)` 仍为 `0x82`
  （TE=1、TD=1 Hz），`clearIRQ()` 后也不变，TIE 保持；
- `clearIRQ()` 只清 `Control_status_2 (0x01)` 的 TF/AF，不停止定时器；
- `setTimerIRQ(0)` 与 `disableIRQ()` 均把 `0x0E` 置为 `0x03`（TE=0、TD=1/60 Hz）；
- 默认 `disable_rtc_irq = true`（`begin()` → `disableIRQ()`）仍以 `0x03` 停止定时器。

证据等级为 **virtual-device validation**。QEMU 的 PCF8563 模型只实现时间寄存器，没有倒计时 /
TF / INT 逻辑，因此“定时器实际持续触发”和“电源断→RTC 起床”的重复周期仍为 **NOT RUN**；
本机也没有 CoreInk 实机或 CoreInk 虚拟 profile。hardware validation: **NOT RUN**。

## 关键证据

- 合并 commit 与 PR head 同树：`git diff --stat 4a0ebfd dae3b5d` 无输出；API compare
  `files: []`。见 `evidence/merged-commit.txt`。
- 构建：M5Unified `dae3b5d` + M5GFX `28d4794` + ESP-IDF v6.0.2，merged BIN 503424 bytes，
  SHA256 `b57aa03c...`。见 `evidence/build-and-run.txt`。
- 运行：`dial` / QEMU / PCF8563 寄存器模型，session `29343da6...`，串口标记
  `PCF8563_446_FOLLOW_DONE`。
- 寄存器读回（`0x0E` / `0x01` / `0x0F`）：`disable_rtc_irq=false` 时 `0x82` 跨 `begin()` 与
  `clearIRQ()` 保持；停止路径均落到 `0x03`。见 `evidence/register-readback.txt` 与
  `evidence/serial-develop.log`。

## 文件

- `report.md`：完整报告（代码路径、构建、阶段、边界、复现命令）
- `run.json`：结构化记录
- `evidence/`：合并 commit 核对、构建运行摘要、设备 profile、寄存器表、串口日志
- `code/pcf8563-446-follow/`：可重建的最小 ESP-IDF 工程与 Device Service 运行脚本

## 未覆盖项

- CoreInk 或其他 PCF8563 实机：**NOT RUN**（本机与 Device Service 均无该型号/profile）。
- 定时器继续计数、TF 置位、INT 引脚触发：**NOT RUN**（QEMU 模型无倒计时逻辑）。
- 实际电源断→RTC 起床的重复周期，含 `M5.Power.timerSleep(seconds)`：**NOT RUN**。
- 其他 PCF8563 板卡的初始化差异：**NOT RUN**；本次只覆盖同一 `PCF8563_Class` 驱动路径。
