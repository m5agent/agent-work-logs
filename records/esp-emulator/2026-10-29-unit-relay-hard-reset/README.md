# ESP Emulator Relay/Relay2 hard-reset boundary

- 日期：`2026-10-29`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：`UNIT-HOST-36`
- 源码版本：`m5agent/m5stack-esp-emulator@228283907ff6067e17a0cf8823c76f3fb97200a3`
- 环境：macOS Apple Silicon；AtomS3R UIFlow2 QEMU；Device Service `/api/v1`

## 结论

共享 legacy GPIO reset 现在先建立复位后的 route/level，再通知 Unit reset
observer，最后才执行正常 output listener 和 transition IRQ。Relay/Relay2
从实际 post-reset pad 重定 previous level 并清零数字 transition counter，
因此 high→hard-reset-low 不会被计为新的 guest edge。

同一 AtomS3R 固件下，pre-fix QEMU 对单 Relay/Relay2 复现跨 reset 计数泄漏；
fixed QEMU 在复位后清零并分别观察到 gpio-1、gpio-2 的独立 transition。
结果只覆盖 virtual-device 数字 GPIO。

## 关键证据

- 固定固件 SHA256：`ab4dd742a342f85037c3c0cb2c67c037bf5eef7cf429bee131d2227d4a404e3d`
- pre-fix QEMU SHA256：`9aca9a8db5143ad133510795cd228ed8ac23c388ea197267d7b2b4750e58eb82`
- fixed QEMU SHA256：`e318b2b748d6e982cd2e592a1b991ec930a8e9501cf02a0c19925022a656b373`
- fixed 2Relay：reset 后 level `0/0`、counter `0/0`；随后 `1/0 -> 1/1`
- fixed Relay：reset 后 counter `0`，warm low 基线 `1`，gpio-2 高后 `2`
- platform：`1558 tests OK, 10 skipped`
- PR #36 CI：两个 run 各 `2/2 PASS`；main CI `2/2 PASS`
- merge：`16580f97228908c3d0f11dcbec71f7f9a530a747`

## 文件

- `report.md`：根因、实现和 A/B 执行
- `run.json`：结构化记录
- `evidence/verification.summary.json`：脱敏机器摘要
- `evidence/fixed-2relay.serial.log` / `fixed-relay.serial.log`：fixed guest 串口
- `evidence/prefix-2relay.summary.json` / `prefix-relay.summary.json`：pre-fix 负控摘要

## 未覆盖项

机械触点、线圈/负载、电气、光学和 physical hardware 为 `NOT RUN`。本次只
验证 AtomS3R 的一个 guest；其它 host/model 组合、FlashLight reset 和其它 Unit
reset 语义不继承。Preview reset 仍禁用。
