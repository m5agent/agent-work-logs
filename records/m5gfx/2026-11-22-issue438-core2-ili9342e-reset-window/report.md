# M5GFX #438 报告：Core2（AXP192）+ ILI9342E 复位后初始化落在 120 ms 重载窗口内

## 1. 背景

`m5stack/M5GFX#438`（作者 `svengrun`，英文，2026-11-22 提交）报告 M5Stack Core2
（AXP192，`M5.getBoard() == 2`）配 ILI9342E 面板时，每隔一次 ESP32 复位就黑屏一次，
严格交替。作者用 `RDDPM 0Ah` / `RDDST 09h` 读回证明：

| 启动 | RDDPM raw | 解码 | 画面 |
| --- | --- | --- | --- |
| good | `0x38` | `0x9C`：booster on、Sleep Out、normal、display on | 有画面 |
| blank | `0x10` | `0x88`：booster on、Sleep In、display off | 黑屏 |

作者给出的解释是：复位时面板处于 Sleep Out，ILI9342E 会先从 NV 重载寄存器，
最长 120 ms（datasheet 12.4）；M5GFX 在面板刚回读键值（约 6 ms）后就把初始化序列发下去，
被重载抹掉；下一次复位时面板已在 Sleep In，重载很短，于是成功——所以严格交替。
此外 `CORE_DEBUG_LEVEL=3`（多约 9 ms 日志）能掩盖问题，应用侧 130 ms 预置延时能消除问题。

本次工作要回答两点：

1. 0.3.0 的代码路径是否真的在复位后 ~10 ms 量级就发初始化，且 120 ms 只当上限；
2. 在没有 Core2 实机的条件下能给出到哪一层的结论。

## 2. 代码路径（`28d4794`，v0.3.0）

### 2.1 复位参数是 1 ms 拉低 + 10 ms 释放后等待

`src/board_detect/m5/esp32_d0wdq6.inl:60`：

```cpp
i2c_power(400000, core_pmic_variants, pmic_ops::core2_devices, 5, 20), i2c_reset(1, 10),
```

`i2c_reset(low_ms, post_ms)`；`src/board_detect/prepare.inl:510` 在释放后执行
`io::delay_ms(reset.post_ms)`，也就是 **10 ms**。Core2 与 Tough 共用该描述符
（`:60` 与 `:75` 两处相同参数）。

### 2.2 复位后探测把 120 ms 当上限，不是等待

`src/board_detect/m5/esp32_d0wdq6.inl:488-517`：

```cpp
variant = identify_panel_variant(bus, display.cs, keys, ctx.allow_reset ? 1 : 120);
if (ctx.allow_reset)
{
  ...
  if (!i2c.opened || !prepare_reset(desc_core2, result, ctx, i2c.port)) { ... }
  std::uint32_t after_keys[4] = {};
  const auto after = identify_panel_variant(bus, display.cs, after_keys,
                                            120, variant != panel_variant_t::e);
```

`src/board_detect/m5/board_registry.inl:170-183`：

```cpp
panel_variant_t identify_panel_variant(soft_spi_t& bus, int pin_cs,
                                       std::uint32_t keys[4], std::uint32_t poll_ms,
                                       bool try_c_key = true)
{
  auto variant = probe_panel_variant(bus, pin_cs, keys, try_c_key);
  const auto started = io::millis();
  while (variant == panel_variant_t::unknown && poll_ms)
  {
    io::delay_ms(1);
    variant = probe_panel_variant(bus, pin_cs, keys, try_c_key);
    if (io::millis() - started >= poll_ms) { break; }
  }
  return variant;
}
```

E 的判定键在 `:150`：`if (keys[0] == 0x01 && keys[1] == 0x1C) { return panel_variant_t::e; }`，
与作者日志 `DDh:01 CBh:1c -> ILI9342E` 一致。面板一旦回读成功，循环立即退出，
`poll_ms = 120` 完全不会被执行到。于是初始化开始在 **10 ms 后加少量 1 ms 轮询**的量级，
远小于 120 ms。

### 2.3 检测之后不会再有第二次复位

`src/M5GFX.cpp:997-1002`：

```cpp
bool M5GFX::_init_adopted_panel(bool use_clear)
{
  // Detection and preparation have already handled reset. Construction
  // and panel initialisation must not pulse it again.
  if (false == LGFX_Device::init_impl(false, use_clear)) {
```

`LGFX_Base.hpp:1433` 的 `begin()` 是 `init_impl(true, true)`，所以检测阶段这次复位
就是初始化前唯一的一次；`Panel_Device::init(use_reset=false)` 里那 8 ms + 64 ms 的
二次复位等待不会发生。

### 2.4 初始化列表自带的 120 ms 在 SLPOUT 之后

`src/lgfx/v1/panel/Panel_ILI9342.hpp:86-101`（ILI9342E 列表）：

```cpp
CMD_SETEXTC_E, 1, 0x01,
0xD5       , 1, 0x00,
...
CMD_IDMOFF , 0,
CMD_DISPON , 0,
CMD_SLPOUT , 0 + CMD_INIT_DELAY, 120,    // Exit sleep mode
```

`Panel_Device::command_list()`（`src/lgfx/v1/panel/Panel_Device.inl:196-218`）先写命令、
再写参数、最后才 `delay(ms)`。所以 `120` 是 SLPOUT 写入之后的延时，
保护不到它前面的 EXTC / 电源 / gamma / `IDMOFF` / `DISPON`；而且 `DISPON` 排在
`SLPOUT` 之前，本来也不符合"先退出睡眠、等 120 ms、再开显示"的顺序。

结论：`PR #300` 描述中的 "After the reset the probe is repeated every millisecond until
the panel answers its keys again (at most 120 ms), which also keeps the init sequence out
of the reload window" 对 ILI9342E 不成立——回读键值恢复（约 6 ms）早于 NV 重载完成（最长 120 ms）。

## 3. 修复位置

检测阶段已经知道"复位前面板是否在显示"：`observe_core_panel()` 里复位前的
`identify_panel_variant()` 若已识别出 E/C，说明面板当时处于 Sleep Out。

可行的最小改动：当"复位前已识别面板 + 本次确实施加了复位"（`ctx.allow_reset`）时，
把初始化推迟到复位释放后满 120 ms，例如在 `prepare_reset()` 返回后再
`io::delay_ms(120 - reset.post_ms)`，或给 Core2 的 `reset.post_ms` 单独取 120。
作者建议的"复位前已在显示的场合等满 120 ms"与代码里可得的信息一致；
冷启动、以及"复位前不回读、只能先复位"的分支不需要等满。代价是热启动最多多约 110 ms，
与作者在应用侧加的 130 ms 同量级。

## 4. 证据等级

- **code-level verification**：2.1–2.4 全部来自固定 commit `28d4794` 的源码，行号可核对。
- **hardware validation**：`NOT RUN`。本机硬件测试中心 5 个节点（4 在线）只有
  `matrix` / `profile=unknown`，没有 Core2，也没有 AXP192 + ILI9342E 的同路径替代板。
  作者正文里的实机数据（6/12、0/8、0/20、0/26 等）属于引用，不构成本次实测。
- **virtual-device validation**：`NOT RUN`，原因见第 5 节，不是跳过。

## 5. 为什么没有虚拟设备复现

本机 Device Service 有 `core2` profile（`backend=qemu-esp32lx6`、`machine=m5core2`、
显示 `ILI9342C / ILI9342E`、`display/touch` 均可观测），所以不是缺 profile。

缺的是**面板外设模型的行为**。模拟器 Core2 的面板 sink（`hw/m5stopwatch/m5_spi_panel.c`，
见 `m5agent/m5stack-esp-emulator` 的 `patches/qemu-m5stack-peripherals/`）：

- `0x10` 只置 `sleep = true`、`0x11` 只清 `sleep`，画面可见性由
  `disp_on && !sleep` 直接推导，没有任何时间量；
- `realize` 时 `sleep = true`；模型没有注册设备复位回调，也没有"复位后从 NV 重载最长 120 ms"
  或"Sleep Out 下复位后回到 Sleep In"的转移。

也就是说，即使把 M5GFX 固件跑起来，热复位后模型也不会吞掉初始化命令，
"好 / 黑"交替在该模型里不可表达。这样的运行只能得到"每次都好"，会把模型缺口
当成"问题不存在"，所以本次没有把它当作复现。

构建链方面同样不可得：本机没有 Arduino/ESP-IDF 工具链；`docker run` 在本机容器上
直接失败（`containerd metadata ... read-only file system`），无法用 `espressif/idf` 镜像
编一个最小 M5GFX sketch。两项都记在 `run.json` 的 `execution.environment`。

## 6. 未覆盖项与风险

- 物理 Core2 + ILI9342E 的复位时序与修复效果：`NOT RUN`；本文不主张修复已验证。
- Core2 v1.1（AXP2101，`rst_reg = 0x90`）与 Tough 的 120 ms 行为：未评估。
- 0.2.34（作者现用版本）与 0.3.0 的逐行差异未做；作者已声明 0.3.0 同形，
  本次核对 0.3.0 后同意该判断。
- 修复建议未实现、未编译、未上机；`120 - post_ms` 的写法需要同时考虑 Tough 的触摸
  控制器时序，改动前应跑一次 Core2/Tough 启动回归。

## 7. 回滚

只读分诊，无代码改动、无服务切换，无需回滚。

## 8. 发布

GitHub 单条英文回复，结构为 结论 → 证据等级 → 代码位置 → 未覆盖项，
引用本记录固定 commit 的 permalink。
