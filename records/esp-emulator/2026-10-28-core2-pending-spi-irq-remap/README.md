# Core2 pending SPI IRQ remap

- 日期：`2026-10-28`
- 结果：`PASS`（限定 pending SPI IRQ remap；legacy `RUNTIME-03` 仍为 `OPEN`）
- 工作类型：`code_change`
- 问题来源：项目 Backlog `RUNTIME-03` 及既有 Core2 LVGL/SPI completion 诊断
- 源码版本：
  [`m5agent/m5stack-esp-emulator@f3bab9c0`](https://github.com/m5agent/m5stack-esp-emulator/commit/f3bab9c0dfcb8a1928fc3f2e064d973a9ac252c9)
- 环境：macOS arm64；QEMU Xtensa；ESP-IDF `5.5.4`；QEMU `m5core2`

## 结论

`0064-esp32-intmatrix-pending-irq-remap.patch` 修复了 ESP32
interrupt matrix 在 source level 已高时改写 mapping 却不重新计算 CPU
interrupt output 的缺陷。独立的 Core2 ESP-IDF SPI3 guest 探针在同一
firmware/ELF 上从 pre-fix callback timeout 变为 fixed `3/3 PASS`。

同一 fixed runtime 的 Core2 UIFlow2 设备组保持 `6/6 PASS`，attempt 1、
无 retry。该结果关闭通用 SPI/INTMATRIX completion 子缺口，但不把 legacy
UIFlow 黑帧或 `lv_disp_flush_ready` 问题升级为 PASS。

## 关键证据

- pre-fix QEMU `03ae86b5…`：SPI queue 已建立，但 guest callback timeout；
- fixed QEMU `22bf9dba…`：三个独立 guest 运行均返回 post callback 和
  queued-transaction result；
- probe firmware `1f4d1b40…`，ELF `00d946fe…`；
- Core2 UIFlow2 设备组：touch/RTC/PWR、Speaker/Mic、INA3221、MPU6886、
  AXP192，`6/6 PASS`；
- 平台测试 `1354` 项 `OK`（1 skip），docs contracts `48/48 PASS`；
- GitHub CI run
  [`40655925155`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40655925155)
  两个 job PASS。

## 文件

- `report.md`：根因、执行、证据和边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：可机器读取的摘要
- `patches/README.md`：固定 commit patch 链接与 digest

## 未覆盖项

- legacy `UIFlow_Core2 v1.15.4` 仍未到达 display completion，仍无 REPL 或
  非空应用帧；
- `Core2FactoryTest` 未重跑；
- 物理 ESP32 SPI timing、电气行为和真机验证 `NOT RUN`；
- 更大的 UIFlow2 全矩阵未因本次定向 SPI/INTMATRIX 修复自动宣称通过。
