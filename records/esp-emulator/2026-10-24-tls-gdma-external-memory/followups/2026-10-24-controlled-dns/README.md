# Linux Namespace Controlled DNS

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`hardware_test`
- 问题来源：网络 P0 的 DNS/egress policy
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`6de2f923735937aac19457ccb37469ae03cfb822`
- 基线版本：`28a51f4b86abd39686214cedf94b2214810f6ca2`
- 环境：Linux arm64 容器；QEMU ESP32-S3；

## 结论

namespace sandbox 新增 controlled DNS。它先创建 private mount namespace，
只向 QEMU 子树绑定临时 resolver 配置，不修改宿主机或容器全局配置。

同一 StickS3 guest 完成：

- `allowed.lab.test` 解析为 lab gateway 地址；
- `denied.lab.test` 返回 NXDOMAIN；
- UIFlow/NTP 后台域名全部返回 NXDOMAIN；
- 随后 TLS Host allowlist 继续返回允许 200、拒绝 403；
- pcap 保留 DNS、DHCP、TLS 流。

## 关键证据

- `controlled_dns=true`；
- `dns_allow_and_deny=true`；
- `dns_background_denied=true`；
- `tls_allow_and_deny=true`；
- namespace 无外部路由；
- 平台测试：`223/223 PASS`；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`
- `run.json`
- `evidence/verification.summary.json`

## 未覆盖项

- 目标地址/端口级通用 egress allowlist；
- DHCP renewal 和双设备 lab fabric；
- 正式 worker/CI；
- 真机 RF、TLS、功耗和电气行为。
