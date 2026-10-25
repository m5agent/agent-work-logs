# ESP Emulator 有界 CIDR、domain-set 与代码/文档重整

- 日期：`2026-10-25`
- 结果：`PASS`（bounded network policy + docs/contracts；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 问题来源：用户要求完整整理 ESP Emulator 的代码、文档、当前工作和待办
- 源码仓库：<https://github.com/m5agent/m5stack-esp-emulator>
- 基线版本：`3bd0f6655fc6495bd1653eac2f39c1139f1fed64`
- 能力提交：`8c125fb580482cb25f38e3a45630654eb94e6dc9`
- 证据提交：`7da51aa`
- 环境：macOS Apple Silicon；Python 3；Linux Docker；GitHub Actions Ubuntu

## 结论

网络策略从 exact IP/port 扩展到有界 IPv4/IPv6 CIDR，并加入 controlled
DNS domain suffix。域名只在 DNS label boundary 匹配，exact record 优先、
最长 suffix 优先；每个 suffix 必须显式绑定 resolver answer，且 answer
必须落在允许的 endpoint 地址或 CIDR 内。域名授权不再可能绕开 IP/端口
策略。

同时把 API、网络方案、`AGENTS.md`、当前状态、Backlog、工作流、代码地图、
新鲜度台账和自动快照中的旧“CIDR/domain 不支持”口径统一到同一实现。

## 关键证据

- Linux namespace CIDR fixture：`22/22 PASS`；
- 平台测试：`411/411 PASS`；
- 文档契约：`22/22 PASS`；
- Node：`2/2 PASS`；
- OpenAPI YAML、compileall、runtime coverage、peripheral catalog、QEMU
  profiles、project snapshot、selected Ruff 和 `git diff --check`：`PASS`；
- GitHub Actions `40145733947`：`platform-contracts` 与
  `network-namespace-policy` 均 `PASS`；
- GitHub Actions `40145813958`：证据提交 `7da51aa` 的完整 CI 也 `PASS`。

## 文件

- `report.md`：策略语义、文档纠偏、验证和边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：脱敏验证摘要。

## 未覆盖项

- 没有证明任意公网域名到外部 IP 的动态 allowlist；
- 没有新增 guest 固件使用 domain suffix 的端到端生命周期；
- 没有覆盖 WPA3、物理 RF、跨主机 worker/QEMU executor 或真机；
- Linux fixture 验证的是网络策略和清理，不是恶意固件 VM 隔离。
