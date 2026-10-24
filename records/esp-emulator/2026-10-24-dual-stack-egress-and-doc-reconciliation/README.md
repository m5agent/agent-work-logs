# ESP Emulator exact IPv6 egress 与代码/文档重整

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：用户维护请求（无公开 Issue）
- 源码版本：`m5agent/m5stack-esp-emulator @ 9981460b46dad235eed5d8001d0df432faabd79e`
- 环境：macOS 平台测试主机；独立特权 Linux container；GitHub Actions `ubuntu-latest`

## 结论

`NET-05` 已完成 exact IPv4/IPv6 destination egress。worker namespace 通过
双栈 default route、inner veth、nftables、IPv6 neighbor control 和
masquerade 到达独立 upstream；允许的 IPv4/IPv6 地址和端口返回 HTTP 200，
其余地址/端口被阻断，NAT 源地址与全部 namespace/table 清理均有证据。
本地重复运行 `2/2 PASS`，同一 source commit 的 GitHub Actions 再次 PASS。

代码、API/OpenAPI、项目状态、Backlog、自动快照、工作流台账和专题文档已同步；
`NET-05` 从 Backlog 关闭，`RUNTIME-03` 的最新 AXP/BM8563 trace 边界已并入
当前文档，Core2 artifact-bound `7200s` soak 明确保持“在途，不是 PASS”。

## 关键证据

- 平台契约与文档测试：`336/336 PASS`。
- Node 浏览器上传测试：`2/2 PASS`。
- `runtime_coverage`、`peripheral_catalog`、`qemu_profiles`、
  `project_snapshot`：全部 `PASS`。
- 本地 Linux 双栈 egress：连续 `2/2 PASS`。
- GitHub Actions：run `40098666896` 和最终 source run `40098772592` 均成功。
- 上游 peer 观察到 worker 侧 IPv4/IPv6 源地址，证明两条路径都经过
  masquerade，而不是 loopback shortcut。

## 文件

- `report.md`：改动、执行、验证层级和边界。
- `run.json`：机器可读记录。
- `evidence/summary.json`：从已提交 evidence 和 CI artifact 派生的脱敏摘要。
- `patches/`：不适用；完整改动已提交到源码仓库。
- `code/`：不适用；可重建测试位于源码仓库 `tests/network/egress_allowlist/`。

Follow-up：

- [`2026-10-24-dns-aaaa-and-capability-intake`](followups/2026-10-24-dns-aaaa-and-capability-intake/)：
  IPv6 preflight、A/AAAA resolver、WebBurner capability intake 和
  sdkconfig detected capability。
- [`2026-10-24-cross-netns-worker-control-plane`](followups/2026-10-24-cross-netns-worker-control-plane/)：
  真实 server/worker namespace 间 authenticated submit/claim/heartbeat/result。

## 未覆盖项

- 未执行固件 guest 网络行为；本记录只验证 Linux 虚拟网络策略。
- 未验证物理硬件、RF、功耗或电气行为。
- 未实现或验证 CIDR、domain-set、IPv6 DNS/AAAA policy。
- Core2 artifact-bound 两小时 soak 当时仍在运行，不包含在本记录 PASS 内。
