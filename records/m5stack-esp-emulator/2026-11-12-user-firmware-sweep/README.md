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
- 已提交 3 个 issue：[#216](https://github.com/m5agent/m5stack-esp-emulator/issues/216)（Nesso N1 C6 启动崩溃循环）、[#217](https://github.com/m5agent/m5stack-esp-emulator/issues/217)（PaperColor 触发 QEMU `atomic_mmu_lookup` 断言、进程 SIGABRT）、[#218](https://github.com/m5agent/m5stack-esp-emulator/issues/218)（PM1 主动关机被记为启动失败）。
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
- AtomS3 的 ATOMS3 UserDemo/Snake Game 静默无输出、Tab5 多固件无首帧等个例尚未定位到模型或固件侧，未开 issue。
