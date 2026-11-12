# M5Stack 模拟器 26 设备 × 5 固件公开固件扫描

- 日期：`2026-11-12`
- 结果：`PARTIAL`
- 工作类型：`report`
- 问题来源：用户请求（每台模拟器设备找 5 个固件烧录运行，模拟器缺陷提 issue）
- 源码版本：`m5stack-esp-emulator @ 1506de25`
- 环境：macOS arm64；agent 自有 Device Service（`/api/v1`，非用户 8787/8830 实例）；QEMU `9.2.2`（xtensa 运行时 `2026-11-11` 同步构建）+ C6 riscv32 运行时

## 结论

26 台有专属公开 M5Burner 机型的模拟器设备各选 5 个固件（共 130 个计划，127 个完成会话）通过 Device Service 烧录运行。

- **59 个样本出现可用 UI 帧且无致命错误**；13 个样本通过矩阵严格判定（UI + 输入响应）。
- **30 个样本在启动期或首帧后崩溃**（guest panic / watchdog / 重启循环），集中在 C6（Nesso N1、NanoC6）、经典 LX6 厂测固件和 Tab5。
- 已提交 9 个 issue：[#216](https://github.com/m5agent/m5stack-esp-emulator/issues/216)（Nesso N1 C6 启动崩溃循环）、[#217](https://github.com/m5agent/m5stack-esp-emulator/issues/217)（PaperColor 触发 QEMU `atomic_mmu_lookup` 断言、进程 SIGABRT）、[#218](https://github.com/m5agent/m5stack-esp-emulator/issues/218)（PM1 主动关机被记为启动失败）、[#219](https://github.com/m5agent/m5stack-esp-emulator/issues/219)（AtomS3 两款固件启动卡死）、[#220](https://github.com/m5agent/m5stack-esp-emulator/issues/220)（PaperColor TinyUSB 未建模）、[#221](https://github.com/m5agent/m5stack-esp-emulator/issues/221)（Atom-Lite/Matrix 厂测 watchdog）、[#222](https://github.com/m5agent/m5stack-esp-emulator/issues/222)（Core2 显示写入未到达面板）、[#223](https://github.com/m5agent/m5stack-esp-emulator/issues/223)（StackChan 约 39 s 崩溃）、[#224](https://github.com/m5agent/m5stack-esp-emulator/issues/224)（efuse MAC 全 0）。
- 10 台设备因没有专属公开固件未进入矩阵（CardputerZero、M5Stick、StickT2 不可创建；AtomS3U、Atom Echo、Atom VoiceS3R、AtomS3R-CAM/M12、AtomU、StickC Plus SE 无独立 M5Burner 机型）。

本记录只覆盖 **virtual-device 启动/显示层**；不涉及真机、射频、功耗、电气或光学结论。

## 关键证据

- 运行：Device Service `18787`，提交 `1506de25`；`platform/tools/user_firmware_matrix.py` + 扩展机型映射，`--per-device 5 --observe-seconds 40 --jobs 2` × 3 分片。
- 产物：127 个 `results.json` 样本、串口日志与 before/after 帧；汇总见 `evidence/summary.txt`，逐样本判读见 `evidence/triage-summary.txt`，设备级统计见 `evidence/device-table.md`。
- 缺陷证据：`evidence/papercolor-qemu-abort.stderr`；3 个 issue 草稿见 `evidence/issues/`。

## 文件

- `report.md`：完整报告（方法、结果、分类、未定位项）
- `run.json`：结构化记录
- `evidence/`：汇总、逐样本判读、设备表、QEMU stderr、issue 草稿

## 未覆盖项

- 10 台无专属公开固件的设备没有样本；其模拟器可用性不在本轮结论内。
- 未做真机对照；未见网络协议、音频、射频、功耗与电气行为验证。
- 输入响应只按矩阵默认探针判定；无响应不等于固件不可用。
- Tab5 多固件无首帧（既有 #188）、stackchan 首帧后 Guru Meditation、Core2 空白帧等仍未闭环。


## 2026-11-13 修复进展

- **#224 efuse MAC 已修复并推送**：`m5stack-esp-emulator@c5cda7a0`，所有 ESP32-S3 会话 eFuse 镜像写入由 session id 派生的本地管理 MAC（02:xx）。四个 S3 会话冒烟通过，既有通过样本画面不变。
- **#222 Core2 面板**：定位到失败固件走 SPI DMA 路径，45 s 内面板模型收到 0 条命令；对照固件走 PIO，2030 条 trace。当前运行时二进制不含 `0085` 的 DMA 描述符处理，需重建运行时后再验证，未修复。
- **#222 Core2 面板已修复并推送**：`m5stack-esp-emulator@778717a6`（patch 0179）。根因是 SPI OUT_LINK 的 latch 被只带 start 位的第二次写覆盖；Core2_For_AWS 修复后服务帧 76294 非黑像素（修复前 0），对照固件与 StickS3 不变。
- **#220 PaperColor USB 已修复并推送**：`m5stack-esp-emulator@6b52ee33`（patch 0180）。PaperColor 现在实例化 ESP32-S3 USB OTG 控制器，厂测固件 `TinyUSB Driver installed on port 0` 并打印描述符；PaperColor Frame 帧不变。
- 用重建后的完整运行时复测：AtomS3 两款固件仍停在 ROM entry（#219 未修复）；StackChan UserDemo 仍出现一次 Guru Meditation（#223 未修复）。
- 其余 #216/#217/#219/#221/#223 仍在开放状态。
