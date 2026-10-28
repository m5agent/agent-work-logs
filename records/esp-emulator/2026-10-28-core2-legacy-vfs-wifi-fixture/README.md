# ESP Emulator Core2 legacy VFS 与 WiFi fixture 校正

- 日期：`2026-10-28`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：Core2 legacy UIFlow `RUNTIME-03` 复测
- 源码版本：`m5agent/m5stack-esp-emulator @ 0f357b7eccfc642c6efd31141af5d816f590a2ae`
- 环境：Core2 `UIFlow_Core2 v1.15.4`，QEMU `m5core2`，Device Service
  `runtime=qemu-wifi` / `profile=core2-openmac`

## 结论

旧 legacy 黑帧诊断混入了两个测试夹具问题：通用 LittleFS 镜像被 guest
拒绝，以及裸 QEMU 路径没有实例化 `misc.esp32_wifi`。改用 UIFlow
checkout 自带 LittleFS2 packer 和正式 WiFi-backed Device Service 后，
120 秒虚拟时间已执行注入的 `/flash/boot.py` 并输出
`CORE2_LEGACY_VFS_BOOT`。但系统 setup/main 和非空画面仍未出现，
normal-WDT 仍 reset，因此本记录只关闭 fixture 校正，不关闭
`RUNTIME-03`。

## 关键证据

- 测试镜像：`893d3535…`，仅替换源码固件的 VFS partition。
- VFS payload：`805e1acd…`，由 `littlefs2` packer 生成。
- QEMU：`3b56b49a…`，`runtime=qemu-wifi`。
- 120 秒快照：CPU0 `0x40249c5d`、CPU1 `0x400e1ffd`。
- Serial：`575` bytes，包含 `APIKEY` 与 `CORE2_LEGACY_VFS_BOOT`。
- Frame：`320x240`，`0` nonblack pixels，SHA256 `57580743…`。
- Session ID SHA256：`9002382d…`。
- 平台测试：`1362` 项通过，`1` skip；四个生成器检查通过。

## 文件

- `report.md`：根因、修复和验证边界。
- `run.json`：机器可读记录。
- `evidence/summary.json`：脱敏后的检查摘要。

## 未覆盖项

- legacy setup/REPL 和非空应用帧未通过；
- normal-WDT 产品门禁未通过；
- 旧 `0x40100049` LVGL 等待未在 corrected lane 复现，需重新绑定；
- 物理硬件、RF、cache timing 和电气行为 `NOT RUN`。
