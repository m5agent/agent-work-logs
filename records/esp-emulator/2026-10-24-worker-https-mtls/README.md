# ESP Emulator Worker HTTPS/mTLS Transport

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码版本：`m5agent/m5stack-esp-emulator @ ea6e4cb37460f6ce20fc2f18f03224c8724ae0cd`
- 基线版本：`e9520bbca56da753cd4cd75cf30c8c5594866386`
- 环境：macOS Apple Silicon；Python 3；同一主机 loopback；真实 Device Service 与 worker 子进程；临时测试 PKI

## 结论

Device Service 和 `worker_agent.py` 已支持可验证的 HTTPS/mTLS 传输。服务端
使用 TLS 1.2+ 证书，可通过 client CA 强制客户端证书；worker 客户端支持
自定义 CA 和客户端证书，不提供 hostname 校验绕过。

真实 loopback 进程门禁协商 TLS 1.3，验证服务端证书、无可信客户端证书拒绝、
有证书通过、Bearer + worker HMAC 保持、unsigned claim `401`、明文 HTTP
回退失败，以及 worker agent 的签名注册/heartbeat/claim/stop 生命周期。

## 关键证据

- 平台测试：`305/305 PASS`；
- Node：`2/2 PASS`；
- GitHub Actions CI run `40070863490`：两个 job 均 `PASS`；
- TLS：最小 TLS 1.2，实测 TLS 1.3；
- transport：真实 HTTPS、mTLS、证书拒绝/通过；
- authentication：Bearer + worker HMAC 未降级，unsigned claim `401`；
- worker：带客户端证书的 agent 退出码 `0`；
- evidence SHA256：
  `9342e8f549129ab215a1bd08f7efa6d07ca03d97d0084ac8badb8c2e8dbbb114`。

## 文件

- `report.md`：实现、验证、边界和回滚
- `run.json`：机器可读记录
- `evidence/verification.transport.json`：传输安全证据摘要

## 未覆盖项

- 跨主机网络拓扑、延迟和丢包；
- 证书或 worker 凭据热轮换；
- 生产 CA/证书生命周期；
- 真实 QEMU job over mTLS；
- 多主机调度和 worker continuity；
- 真机、RF 或硬件验证。
