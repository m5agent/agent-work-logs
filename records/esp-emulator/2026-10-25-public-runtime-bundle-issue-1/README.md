# 公网运行时缺口的验证、发布与复现

- 日期：`2026-10-25`
- 结果：`PARTIAL`（release runtime PASS；clean-room source rebuild 仍开放）
- 工作类型：`issue`
- Issue：<https://github.com/m5agent/m5stack-esp-emulator/issues/1>
- 源码版本：`10df26ece0b605a3a8bb36a3661b53494fdae9a0`
- 文档版本：`2a2c792`
- 环境：macOS arm64；Python 3.13；Device Service `/api/v1`

## 结论

Issue #1 的核心问题成立：公开 clone 不能按旧 README 从源码重建完整 QEMU
运行时，且 `hw/gpio/esp32_gpio.c` 等共享文件存在不可线性叠加的历史快照。

已发布一个可执行的 macOS arm64 runtime bundle，并在全新 public clone 中
验证：

- `sticks3`、`nesso-n1` 均 `backend_ready=true`、`creatable=true`；
- 公开 StickS3 和 Nesso N1 固件均通过 Device Service 启动到非空
  `135x240` frame；
- key/touch 输入均被 session 接受；
- bundle 内 QEMU、ROM、`esp-emu` 和 Python 依赖无需 Homebrew。

Release：
<https://github.com/m5agent/m5stack-esp-emulator/releases/tag/runtime-macos-arm64-2026.10.25>

Asset SHA256：
`735464198c5f7f3ffa930307c0e4cedb973ac48934b73d0092a3a4659831c7a9`

## 关键验证

- `da100c9092...` 的 GitHub API 返回 `422`，不是公开可达的上游 pin；
- 公开 tag + zqqf16 v0.1.0 五补丁 + stopwatch patch 后，multiboard 和
  peripherals patch 都在共享文件前像上失败；
- C6 `febae182...` 本身可公开访问，issue 中对该 commit 的笼统否定未复现；
- 一次 StickS3 session 在非空 frame 后出现 QMP startup timeout，立即重试
  PASS；该服务启动抖动单独保留，不归因于 bundle 或固件。

## 文件

- `report.md`：复现、发布、clean-clone 验证和边界
- `run.json`：机器可读结果
- `evidence/verification.summary.json`：脱敏聚合证据

## 未覆盖项

- clean-room source rebuild 仍未提供一键脚本；
- runtime bundle 只覆盖 macOS arm64 + Python 3.13；
- 未覆盖 Linux/Windows；
- 未做物理硬件验证。
