# ESP Emulator worker control/runtime plane split

- 日期：`2026-10-25`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：`NET-04` 跨主机 QEMU executor
- 源码版本：`m5agent/m5stack-esp-emulator @ 261d31016aedd85974ad15a46e3b413c2a8f2bcf`
- 基线版本：`1d3694eea6a4cf39ccfa56e53b8bbb9bfe28b575`
- 环境：macOS 平台测试主机；privileged Linux container network namespaces

## 结论

`WorkerAgent` 已把中央控制面与执行面拆开：

- `--service-url` 负责 registration、claim、worker/job heartbeat 和 result；
- `--runtime-service-url` 负责 session create/wait、evidence 下载和 stop；
- 未提供 runtime URL 时仍复用原服务，保持同主机兼容；
- control/runtime URL 必须使用相同 HTTP/HTTPS scheme；
- credential generation 未提供独立 runtime token 时同步更新两个执行面。

单测验证 session/evidence 请求不会发到控制 API。Linux network namespace
fixture 的 no-QEMU 兼容模式在拆分后再次 `13/13 PASS`。worker-local 真实
QEMU fixture 已实现，但为避免干扰正在运行的 Core2 soak，本轮未执行，
因此整体只记 `PARTIAL`。

## 关键证据

- 完整平台套件：`350/350 PASS`。
- cross-network-namespace control plane：`13/13 PASS`。
- runtime plane 单测：控制 API 无 session 请求，session/evidence/stop 全部
  发往 runtime API。
- 包校验/快照：runtime coverage、peripheral catalog、QEMU profiles、
  project snapshot 全部 `PASS`。
- Ruff fatal/未使用 import、`compileall` 和 `git diff --check`：`PASS`。
- GitHub Actions：见 `run.json`。

## 文件

- `report.md`：实现、执行和边界。
- `run.json`：机器可读记录。
- `evidence/verification-summary.json`：脱敏摘要。
- `patches/`、`code/`：不适用；实现位于公开源码仓库。

## 未覆盖项

- 真实 worker namespace Device Service 启动 QEMU、应用首帧/串口、
  evidence ZIP 和 QEMU reap：`NOT RUN`。
- companion/evidence-stream continuity 和跨主机 process reattach。
- 物理独立主机、生产多机调度和物理硬件。
