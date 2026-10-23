# Linux Namespace TLS/Host Allowlist 复测

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`hardware_test`
- 问题来源：上一记录的 Linux namespace TLS `NOT RUN` 后续验证
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`28a51f4b86abd39686214cedf94b2214810f6ca2`
- 基线版本：`f0f7065b7ba42ba914a74b6d80ceb2c88c8e52eb`
- 环境：Linux arm64 容器；同一 QEMU 源树重建的 ESP32-S3 QEMU

## 结论

在 Linux private network namespace 中复用同一 StickS3 TLS/Host allowlist
fixture，所有断言 PASS：

- QEMU 位于新 private network namespace；
- namespace 无外部路由；
- guest WiFi 关联、DHCP；
- CA 写入 VFS 并加载；
- TLS 握手；
- 允许 Host 返回 200；
- 拒绝 Host 返回 403；
- pcap 记录 DHCP 和 TLS flow，DNS 无响应。

## 关键证据

- `private_namespace=true`；
- `no_external_route=true`；
- `tls_allow_and_deny=true`；
- `tls_port_observed=true`；
- `pcap_written=true`；
- Linux arm64 QEMU 使用 patch `0027`；
- 平台测试：`223/223` PASS；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`
- `run.json`
- `evidence/verification.summary.json`

## 未覆盖项

- 通用 destination egress allowlist / controlled resolver；
- DHCP renewal、双设备 lab fabric 和正式 worker/CI；
- 真机 TLS、RF、功耗和电气行为。
