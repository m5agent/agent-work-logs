# ESP Emulator 精确 IPv4 IP/端口 Egress Allowlist

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`e14169f4c49d8651444b987172b0ab0135a93e11`
- 基线版本：`97d9a80e1a1abe6a9870e79d2bc2ca81583e6f7d`
- 环境：Linux arm64 worker container；root；`NET_ADMIN`/`SYS_ADMIN`

## 结论

Device Service 的 `network.policy.egress=allowlist` 现在可以执行精确 IPv4
`protocol + address + port` 策略，而不是只做 Host/DNS allowlist。

- nftables input/output chain 默认 `drop`；
- 仅允许显式 endpoint、established/related flow 和内部 DNS/HTTP/HCI/GDB
  loopback 控制端口；
- guest-visible `10.0.2.2` 映射到 QEMU SLiRP host-loopback socket；
- 其他允许的 IPv4 通过 per-session veth 和临时 NAT table 外出；
- worker 能力缺失、netns/规则安装失败时 fail-closed；
- 会话结束后 namespace、veth 和 NAT table 均清理。

## 关键结果

- 允许的 worker-local IP+端口：TCP 连接成功，HTTP 200；
- 同一 IP 的未允许端口：超时；
- 同一允许端口但不同 IP：超时；
- `1.1.1.1:80`：经 veth/NAT 连接成功，HTTP 301；
- 未允许的第二台 target server：收到 0 个请求；
- `nftables-default-drop=true`、`veth-nat=true`、namespace/NAT cleanup 均 PASS；
- StickS3 UIFlow2 TLS guest 在同一 nftables 策略下：
  - WiFi/DHCP PASS；
  - controlled DNS A/NXDOMAIN PASS；
  - TLS 允许 Host 200、拒绝 Host 403；
  - exact `10.0.2.2:18443/tcp` evidence PASS；
  - pcap PASS；
- 平台测试：`234/234 PASS`；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`
- `run.json`
- `evidence/verification.summary.json`

## 未覆盖项

- 外部 IPv6、CIDR 和域名到多个 IP 的 egress policy；
- DHCP renewal、真实 AP 丢失和双设备 fabric；
- 恶意固件 VM 隔离；
- 真机 RF、网络性能和长期 soak。
