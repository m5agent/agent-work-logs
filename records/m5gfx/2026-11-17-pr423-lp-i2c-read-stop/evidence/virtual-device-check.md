# 虚拟设备边界（QEMU ESP32-C6）

- 采集时间：2026-11-17 00:16（CST）
- 对象：esp-emulator 平台使用的 QEMU ESP32-C6 机器（源树 `hw/riscv/esp32c6.c`、
  `hw/misc/esp32c6_lp.c`）

## 观察到的事实

1. C6 机器只为 Nesso 板注册了 **HP I2C0**（`hw/riscv/esp32c6.c:554-584`，
   `TYPE_ESP32_I2C` 挂在 `DR_REG_I2C_EXT_BASE`），并挂了 pi4ioe / ft5x06 / bmi270 /
   bq27220 / aw32001 等板级 I2C 从设备。
2. LP 域模型 `hw/misc/esp32c6_lp.c` 只处理 LP_CLKRST / LP_AON / LP_TIMER。RTC I2C 子块
   （`0x1800-0x18FF`）在读路径上返回 `0x00FFFFFF`（注释：为了让 early-boot 的轮询尽快退出），
   写路径没有对应分支，直接丢弃（读 `:79-83`、写 `:88-110`）。
3. 因此 QEMU 的 C6 机器里没有可用的 LP I2C 控制器，也没有 ST25R3916（UnitNFC）模型。

## 结论

- LP 端口的寄存器写入被丢弃、读回 all-ones，无法执行 `i2c_new_master_bus()` 之后的真实
  传输，也无法观察 STOP 是否上总线。
- 有 C6 的 device profile，但没有 C5 的 profile；即使换到 C6，也缺少被测从机（ST25R3916）
  和 LP I2C 控制器模型。
- 所以本 PR 的 virtual-device validation 为 `NOT RUN`，而不是未尝试。
