# ESP Emulator worker-local QEMU across network namespaces

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device validation）
- 工作类型：`code_change`
- 问题来源：`NET-04` worker-local QEMU executor
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`f0fe0553546032fdf6c5219f8b7278af823d24b2`
- 实现与证据版本：`902034997afbf1f47949c08f129da101bb90582a`
- CI run-shape 修复：`461d489f2c36825d4b4ce27421322b56231c34e1`
- 文档与当前状态版本：`ec63754f183c7b059fab2d4aa520ab43a307d426`
- 环境：privileged Linux arm64 container；两个 veth 连接的 private
  network namespace；真实 Linux arm64 QEMU

## 结论

中央 control service 与 worker-local runtime Device Service 已在两个独立
network namespace 中完成真实 job：

- central service 负责 registration、claim、worker/job heartbeat 和
  terminal result；
- worker namespace 内的 runtime service 负责 artifact/firmware、session、
  serial/frame/QOM evidence 和 stop；
- 真实 StickS3 QEMU 启动并进入 session running；
- source firmware、normalized firmware 和 QEMU SHA256 均绑定；
- evidence ZIP 包含 manifest、serial 和 QOM snapshot；
- terminal result 为 `completed/PASS`；
- token 未进入保留日志；
- QEMU 与两个 namespace 均回收。

18/18 checks PASS。结果只证明同一主机上的两个 network namespace；物理独立
主机、自动 worker 主机发现、跨主机 QEMU reattach、companion/evidence-stream
continuity 和生产多机调度仍为 `NOT RUN`。

## 关键证据

- worker-local QEMU：`18/18 PASS`；
- QEMU session：真实启动，`completed/PASS`；
- source firmware SHA256：
  `c08196024019273ccadee9b4b3da303567f7ab206fa14edd1af283f04f6e98d8`；
- normalized firmware SHA256：
  `a5d027f6d2953edb9ece45cddea1490112d8e421ba563edc6e7c71cf7ac4f6ec`；
- QEMU SHA256：
  `f024f034d20bd5b8e2c224ce69deed70984b0514f8a310d221b388b74c179ecb`；
- evidence file SHA256：
  `8ec57f252cbf7676c561c354f8e6a5aa27b17affa37e2b1cbbf0d14d219682be`；
- platform tests：`368/368 PASS`；
- docs contracts：`19/19 PASS`；
- Node tests：`2/2 PASS`；
- GitHub Actions run
  [`40129700779`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40129700779)：
  `network-namespace-policy` 与 `platform-contracts` 均 `PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall、selected Ruff fatal rules 和 `git diff --check`：`PASS`；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：背景、修复、执行、证据和边界；
- `run.json`：机器可读记录；
- `evidence/verification-summary.json`：脱敏验证摘要；
- [`followups/2026-10-25-cross-container-qemu/`](followups/2026-10-25-cross-container-qemu/)：
  两个独立 Docker 容器中的 worker-local QEMU、三哈希 evidence 和 cleanup；
- `patches/`、`code/`：不适用；实现位于公开源码仓库。

## 未覆盖项

- 物理独立主机、真实跨主机网络延迟和丢包；
- automatic worker-host discovery；
- cross-host QEMU process reattach；
- companion HTTP/BLE helper 与 evidence-stream continuity；
- 生产 secret manager、多主机容量调度和 disposable VM；
- 物理硬件、RF、功耗或电气验证。
