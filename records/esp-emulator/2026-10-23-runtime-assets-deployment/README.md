# ESP Emulator 运行时资产部署诊断

- 日期：`2026-10-23`
- 结果：`PASS`（部署诊断与虚拟设备会话；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 问题来源：用户反馈其他部署者找不到 `.work/`，无法启动模拟器
- 源码版本：`m5stack-esp-emulator @ 7b973e481d122be00cdf4cecab48b2a70bf63e8d`
- 基线：`bcbdc030fdd1ee8cdffbcafe4cd15dcce72c2d26`
- 环境：Apple Silicon macOS 26.5.1、Python 3.13.15；另用不含 `.work/` 的 Git
  archive 模拟全新 clone

## 结论

`.work/` 缺失不是 Git 仓库损坏。该目录被 `.gitignore` 完整排除，当前参考
工作站的运行时缓存约 48 GiB，包含平台相关二进制、构建目录、ROM/eFuse 和
第三方固件，不能作为普通源码发布。

全新 clone 可以正常启动设备目录、只读设备清单和 OpenAPI；只有创建 QEMU
会话时才需要 `.work/` 和参考固件。本次改动把这一部署边界写入独立文档，并
让设备 API 与 `503 backend_not_ready` 响应直接列出缺失的相对路径。

## 关键证据

- 干净导出：无 `.work/` 时目录页 HTTP `200`，14 台设备仍可枚举。
- 诊断：`sticks3.backend_ready=false`，缺失项为 QEMU 可执行文件、
  `pc-bios` 目录和 `esp-emu`。
- 错误响应：创建会话返回 `503 backend_not_ready`、`missing` 数组及
  `docs/deployment.md` 指引。
- 已 provision 环境：`sticks3` lease 返回 HTTP `202`，状态由 `flashing`
  进入 `running`，PNG 帧读取成功，随后以 `purge=0` 停止并保留历史。
- 回归：158 个 Python unittest 通过；runtime coverage 与 peripheral
  catalog 检查通过。

## 文件

- `report.md`：根因、改动、执行与边界
- `run.json`：结构化记录
- `evidence/clean-clone-deployment.txt`：无 `.work/` 的部署复现
- `evidence/provisioned-session.txt`：现有运行时的虚拟设备会话
- `evidence/runtime-assets-summary.md`：运行资产范围与体积
- `evidence/unittest.txt`：单元测试输出
- `evidence/runtime-coverage.txt`、`evidence/peripheral-catalog.txt`：契约检查
- `evidence/openapi-check.txt`、`evidence/git-check.txt`：格式检查

完整代码差异：
[m5stack-esp-emulator@7b973e4](https://github.com/m5agent/m5stack-esp-emulator/commit/7b973e481d122be00cdf4cecab48b2a70bf63e8d)

部署说明：
[docs/deployment.md](https://github.com/m5agent/m5stack-esp-emulator/blob/7b973e481d122be00cdf4cecab48b2a70bf63e8d/docs/deployment.md)

## 未覆盖项

- 没有在 Linux/x86_64 或其他目标架构重新构建 `.work/`。
- 没有验证自动化 runtime image 打包；当前仓库仍没有一键 bootstrap。
- 没有执行物理硬件测量；QEMU 结果明确标记为 virtual-device validation。
