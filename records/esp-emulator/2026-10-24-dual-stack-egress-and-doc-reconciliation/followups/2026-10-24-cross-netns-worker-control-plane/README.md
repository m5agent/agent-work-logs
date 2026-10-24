# ESP Emulator cross-network-namespace worker control plane

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：`NET-04` 跨主机 worker 产品化
- 源码版本：`m5agent/m5stack-esp-emulator @ ad6e96e69757eafd13993f0d45484c42d4476182`
- 环境：独立 privileged Linux container；GitHub Actions `ubuntu-latest`

## 结论

真实 Device Service 与真实 `WorkerAgent` 已分处两个由 veth 连接的 Linux
network namespace，跨边界完成：

- authorization header + worker HMAC authenticated registration；
- capability-matching durable job submit/claim；
- worker heartbeat 和 job lease heartbeat；
- terminal completed result；
- worker stop；
- API credential 不进入 server/worker 日志；
- veth route 和两个 namespace 清理。

该 fixture 明确不启动 QEMU、不创建 device session。它证明 worker control
plane 可以跨网络边界工作，不代表 cross-host QEMU executor、companion /
evidence continuity 或 process re-attach 已完成。

## 关键证据

- 本地 privileged Linux container：PASS。
- 同一 commit GitHub Actions `network-namespace-policy`：PASS。
- Platform contracts：`340/340 PASS`。

## 文件

- `report.md`：拓扑、执行、边界和回滚。
- `run.json`：机器可读记录。
- `evidence/summary.json`：脱敏结果。
- `patches/`、`code/`：不适用；fixture 位于公开源码仓库。

## 未覆盖项

- cross-host QEMU executor；
- cross-host process re-attach；
- companion HTTP/BLE 和 evidence-stream continuity；
- production multi-host scheduling；
- physical hardware。
