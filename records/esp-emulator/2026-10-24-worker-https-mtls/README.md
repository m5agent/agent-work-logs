# ESP Emulator Worker HTTPS/mTLS Transport

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码版本：`m5agent/m5stack-esp-emulator @ ea6e4cb37460f6ce20fc2f18f03224c8724ae0cd`
- QEMU job follow-up：`m5agent/m5stack-esp-emulator @ 865e4f810263f3f388beeee3aa577de27f99d0b1`
- unified job follow-up：`m5agent/m5stack-esp-emulator @ 48ff20c416221e20f76873c07d7473329318eb5c`
- 基线版本：`e9520bbca56da753cd4cd75cf30c8c5594866386`
- 环境：macOS Apple Silicon；Python 3；同一主机 loopback；真实 Device Service 与 worker 子进程；临时测试 PKI

## 结论

Device Service 和 `worker_agent.py` 已支持可验证的 HTTPS/mTLS 传输。服务端
使用 TLS 1.2+ 证书，可通过 client CA 强制客户端证书；worker 客户端支持
自定义 CA 和客户端证书，不提供 hostname 校验绕过。

真实 loopback 进程门禁协商 TLS 1.3，验证服务端证书、无可信客户端证书拒绝、
有证书通过、Bearer + worker HMAC 保持、unsigned claim `401`、明文 HTTP
回退失败，以及 worker agent 的签名注册/heartbeat/claim/stop 生命周期。

后续把传输和真实业务进程合并：通过 mTLS 上传完整 StickS3 flash、compose
firmware、提交 durable job，由带客户端证书与 HMAC 的 worker 启动真实 QEMU
session，下载 evidence，核对 SHA256 并提交 terminal `completed/PASS`。

第三次门禁使用 unified StickS3 镜像和 `qemu-unified` profile，在同一个
mTLS worker job 中验证 board/WiFi/BLE serial markers、network evidence、
pcap 和 PNG frame；所有文件均来自同一个下载的 evidence ZIP。

## 关键证据

- 平台测试：`305/305 PASS`；
- Node：`2/2 PASS`；
- GitHub Actions CI run `40070863490`：两个 job 均 `PASS`；
- GitHub Actions CI run `40071518376`（QEMU follow-up）：两个 job 均 `PASS`；
- GitHub Actions CI run `40071841654`（unified follow-up）：两个 job 均 `PASS`；
- TLS：最小 TLS 1.2，实测 TLS 1.3；
- transport：真实 HTTPS、mTLS、证书拒绝/通过；
- authentication：Bearer + worker HMAC 未降级，unsigned claim `401`；
- worker：带客户端证书的 agent 退出码 `0`；
- evidence SHA256：
  `9342e8f549129ab215a1bd08f7efa6d07ca03d97d0084ac8badb8c2e8dbbb114`。
- real QEMU job evidence SHA256：
  `7b718b72d7ca5a2f244349294b6e1655fb6690cc63371599f202a40fd08c2b2c`；
- firmware SHA256：
  `a5d027f6d2953edb9ece45cddea1490112d8e421ba563edc6e7c71cf7ac4f6ec`；
- job：`completed / PASS / attempts=1`。
- unified firmware SHA256：
  `43429d475fea7ce8dfd24fe34c373e8cd0cb9196b1f64a1f60f42957547580c9`；
- unified evidence SHA256：
  `87fb8d04f630833cbebcc2d0842a8dabe94b02a4f20c6c60a106341496a4f423`；
- unified pcap / frame：`9570` / `2885` bytes。

## 文件

- `report.md`：实现、验证、边界和回滚
- `run.json`：机器可读记录
- `evidence/verification.transport.json`：传输安全证据摘要
- `evidence/verification.qemu-job.summary.json`：真实 QEMU job over mTLS 的 follow-up
- `evidence/verification.unified-job.summary.json`：unified board/WiFi/BLE job over mTLS 的 follow-up

## 未覆盖项

- 跨主机网络拓扑、延迟和丢包；
- 证书或 worker 凭据热轮换；
- 生产 CA/证书生命周期；
- 任意其他固件的 unified board/network/UI PASS；
- 多主机调度和 worker continuity；
- 真机、RF 或硬件验证。
