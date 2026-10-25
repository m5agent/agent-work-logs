# ESP Emulator Cross-Subnet NAT Worker Discovery Seed

- 日期：`2026-10-25`
- 结果：`PASS`（virtual control-plane validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`feb42b6e0ddcd35ab4dcd6dfc297111861cfcd14`
- 结果版本：`667c3564208fcb69df7afea68091d6d3e34d3eb4`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40159761453>
- 环境：Linux privileged Docker；两个 routed/masqueraded network namespace；GitHub Actions Ubuntu

## 结论

同一 multicast domain 的现有 discovery 保持不变。无法接收 multicast 的
worker 现在可通过稳定的 unicast discovery seed 获取同一 active-token
HMAC-signed beacon，验证后取得真正的 control URL。

三个独立运行均通过：

- worker 与 control 位于两个独立 subnet；
- 中间 router 开启 IPv4 forwarding 并执行 masquerade；
- control-plane multicast announcer 存在，但 multicast 不跨 router；
- `WorkerAgent --discover-control-seed-url` 成功发现、注册、heartbeat 和停止；
- 错误 token、rotation 前旧 token 均被拒绝且不注册；
- token rotation 后新 token 可经同一 seed 重新发现和注册；
- control-side access log 观察到 router 地址，证明 NAT 路径；
- token 不进入 beacon 或日志；
- namespace、nftables 和全部 fixture process 均清理。

## 关键证据

- 独立运行：`3/3 PASS`；
- 每轮检查：`23/23 PASS`；
- multicast 跨 router：被拒绝/超时，未注册；
- 工具哈希在首次 lease 前记录，运行前后无漂移；
- 平台测试：`442/442 PASS`；
- 文档契约：`29/29 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- GitHub Actions `platform-contracts` 与
  `network-namespace-policy`：`PASS`；
- CI 实际执行 unicast seed 跨子网/NAT fixture 并成功上传脱敏 evidence。

源码 evidence：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/667c3564208fcb69df7afea68091d6d3e34d3eb4/tests/network/worker_discovery_seed/evidence-2026-10-25-seed-nat-3x.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/667c3564208fcb69df7afea68091d6d3e34d3eb4/platform/tools/worker_discovery_seed.py>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/667c3564208fcb69df7afea68091d6d3e34d3eb4/platform/tools/worker_discovery.py>

## 文件

- `report.md`：设计、拓扑、执行、验证边界和回滚；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏聚合摘要；
- `evidence/seed-nat-3x.json`：三次独立运行汇总。

## 未覆盖项

- 物理跨主机 QEMU executor/reattach；
- 没有 reachable seed 时的任意 NAT traversal；
- QEMU execution through the discovered control plane；
- 生产多机 scheduler、capacity、secret manager 和 audit；
- physical hardware validation。

HMAC 证明 discovery beacon authenticity，不提供 confidentiality。生产 seed
应使用 HTTPS 或受信任的私有传输。
