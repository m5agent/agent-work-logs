# ESP Emulator bounded DNS CNAME and code/document reconciliation

- 日期：`2026-10-25`
- 结果：`PASS`（controlled DNS resolver + code/docs/CI）；guest CNAME
  lifecycle、public DNS、RF 与物理硬件为 `NOT RUN`
- 工作类型：`code_change`
- 源码版本：
  `https://github.com/m5agent/m5stack-esp-emulator/commit/8710e41bf00d592ad0a5a7b9e5a3d5f32a333f9d`
- Base commit：`2a2c7920039d38dec92c93c14a69caec6fbfd4fa`
- 环境：macOS arm64；Python 3.13；Node 20；QEMU/Guest `NOT RUN`

## 结论

Controlled DNS 现在支持受 policy 约束的有界 CNAME chain，并同时覆盖 exact
与 domain-suffix terminal。resolver 会返回完整的 CNAME chain 和匹配的 terminal
address，拒绝 cycle、uncontrolled terminal、越权 alias、owner/address 冲突及
超过 8 跳的 chain；Device Service 与 OpenAPI `1.30.0` 已接线。

文档同时完成一次结构收敛：会随提交变化的测试、设备和 profile 数量只保留在
自动项目快照中，当前状态页不再复制这些动态数字。新增 `NET-07`，明确剩余工作
是“同一 guest 固件跟随 CNAME terminal 并完成 TCP/HTTP”，不能把本次
resolver-only 证据写成完整固件生命周期 PASS。

## 关键证据

- resolver：exact terminal、domain-suffix terminal、CNAME query、NXDOMAIN、
  cycle、uncontrolled/越权 terminal、exact/domain owner 冲突与 8/9 跳边界；
- Device Service：valid CNAME 配置被接受，非 controlled/allowlist、越权
  alias、uncontrolled terminal 返回结构化 `invalid_network`；
- contracts：`425/425` 平台测试、Node `2/2`、OpenAPI YAML、compileall、
  runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  selected Ruff 与 `git diff --check` PASS；
- CI：GitHub Actions `40152639444` 的 `platform-contracts` 与
  `network-namespace-policy` 两个 job 均成功。

## 文件

- `report.md`：背景、改动、执行证据、边界与回滚
- `run.json`：机器可读结果
- `evidence/verification.summary.json`：CNAME checks、policy negatives 和
  CI 结果摘要

## 未覆盖项

- 同一 guest 固件 CNAME→terminal→TCP/HTTP 生命周期（`NET-07`）；
- Linux namespace 下的 CNAME guest 生命周期；
- public DNS、DNSSEC、rebinding 防护；
- RF/PHY、物理硬件、功耗与电气测量。
