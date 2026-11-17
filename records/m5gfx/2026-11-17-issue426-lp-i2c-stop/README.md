# M5GFX #426：LP I2C 端口上 `i2c_stop()` 的恢复动作到不了引脚

- 日期：`2026-11-17`
- 结果：`PARTIAL`（仅代码层确认报告；硬件 / 虚拟设备 / 构建均 `NOT RUN`）
- 工作类型：`issue`
- 条目：[m5stack/M5GFX#426](https://github.com/m5stack/M5GFX/issues/426)
  「LP I2C ポートでは、i2c_stop() によるバスの復旧がピンに届かない」，作者 GOB52，日文，OPEN，取得时评论 0
- 源码：`develop` `b48dce04c80d3e3c9874b7ba946c43d672129c28`；ESP-IDF v5.5 的 C5 头文件与驱动实现
- 环境：macOS。本机无 ESP32-C5；Device Service 36 个 profile 里没有 C5；
  esp-emulator 没有 C5 QEMU 机，C6 / P4 的 LP I2C 控制器也未建模

## 结论

报告列出的 5 条路径与 `develop` `b48dce0` 完全一致，且这 5 处是 `i2c_stop()` 的全部调用点
（`:1997`、`:2022`、`:2255`、`:2548`、`:2754`）。LP 端口上该函数只会复位 LP I2C 控制器，
不会向总线送出 STOP 或恢复时钟：

1. `i2c_stop()` 只用 `gpio_set_level` / `gpio_set_direction` / `gpio_get_level` 和
   `pin_backup_t`（`:1847-1882`）。IDF v5.5 的 `gpio_set_direction()` 只开关 input / output /
   open-drain 使能，不切换 IO MUX；C5 的 LP 焊盘由 IDF 的 `s_lp_i2c_pins_config()` 用
   `rtc_gpio_iomux_func_sel()` 接到 LP I2C，`i2c_stop()` 完全不经过这条路径。
2. C5 上 `LGFX_GPIO_RTC_INDEPENDENT=1`，`pin_backup_t` 不备份/恢复 RTC/LP 侧寄存器
   （`:783`、`:836`），所以“借用后还原”也没有覆盖 LP 侧。
3. 末尾的 `i2c_periph_reset()` 在 LP 端口只调用 `lp_i2c_ll_reset_register()`
   （`:1582-1590`），IDF v5.5 实现是给 LPPERI 一个 reset 脉冲，返回 void；总线无动作，
   失败也不会返回给调用者。
4. `b48dce0` 上 read 结束同样因 `state == state_read` 进入强制 STOP 分支，因此 #423 合并前
   正常 read 也会经过 `:1997`；#423 之后表中列出的错误路径仍然存在。

对作者提出的两个方向，代码层能补充的是：

- 案 2（控制器 bus clear + STOP）：C5 的 **LP I2C** 寄存器块确实有 `scl_sp_conf`
  （`scl_rst_slv_en` / `scl_rst_slv_num`）和 `ctr.conf_upgate`，但 C5 的 `soc_caps.h` 没有
  `SOC_I2C_SUPPORT_HW_CLR_BUS`（S3 / C6 / P4 有），IDF 自己的 `i2c_master_bus_reset()` 在 C5
  上走 GPIO 位操作兜底路径，不能当 LP 的参考实现；LP 实例是否真的发出 9 个时钟需实机确认。
- 案 1（借用焊盘再还原）：IDF 的还原序列还包含 `rtc_gpio_set_direction(INPUT_OUTPUT_OD)`、
  `rtc_gpio_pulldown_dis`、`rtc_gpio_pullup_en`；`rtc_gpio_deinit()` 会按引脚强制关闭 LP IO
  时钟，`rtc_gpio_init()` 再打开。作者失败的那版是否漏了 direction / pull，需要作者确认，
  本记录未定位该失败原因。

## 关键证据

- 调用点与函数体：`evidence/m5gfx-source-lines.txt`（`b48dce0` 的 `common.inl` 摘录）
- IDF LP 引脚配置、GPIO 语义、RTC IO 时钟：`evidence/idf-v55-lp-i2c-pins.txt`
- C5 LP I2C 的 bus clear 寄存器与 LL 函数：`evidence/idf-v55-lp-i2c-registers.txt`
- 各目标 `SOC_I2C_SUPPORT_HW_CLR_BUS` 对照与 IDF 兜底实现：`evidence/idf-v55-caps-and-bus-clear.txt`
- 边界：`evidence/virtual-device-check.md`、`evidence/hardware-inventory.md`
- 条目元数据与回复正文：`evidence/issue-426.json`、`evidence/reply-ja.md`
- 已发布回复：<https://github.com/m5stack/M5GFX/issues/426#issuecomment-6935810184>（1 条，Issue 保持 OPEN，未改代码）

## 文件

- `report.md`：代码事实、两方案评估、边界
- `run.json`：结构化记录
- `evidence/`：源码与 IDF 摘录、边界说明、回复原文

## 未覆盖项

- hardware validation：`NOT RUN`。没有 ESP32-C5 实机，未用逻辑分析仪/示波器观察 SDA/SCL，
  也未验证 LP 端口出错后从设备是否真的停在传输中间。
- virtual-device validation：`NOT RUN`。Device Service 无 C5 profile；esp-emulator 无 C5 机，
  C6/P4 的 LP I2C 控制器未建模；问题依赖 LP 焊盘路由，GPIO 级模型无法复现。
- 案 1 / 案 2 的成立与否：`NOT RUN`。只做了代码层候选整理，没有补丁、没有构建、没有实机。
- C6 / P4 等其他 LP I2C 芯片：`NOT RUN`。
- 上游合并：未改 M5GFX 代码、未提 PR、未 push；issue 保持 OPEN。
