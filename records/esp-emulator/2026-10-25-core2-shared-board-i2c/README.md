# ESP Emulator Core2 legacy shared board I2C

- 日期：`2026-10-25`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：Core2 legacy UIFlow 启动链中 RTC `0x51` 无 ACK
- 源码版本：
  [`m5agent/m5stack-esp-emulator@105ad247`](https://github.com/m5agent/m5stack-esp-emulator/commit/105ad247315644acccef96352a93269c27c67450)
- Base commit：`2175ebbbc94a3de7cd1fc775641e01659cfc2b31`
- 环境：macOS arm64、Python 3.13、Node 20、QEMU virtual-device

## 结论

Core2 的 ESP32 有两个 I2C controller register block，但板级 AXP、RTC、touch
和 IMU 实际共享同一条 GPIO21/22 物理 bus。旧板模型把 RTC/touch/IMU 只挂在
controller 1，而公开 legacy UIFlow 在 controller 0 上访问 RTC，导致
address `0x51` 无 ACK，随后返回 `OSError: I2C bus error (19)`。

`0031` 将两个 controller 都路由到唯一物理 board bus，并保持每个 slave 只挂
一份。同一固件 SHA 修复后，AXP `0x34`、RTC `0x51` 和 INA3221 `0x40`
的 write/read 都获得 ACK，原 I2C error 消失。现有 UIFlow2 Core2 设备组
`6/6`、`24/24` checks 无 retry 回归通过。

该修复只关闭 controller-to-physical-bus routing。同一 legacy UIFlow 固件随后
进入独立的 interrupt-WDT reset/panic，frame 仍为 black，因此完整 legacy
firmware、`RUNTIME-03` 和物理硬件都不能标记为 PASS。

后续 WDT timing diagnosis 进一步确认：默认单会话可持续 feed 超过 285 秒，
而多个并发 lease 和显式 accelerator 对照会在不同 CPU/PC 触发 WDT。详细
follow-up 见
[`followups/2026-10-25-wdt-timing-diagnosis/`](followups/2026-10-25-wdt-timing-diagnosis/)。

## 关键证据

- 公开 `UIFlow_Core2 v1.15.4`，firmware ID `1897200000000002280`，source
  SHA-256 `18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`；
- 修复前：123 个事务均在 controller 0，`0x34` ACK，`0x51` `start_rc=1`；
- 修复后：480 个事务均在 controller 0，`0x34`、`0x51`、`0x40` 均有
  write/read ACK；
- `M5SW_CORE2_PMIC=axp192` 变体也越过原 I2C error；
- UIFlow2 Core2 外设组 `6/6 PASS`，checks `24/24`，无 retry；
- 后续失败：CPU1 interrupt-WDT、CPU0 interrupt-WDT、reset loop、black frame；
- 文档/代码门禁：平台 `498/498`、文档契约 `38/38`、Node UI smoke、
  runtime coverage、peripheral catalog、QEMU profiles、snapshot、compileall、
  selected Ruff、patch reverse-check 和 `git diff --check` PASS；
- GitHub Actions `40204089670` 的 `platform-contracts` 与
  `network-namespace-policy` 两个 job 均成功。

## 文件

- `report.md`：根因、修复、执行证据、验证层级和边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：修复前后 trace、回归、CI 与剩余失败摘要。
- `followups/2026-10-25-wdt-timing-diagnosis/`：TIMG watchdog trace、
  单实例/并发/accelerator 对照和后续 `RUNTIME-03` 边界。

## 未覆盖项

- legacy UIFlow 的非空应用帧与稳定运行；
- WDT 前最后一次 feed 对应的具体 guest 代码点，以及稳定 accelerator 配置；
- `Core2FactoryTest` 修复后的重跑；
- 物理 I2C timing、电气特性和真机；
- bit-exact ESP32 radio/controller、物理 PSRAM/cache timing；
- 其他 Core2 firmware SHA 的兼容性继承。
