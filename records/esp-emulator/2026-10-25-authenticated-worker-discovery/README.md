# ESP Emulator Authenticated Worker Discovery

- 日期：`2026-10-25`
- 结果：`PASS`（virtual control-plane scope）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`351eb16d49f1ffbef562810668f3248e1cfc7f52`
- 结果版本：`658b2d494bbd40fcb798ed4349a6304d46c0d917`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40140611924>
- 环境：macOS Apple Silicon；真实 Device Service/WorkerAgent；IPv4 multicast；GitHub Actions Ubuntu

## 结论

Device Service 现在可广播 active-token HMAC 签名的 IPv4 multicast beacon，
`WorkerAgent --discover-control` 可在不硬编码 control URL 的情况下发现
control plane、验证 beacons、注册、heartbeat 并停止。

安全行为：

- beacon 不含 token；
- signature 绑定 service URL、group、port、issue/expiry time 和 nonce；
- worker 拒绝错误 token、错误 group、过期 packet 和异常 URL；
- SIGHUP token rotation 后 announcer 使用 active token，新 token worker
  可重新发现；
- rotation 前旧 token 和随机错误 token 均不能注册；
- TLS/mTLS 仍负责 transport identity，multicast HMAC 只负责发现真实性。

## 关键证据

- 平台测试：`391/391 PASS`；
- 文档契约：`20/20 PASS`；
- `test_worker_discovery.py`：`4/4 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`；
- GitHub Actions `platform-contracts` 与
  `network-namespace-policy`：`PASS`；
- CI network job 实际执行 authenticated discovery 和 token rotation；
- 真实 worker 无硬编码 URL 注册后状态 `stopped`；
- wrong token / old token 均未注册；
- 未创建 Device Service session，未启动 QEMU；
- token 未进入 beacon、service log 或 worker log。

源码 evidence：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/658b2d494bbd40fcb798ed4349a6304d46c0d917/tests/network/worker_discovery/evidence-2026-10-25-discovery-rotation-pass.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/658b2d494bbd40fcb798ed4349a6304d46c0d917/platform/tools/worker_discovery.py>

## 文件

- `report.md`：设计、安全、执行和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏聚合证据。

## Follow-up

- [Cross-subnet/NAT unicast discovery seed](followups/2026-10-25-cross-subnet-nat-seed/)：
  两个 routed/masqueraded subnet、multicast 不跨 router、seed bootstrap、
  错误/旧 token、rotation 和 cleanup `3/3 PASS`。

## 未覆盖项

- NAT、路由不转发 multicast 的跨子网发现；
- 物理跨主机 QEMU executor/reattach；
- companion HTTP/BLE/evidence continuity；
- 生产多机 scheduler 和 secret manager；
- 物理硬件验证。
