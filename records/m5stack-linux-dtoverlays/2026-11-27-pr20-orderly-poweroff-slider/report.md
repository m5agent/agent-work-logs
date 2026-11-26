# powerfail_suo: orderly poweroff from the power slider — 只读评审

## 1. 背景与目标

CardputerZero 的电源拨杆本身不切电：M5IOE1（PY32，I2C `0x4f`）在拨杆断开后仍把 PWR_EN
拉高 `OFF_TIME`（`0xB2/0xB3`，u16 LE 毫秒，上电默认 2000），然后才掉电。旧驱动只在这个
约 2 s 窗口里做 SysRq U + 拉低 LCD reset，用户态从不收敛，未保存的数据丢失。

PR #20 的做法：

1. probe 时把 `OFF_TIME` 设为 `power-hold-ms`（默认 20000），拨杆断开时再设一次；
2. `0xB6` 电源状态确认是拨杆真的断开后跑 `orderly_poweroff(true)`；
3. `power-hold-ms - 4 s` 时挂一个 backstop，跑 SysRq S + U 兜底；
4. `.shutdown` 里只在 `SYSTEM_POWER_OFF` 时把 `OFF_TIME` 降到 200 ms，让 Linux 关完就切电。

评审目标：确认这套状态机在代码层面自洽、失败路径不劣化，并给出可执行证据。

## 2. 评审对象

- PR：<https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20>，作者 shrimpapplepro，英文，OPEN，评审前 0 评论 0 review
- head `5623292f043f5b4617f5d035130f464281f13dd1`（单 commit），base `main` `a3fd3e83c0247e16e194e7e40f7fc1f5be933dd4`
- 变更：`modules/CardputerZero/powerfail_suo.c`（+297/-52 量级）、`modules/CardputerZero/cardputerzero-v5-overlay.dts`（+3），共 +248/-52
- 相关既有实现：`modules/m5ioe1-1.0/m5ioe1.c`（同为 `0xB2` 的 8 位 regmap 访问，probe 里有 `m5ioe1_reset()`）

## 3. 方法

### 3.1 overlay 编译复核

本机 `dtc 1.8.1` + `clang -E`，对 PR head 的 `cardputerzero-v5-overlay.dts` 执行仓库
`Makefile` 里的同一条链路（`cpp -nostdinc -undef -x assembler-with-cpp` → `dtc -@`）：

- 无诊断、无 warning，产物 sha256 `af5eeadd…0423`；
- dtbo 里 `powerfail` 节点带 `m5stack,power-controller = <&m5ioe1>` 与
  `power-hold-ms = <0x4e20>`（20000）；
- `__local_fixups__` 中 `m5stack,power-controller` 与 `disabled-gpios` 并列，
  说明新 phandle 与既有属性走同一条 overlay 应用期修补路径，作者“在编译出的 dtbo 里核对过”
  的说法可以复现。

### 3.2 内核 API 核对

对 `kernel/reboot.c`（v6.12 与 master）、`drivers/base/core.c`、`drivers/i2c/i2c-core-smbus.c`、
`drivers/i2c/i2c-core-of.c`（rpi-6.12.y）逐条核对，见 `evidence/kernel-api-checks.txt`：

- `kernel_shutdown_prepare()` 先 `system_state = state` 再 `device_shutdown()`，
  所以 `.shutdown` 里 `system_state != SYSTEM_POWER_OFF` 的门控在 poweroff 时成立、
  reboot 时跳过，写法正确；
- `i2c_smbus_write_i2c_block_data()` 的 `I2C_SMBUS_I2C_BLOCK_DATA` 写路径是
  `[command][data…]`、不带 SMBus 长度字节，即线上就是 `0xB2, LSB, MSB`，
  与 `0xB2/0xB3` 这对寄存器一致；`i2c_smbus_read_word_data()` 按 LE 组装，回读比较成立；
- `device_shutdown()` 逆序遍历。块设备/mmc 是运行期注册的，排在启动期 platform 设备之后，
  因此 SD 卡先于本驱动 shutdown，`.shutdown` 里写 200 ms 不会抢在 SD flush 之前。
  （这条一度是疑点，核对后排除。）

### 3.3 主机级状态机 harness

`code/` 下用 stub 内核头文件直接编译驱动真实源码（`harness.c` include `powerfail_suo.c`），
配一个模拟 M5IOE1 寄存器文件、可编程 `0xB6` 读数序列、模拟 jiffies（`msleep` 只推进时间）、
记录 `schedule_delayed_work` 延迟与 `orderly_poweroff`/`handle_sysrq` 调用。
15 个场景（probe 默认/legacy/defer、拨杆断开、DEBOUNCE 重读、丢弃分支、误触发、写 `OFF_TIME` 失败、
`.shutdown` poweroff/reboot/menu、`remove` 还原、`power-hold-ms=8000`/4000、backstop 正文），
基线版与建议修复版各跑一遍，全部断言通过：

- `evidence/host-harness-pr-head.txt`
- `evidence/host-harness-proposed-fix.txt`

## 4. 结论

设计方向正确：以“能不能真正编程 M5IOE1”为开关，不能就退回旧的 SysRq U 行为；
`.shutdown` 门控、I2C 帧格式、i2c client 引用释放、`remove` 还原 `2000` 都经得起核对。
没有发现阻塞性问题，但有一个**逻辑问题**和两个小项。

### 4.1 `M5IOE1_POWER_DEBOUNCE(2)` 被当成“拨杆还开着”而丢弃事件

`powerfail_confirmed()`（`powerfail_suo.c:129-140`）在读到 2 时只 `msleep(150)` 重读一次，
若仍是 2 就返回 false；`powerfail_suo_work()`（`:179-186`）随即走“switch is still on”
分支：不打 `orderly_poweroff`、不挂 backstop、`triggered` 清零、`enable_irq()`。

但按驱动自己的寄存器注释（`:45`），状态 2 正是“slider off, 100 ms debounce”——芯片已经
看到拨杆断开，只是还在消抖。把 2 判成“还开着”与注释矛盾；一旦 150 ms 后仍读到 2
（触点抖动、拨杆停在中间位置、实际消抖窗口比 150 ms 长），事件就被丢掉，而：

- `OFF_TIME` 停留在 probe 写入的 20000；
- 边沿触发的中断在 `irq-gpios` 仍为低的线路上重新使能，线路不回高就不会有新的下降沿；
- 结果：板子带可写文件系统再跑最多 20 s，然后硬切电——比现在 2 s 内 SysRq U 的旧行为更差。

harness 场景 S5/S5b 在基线版上复现了“事件被丢弃 + `OFF_TIME` 仍 20000 + backstop 未挂 +
线仍为低时重新使能中断”；把 2 也算作已确认、并在丢弃分支把 `OFF_TIME` 还原成 2000 后
（`patches/0002`），S5 变成正常 `orderly_poweroff`，S5b/S6 的丢弃路径回落 2000，其余场景
逐条不变。

建议：最终判定只把 `M5IOE1_POWER_ON(1)` 视为“没断开”，其余（含 2）都算确认；
或对 2 做有上限的重试循环。丢弃分支应把 `OFF_TIME` 还原为 `M5IOE1_OFF_TIME_STOCK`，
让“漏掉一次事件”的最坏情况退回旧行为，而不是长保持。

### 4.2 backstop 偏移固定 4 s，与允许的最小保持时间不匹配

`POWERFAIL_BACKSTOP_MS` 固定 4000，`POWERFAIL_HOLD_MIN_MS` 是 8000
（`powerfail_suo.c:52-55`）。用户按允许的最小值 `power-hold-ms = <8000>` 配置时，
backstop 在拨杆断开后 4.0 s 触发（harness S12：500 ms 时挂，delay = 3500 ms），
而作者自己的日志里一次健康关机用了约 4.9 s（`00:27:31.394` → `00:27:36.252`），
SysRq U 会插进正常关机流程中间。建议把最小值抬到 12000，或让偏移随保持时间缩放
（例如保持时间的 1/4～1/3）。默认 20000 不受影响，非阻塞。

### 4.3 两个小项

- `power-hold-ms` 没有厂商前缀，而同批新增的 `m5stack,power-controller` 有；DT 里
  非标准属性一般要求 `<vendor>,` 前缀，建议改成 `m5stack,power-hold-ms`。
- `m5stack,power-controller` 缺省时回退到 `disabled-gpios` 的控制器，而该属性在本板
  语义上是 LCD reset（`IO12`）。这对已部署的旧 overlay 是必要的兼容手段，但也意味着
  将来任何把 `disabled-gpios` 指向 M5IOE1 的 overlay 会静默进入 orderly-poweroff 路径
  并拿到 20 s 保持。可考虑只在显式出现新属性时才启用新路径。

### 4.4 已核对无问题

- `.shutdown` 的 `system_state` 门控（poweroff 进、reboot 出），harness S8/S9/S10；
- `.shutdown` 在 menu 关机（拨杆仍开）时不动 `disabled-gpios`，S10；
- `OFF_TIME` 写失败 → `powerfail_legacy()` 完整保留（SysRq U + backlight 0 + LCD reset），S7；
- probe 时 i2c client 不在 → `-EPROBE_DEFER`，S3；
- `remove` 在非 slider-off 时还原 `2000`，S11；
- `of_find_i2c_device_by_node()` 的引用由 devm action `put_device()` 释放，无泄漏；
- probe 期写入的 `OFF_TIME` 可能被 `m5ioe1_probe()` 的 `m5ioe1_reset()` 覆盖（两者 probe
  顺序不保证），但拨杆事件路径会重写，属于作者已声明的设计，可接受。

## 5. 未覆盖项

- **hardware validation: NOT RUN**。本机无 Cardputer Zero；作者自述在 6.18.39+rpt-rpi-v8
  实机测过 2 s/10 s 掉电时间、5 s 关机、15.7 s 兜底与下次启动 fsck 干净，均未独立复跑。
- **virtual-device validation: NOT RUN**。本机 Device Service 的 `cardputer-zero` profile
  `supported=false creatable=false backend_ready=false`，缺 `__missing_qemu__` / `__missing_rom__`，
  后端是 Linux ARM64，不是 ESP32 固件目标。
- **内核模块构建（W=1）: NOT RUN**。本机无 Linux 内核头文件/交叉工具链；docker 守护进程
  存在但其 containerd 状态目录只读，无法起临时容器重建。作者报告的 W=1 干净未独立复核。
- **计时真实性**: harness 的 `msleep` 只推进 jiffies，不模拟真实定时器抖动、I2C 传输耗时、
  工作队列并发与 `cancel_delayed_work_sync` 的竞争；S4 的 16.0 s 挂点只证明算术正确。
- **`0xB6`/`0xB2` 语义**: 状态值与“countdown 期间重读 OFF_TIME”依赖作者的寄存器表和实测，
  无 M5IOE1 数据手册或固件源码独立确认。
- **新增 `m5stack,power-controller` 属性的启动路径**: 作者明确写了“booting with the
  updated overlay”未测，实机跑的是 `disabled-gpios` 回退路径；本记录只验证了 dtbo 形态。

## 6. 结论与后续

- 回复一条英文评审：结论（设计可行、无阻塞）+ 证据等级（code-level verification /
  host-level test）+ 上述 3 项 + 未覆盖项。
- 不关闭 PR、不 push 上游、不改他人仓库。
- 若作者接受 4.1 的改法，可等待其更新后做一次同 harness 的回归；否则维持现状也可，
  但建议至少补上“丢弃分支还原 `OFF_TIME`”这一行。
