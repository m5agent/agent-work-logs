# M5GFX #426 完整报告：LP I2C 的 `i2c_stop()` 恢复路径

## 1. 条目与目标

- 条目：`m5stack/M5GFX#426`，日文，作者 GOB52，2026-11-17T01:58:10Z 创建。
- 标题：「LP I2C ポートでは、i2c_stop() によるバスの復旧がピンに届かない」
- 目标：核对报告中的 5 条路径、失效机理与影响，并对作者提出的两个方向给出可核对的代码事实。
- 结论层级：`code-level verification`。没有运行时验证，不把它写成硬件或虚拟设备结果。

## 2. 背景

M5GFX 的 ESP32 I2C 实现（`src/lgfx/v1/platforms/esp32/common.inl`）在 HP I2C 出错或
总线卡住时，用 `i2c_stop()` 以普通 GPIO 位操作发出 9 个时钟和 STOP，然后复位控制器。
ESP32-C5 的 LP I2C 端口把 SDA/SCL 交给 LP IO 域（M5GFX 自己也在 `:2304-2308` 注明
`set_pin()` 不适用于 LP 端口），因此这套 GPIO 位操作是否真的到达焊盘，是 #426 的核心。

前置：#421 报告 LP 端口 read 结束缺少 STOP；作者提交 PR #423（`cc60eaa`，仍 OPEN）改走
控制器 STOP。本 issue 处理 #423 未覆盖的错误/超时/初始化恢复路径。

## 3. 核对结果

### 3.1 调用点完整且与报告一致

在 `b48dce0` 全仓检索 `i2c_stop(`，除定义外只有 5 处调用：

| 报告位置 | 实际行 | 场景 |
| --- | --- | --- |
| `common.inl:1997` | 1997 | `i2c_wait()` 进入强制 STOP 分支 |
| `common.inl:2022` | 2022 | 控制器 STOP 未完成后的回落 |
| `common.inl:2255` | 2255 | `init()` 的首次总线恢复 |
| `common.inl:2548` | 2548 | `beginTransaction()` 发现 bus busy |
| `common.inl:2754` | 2754 | `readBytes()` 超时 |

行号与报告完全一致，没有遗漏的调用点。`b48dce0` 上 read 结束也会因
`i2c_context[port].state == state_read` 进入 `:1993` 的强制 STOP 分支，所以 #423 合并前正常
read 也经过 `:1997`；#423 只改 read 终端，表中 5 条（错误/超时/恢复）仍然成立。

### 3.2 `i2c_stop()` 只操作普通 GPIO

`:1847-1882` 的实现：

- `gpio_set_level()` / `gpio_set_direction()`（IDF 数字 GPIO API）、`gpio_get_level()`；
- `gpio::pin_backup_t` 保存/恢复引脚；
- 必要时 `i2c_periph_reset()`。

IDF v5.5 `gpio_set_direction()`（`components/esp_driver_gpio/src/gpio.c:306-336`）只做
`gpio_input_enable/disable`、`gpio_output_enable/disable`、`gpio_od_enable/disable`，
不调用 `gpio_ll_func_sel`，也不碰 IO MUX。C5 的 LP 焊盘在 IDF 的
`s_lp_i2c_pins_config()`（`components/esp_driver_i2c/i2c_common.c:355-399`）里用
`rtc_gpio_init()` + `rtc_gpio_set_direction(INPUT_OUTPUT_OD)` + pull 配置 +
`rtc_gpio_iomux_func_sel(..., i2c_periph_signal[port].iomux_func)` 接到 LP I2C。
`i2c_stop()` 的寄存器写不在这条路径上，因此不会把焊盘从 LP I2C 切到 GPIO，也不会驱动它。

`gpio_get_level()` 读的同样是数字 GPIO 的输入寄存器，而 LP 焊盘的输入此时接在 LP 域；
`while (!gpio_get_level(sda_io) && i++ < 9)` 的结果与总线实际电平没有确定关系。

### 3.3 `pin_backup_t` 在 C5 不覆盖 RTC/LP 侧

`LGFX_GPIO_RTC_INDEPENDENT` 在 `common.hpp:66` 映射到 `SOC_GPIO_SUPPORT_RTC_INDEPENDENT`；
C5 的 `soc_caps.h:217` 定义为 1。于是 `pin_backup_t::backup()`（`:783`）和
`restore()`（`:836`）都跳过 RTC 寄存器，只保存/恢复 `IO_MUX`、`GPIO_PIN`、
`FUNC_OUT_SEL` 等数字侧寄存器。即使有人在借用前手动 `release_lp_pad()`，`i2c_stop()` 自身
也没有把 LP 侧接回去的能力。

### 3.4 LP 复位只复位控制器

`:1580-1596`：LP 端口走 `lp_i2c_ll_reset_register(port - HP_NUM)`。IDF v5.5
`components/hal/esp32c5/include/hal/i2c_ll.h:875-882` 的实现是：

```c
LPPERI.reset_en.lp_ext_i2c_reset_en = 1;
LPPERI.reset_en.lp_ext_i2c_reset_en = 0;
```

即一次寄存器复位脉冲，没有总线动作，函数返回 `void`。`i2c_stop()` 本身也是 `void`，
所以“恢复失败”无法上报，调用方只看到流程继续。

### 3.5 影响

与报告一致：LP 端口上发生错误、超时或 init 时发现总线被拉低，从设备不会收到 STOP，
也不会收到恢复时钟，可能停在传输中间；控制器被复位，但总线状态没变。随后 M5GFX 会把
`i2c_context` 里的寄存器快照重新写回（`i2c_wait()` 的 `:2042`、`init()` 重建总线、
`beginTransaction()` 的 `restart()`），所以问题不在“控制器没恢复”，而在“从设备没被复位”。

## 4. 两个方向的代码层评估

### 4.1 案 2：用 LP I2C 控制器的 bus clear + STOP

C5 的 LP I2C 寄存器块**有** bus clear 相关寄存器：

- `lp_i2c_struct.h:352-380`：`scl_sp_conf`，含 `scl_rst_slv_en`（R/W/SC）与
  `scl_rst_slv_num`（5 bit）；`:869` 确认它在 `lp_i2c_dev_t` 中。
- `lp_i2c_struct.h:224`：`ctr.conf_upgate`。
- `hal/esp32c5/include/hal/i2c_ll.h:755-795`：`i2c_ll_master_fsm_rst()`、
  `i2c_ll_master_clr_bus(hw, slave_pulses, enable)`、
  `i2c_ll_master_is_bus_clear_done(hw)`。

但 C5 的 `soc_caps.h` **没有** `SOC_I2C_SUPPORT_HW_CLR_BUS`（S3:219、C6:252、P4:310 都有）。
所以在 C5 上 IDF 自己的 `i2c_master_bus_reset()` 会走
`i2c_master.c:60-104` 的 `#if !SOC_I2C_SUPPORT_HW_CLR_BUS` 分支：`gpio_set_direction` +
`gpio_set_level` 位操作，末尾 `i2c_common_set_pins()` 还原。对 LP 总线，这段同样到不了焊盘
（和 M5GFX 的 `i2c_stop()` 是同一类问题），因此 IDF 不能作为 LP 端口的参考实现。

结论：寄存器/IP 层面案 2 值得试，但“LP 实例真的会发出 9 个 SCL 脉冲”只能实机确认
（本记录 `NOT RUN`）。另外，bus clear 只发时钟，STOP 仍需单独用命令列发出，并要处理
`conf_upgate` 与超时。

### 4.2 案 1：借用焊盘后再还给 LP

IDF 的 LP 引脚配置顺序（`i2c_common.c:355-399`）：

1. `rtc_gpio_init(pin)`
2. `rtc_gpio_set_direction(pin, RTC_GPIO_MODE_INPUT_OUTPUT_OD)`
3. `rtc_gpio_pulldown_dis(pin)`
4. `rtc_gpio_pullup_en(pin)`（若启用内部上拉）
5. `rtc_gpio_iomux_func_sel(pin, i2c_periph_signal[port].iomux_func)`

SDA、SCL 各一遍。另有两点：

- `rtc_gpio_deinit()`（`gpio::release_lp_pad()` 用它，`common.inl:737-754`）在
  `SOC_LP_IO_CLOCK_IS_INDEPENDENT=1` 的芯片上会调用
  `io_mux_force_disable_lp_io_clock()`；`rtc_gpio_init()` 会重新
  `io_mux_enable_lp_io_clock()`（IDF v5.5 `rtc_io.c:44-73`）。C5 该宏为 1
  （`soc_caps.h:221`）。
- 作者描述失败版本只写了 `rtc_gpio_init()` + `rtc_gpio_iomux_func_sel()` 还原，随后
  `M5.begin()` 里的 PM1 配置失败。上面第 2、3、4 步是否包含在该版本中，issue 里没有写；
  这是待作者确认的差异点，**不是本记录给出的根因**（未定位）。

## 5. 执行过程

```bash
git clone --depth 60 --branch develop https://github.com/m5stack/M5GFX.git
# HEAD = b48dce04c80d3e3c9874b7ba946c43d672129c28
grep -rn "i2c_stop(" src/lgfx/v1/platforms/esp32/
# 仅定义 + 5 处调用

curl -sL .../esp-idf/v5.5/components/esp_driver_i2c/i2c_common.c
curl -sL .../esp-idf/v5.5/components/soc/esp32c5/register/soc/lp_i2c_struct.h
curl -sL .../esp-idf/v5.5/components/hal/esp32c5/include/hal/i2c_ll.h
curl -sL .../esp-idf/v5.5/components/soc/esp32c5/include/soc/soc_caps.h
curl -sL .../esp-idf/v5.5/components/esp_driver_gpio/src/gpio.c
curl -sL .../esp-idf/v5.5/components/esp_driver_gpio/src/rtc_io.c
curl -sL .../esp-idf/v5.5/components/esp_driver_i2c/i2c_master.c
```

Device Service：`GET /api/v1/devices` 返回 36 个 profile，SoC 列表中没有 ESP32-C5。
esp-emulator：`devices/` 只有 `esp32-c6` / `esp32-lx6` / `esp32-p4` / `esp32-s3` 等目录，
`devices` 与 `third_party/upstream` 中没有 `lp_i2c` / `LP_I2C` 模型文件。

## 6. 风险与边界

- 结论只覆盖 `b48dce0` 的源码与 IDF v5.5 头/实现；不同 IDF 版本或 Arduino-ESP32 内核的
  `gpio_set_direction` 实现需要重新核对。
- 没有测量 LP 端口的真实波形，因此“到不了引脚”是代码层推导（与作者实机观察一致），
  不是本记录的示波器结论。
- 没有验证 `i2c_periph_reset()` 之后从设备需要怎样的恢复序列；案 2 的 STOP 顺序、
  `conf_upgate` 同步与超时上限都未实测。
- 未改任何代码，未向上游 push，issue 保持 OPEN。

## 7. 回复

日文单条回复，结构为 結論 → 証拠等級 → コード位置 → 未カバー項，正文见
`evidence/reply-ja.md`。已发布：<https://github.com/m5stack/M5GFX/issues/426#issuecomment-6935810184>。
