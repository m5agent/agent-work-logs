# M5Stack ESP Emulator SVC-03 device-spec boundary

- 日期：`2026-10-30`
- 结果：`PASS`（platform-contract validation）
- 工作类型：`code_change`
- 问题来源：`SVC-03` Device Service 编排拆分
- 源码版本：`m5stack-esp-emulator @ 823dd8903174991a0e8220622d459c3ebd508c96`
- 交付：PR #53 已合并为 `0e788b7ac8795ab4d037c55e1abd379afd0f126c`
- 环境：macOS arm64；Python 3.12

## 结论

Device Service 的 `DeviceSpec`、catalog/matrix/profile 解析、QEMU backend
路径、Core2 radio 后端选择、network/runtime profile constants 和
`load_device_specs()` 已移到 `platform/tools/device_service_specs.py`。
`device_service.py` 继续 same-object re-export，调用方、HTTP payload、
session 记录、evidence 字段和 QEMU 执行路径不变。

这是代码边界与平台契约验证，不是运行时仿真能力提升。

## 关键证据

- module：`platform/tools/device_service_specs.py`
- 定向 device-spec tests：`5/5 PASS`
- 原 Device Service tests：`125/125 PASS`
- QEMU profile contracts：`20/20 PASS`
- 完整平台回归：`1,604` 项，`1,603 PASS + 1 skip`
- docs contracts：`50/50 PASS`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`
- compileall、Ruff `E9/F` 和 `git diff --check`：`PASS`

## 文件

- `report.md`：边界、验证和回滚
- `run.json`：机器可读记录
- `evidence/verification-summary.json`：精确检查摘要
- `patches/`：不适用；改动已作为源码提交交付
- `code/`：不适用；测试位于源码仓库

## 未覆盖项

QEMU、firmware、session、evidence 和物理硬件行为没有变化，也没有为本重构
重跑单独的功能 lane。物理硬件、RF 和电气验证均为 `NOT RUN/不变`。
