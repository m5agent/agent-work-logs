# 原生固件兼容性后续与固件 SDK 对照

- 日期：`2026-11-13`
- 结果：`PARTIAL`；逐项结果分列，未授予全固件通过。
- 工作类型：`code_change / issue / service_debug`
- 问题来源：[模拟器公开 issues](https://github.com/m5agent/m5stack-esp-emulator/issues)
- 源码版本：`m5agent/m5stack-esp-emulator @ 7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde`；本记录为已执行候选，最终发布另列。
- 环境：独立原生 Device Service 会话、QEMU Xtensa/C6、固定原版或独立重建固件；`virtual-device validation`。

## 结论

沿原固件真实控制器、DMA/FIFO 和板级接线修复模型缺口，同时以公开源码
重建对照区分 StackChan 固件 SDK 竞态。原 BIN 未改，watchdog 未禁用；没有
伪造配对码、HTTP 成功或应用帧。完整最终矩阵及部署尚未写入本记录。

| 问题 | 结果 | 范围 |
| --- | --- | --- |
| #205 | PASS 限定原版方向；交付待验 | 五份原版 StickS3 的 MADCTL/显示方向逐像素对照；raw 和触摸契约独立。 |
| #188 | PARTIAL | 服务镜像身份与首触摸边界已修，最新 Tab5 仍受闭源 P4 CSR/DSI 控制器阻塞。 |
| #221 | PASS 原驱动子路径 | Matrix WPA2/DHCP/DNS/TCP、RMT 灯阵和按键通过；真实 HTTP 404 与不完整帧保留。 |
| #222 | PASS 原驱动子路径 | 错误板型 ID、硬件片选、SPI SD/DMA、重复缓存失效分别修正；原 HamRadio 可读配置进入仪表，原 UIFlow 可见配置页。 |
| #216 | PARTIAL | 原 Bruce 进入菜单；SX1262、PHY、BLE AES 子路径通过，Meshtastic 后续 WDT 与其它原应用仍需复验。 |
| #223 | PASS 因果对照；原 BIN FAIL | 公开应用未修重建同样崩溃，仅加入官方 I2C 修复的两款重建版各 360 秒通过。 |
| Device Service input | PASS | QMP 失效后真实同 guest 触摸可重连并进入应用。 |

## 关键证据

- 构建/源码、firmware/runtime 哈希、串口、协议、输入和帧摘要在 [run.json](run.json)。
- [report.md](report.md) 说明根因、原路径复现、失败控制和责任边界。
- `evidence/` 是经复核的有界 summary，保留原始 ZIP 哈希；不冒充原始日志。
- 本记录不附固件、ROM、mutable Flash 或第三方配置文件；可重建入口使用固定源码链接。

## 未覆盖项

最终组合高负载矩阵与交付记录待追加。物理硬件、RF、功耗、声学、机械、
信号完整性和物理熵未验证。Tab5 闭源后端与 C6 未通过的整应用继续开放。
原版 StackChan BIN 仍失败；新构建通过不等于原发布包被修复。未提交 Burner。

## 后续执行

[2026-11-13：main、两轮高负载回归与常驻服务验收](followups/2026-11-13-main-and-resident/README.md) 已追加固定交付版本、九条联网/编程、五份原版方向、MP3/2048 dry-run 及同运行时 AWS 显示证据。旧候选记录保留；整体应用兼容性仍为 PARTIAL。

I2C 因果对照的准确范围：只有 UserDemo 具有未修源码重建负控，GPT 的负控为原发布 BIN；两份补丁重建版的通过不能转移给原发布二进制。
