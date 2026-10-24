# ESP Emulator Worker HTTPS/mTLS, Signed Jobs and Overlap Credential Rotation

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码版本：`m5agent/m5stack-esp-emulator @ ea6e4cb37460f6ce20fc2f18f03224c8724ae0cd`
- QEMU job follow-up：`m5agent/m5stack-esp-emulator @ 865e4f810263f3f388beeee3aa577de27f99d0b1`
- unified job follow-up：`m5agent/m5stack-esp-emulator @ 48ff20c416221e20f76873c07d7473329318eb5c`
- TLS/token rotation follow-up：`m5agent/m5stack-esp-emulator @ b01e95b22c163c270d1ef632c1abb75cbdd4c527`
- activity-drain follow-up：`m5agent/m5stack-esp-emulator @ e1c18f6eb46fc172f5e2048f5b233cb5ca596765`
- bounded-overlap follow-up：`m5agent/m5stack-esp-emulator @ 5dbc5aad1fadf8c4564147255a8be2b1e30c115b`
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

第四次门禁加入 file-backed token 和 `SIGHUP` A/B rotation。服务端与 worker
原子替换临时 PKI、客户端 CA、worker 客户证书/key 和 master token；旧 CA
身份与旧 token 均被拒绝，新凭据继续注册/heartbeat/claim，并完成真实
StickS3 QEMU job。

第五次门禁补上活动请求 drain。服务收到 `SIGHUP` 后停止接纳新 handler，
等待一个旧 token 的未完成 artifact 上传返回 `201`，之后才提交 token/TLS
配置；默认等待上限 30 秒，超时则取消 reload 并保留旧配置。随后仍验证旧
CA/token 拒绝、新凭据真实 QEMU job。该结果只覆盖同主机 loopback；旧/新
凭据重叠窗口、客户端批量迁移、跨主机 continuity 和生产 secret manager
仍未验证。

第六次门禁加入有界凭据重叠：

- 第一阶段同时信任 A/B client CA，Bearer 和 worker HMAC 同时接受 A/B token；
- 旧客户端和旧 token 仍可访问，worker 随后切到 B；
- 删除 previous token/CA 文件并再次 `SIGHUP`，旧 CA 握手和旧 token 最终失败；
- 最终由新凭据完成真实 StickS3 QEMU job。

客户端 trust bundle 迁移在本 fixture 中由测试手工 staged。自动化客户端发现、
批量迁移和跨主机 continuity 仍未验证。

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
- rotation checks：`9/9 PASS`；
- rotation scope：
  `same-host-loopback-sighup-tls-token-rotation`；
- rotation 后 firmware SHA256：
  `a5d027f6d2953edb9ece45cddea1490112d8e421ba563edc6e7c71cf7ac4f6ec`；
- rotation 后 evidence bytes / SHA256：`6853` /
  `51899986348661abefb82d042ea85f3007e54e33f2c366bd218573b2450761e8`；
- rotation 后 job：`completed / PASS / attempts=1`；
- rotation follow-up：平台测试 `306/306 PASS`，GitHub Actions CI run
  `40072474174` 两个 job 均 `PASS`。
- activity-drain checks：`10/10 PASS`；
- activity drain 后 evidence bytes / SHA256：`6850` /
  `c67f44265ecad925c8bd2069041fd4cfa65f9a3ac4dab2f1f03f2cb4403a1c0a`；
- activity-drain follow-up：平台测试 `308/308 PASS`，GitHub Actions CI run
  `40072991528` 两个 job 均 `PASS`。
- bounded-overlap checks：`13/13 PASS`；
- bounded-overlap 后 evidence bytes / SHA256：`6847` /
  `dc061cb2a848fb7971de7cac712cdf74681c6367ab7d7f436d8ceaed7c9c5e21`；
- bounded-overlap follow-up：平台测试 `309/309 PASS`，GitHub Actions CI run
  `40073423924` 两个 job 均 `PASS`。

## 文件

- `report.md`：实现、验证、边界和回滚
- `run.json`：机器可读记录
- `evidence/verification.transport.json`：传输安全证据摘要
- `evidence/verification.qemu-job.summary.json`：真实 QEMU job over mTLS 的 follow-up
- `evidence/verification.unified-job.summary.json`：unified board/WiFi/BLE job over mTLS 的 follow-up
- `evidence/verification.rotation.summary.json`：TLS/token rotation 与轮换后 QEMU job 的 follow-up
- `evidence/verification.rotation-drain.summary.json`：活动请求 drain、超时保留旧配置和轮换后 QEMU job 的 follow-up
- `evidence/verification.rotation-overlap.summary.json`：A/B bounded overlap、final cutover 和轮换后 QEMU job 的 follow-up

## 未覆盖项

- 跨主机网络拓扑、延迟和丢包；
- 自动化客户端发现与批量迁移；
- 生产 CA/证书生命周期；
- 生产 secret manager 集成；
- 任意其他固件的 unified board/network/UI PASS；
- 多主机调度和 worker continuity；
- 真机、RF 或硬件验证。
