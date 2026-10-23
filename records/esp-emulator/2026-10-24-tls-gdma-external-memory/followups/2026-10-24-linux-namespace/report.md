# Linux Namespace TLS/Host Allowlist 复测报告

## 背景

上一轮已完成 trusted-host TLS/Host allowlist，并修复 ESP32-S3 GDMA
外部内存读取。Linux namespace TLS 当时未执行。

本轮目标是在同一固件路径、同一 QEMU patch 上补 private namespace 证据。

## 执行

1. 使用现有 Linux arm64 QEMU 构建目录，增量重编译 `0027` patch；
2. 在 Ubuntu Linux arm64 容器中安装 Linux `littlefs-python`；
3. 挂载同一 QEMU source `pc-bios`，补齐 ESP32-S3 ROM；
4. 在带有 network namespace 权限的容器中运行 TLS fixture；
5. 由 fixture 自己创建 namespace，启动 HTTPS gateway 和 QEMU guest；
6. 验证 WiFi/DHCP、CA、TLS、Host allow/deny 和 pcap。

## 结果

```text
private_namespace             true
no_external_route             true
TLS_WIFI_READY                true
TLS_CONTEXT_READY             true
TLS_CA_LOADED                 true
allowed.lab.test              200
denied.lab.test               403
tls_port_observed             true
dns_responses                 0
pcap_written                  true
```

平台测试仍为 `223/223 PASS`。

## 验证边界

- 这是 Linux virtual-device validation，不是物理硬件验证；
- Host allowlist 仍不是通用 destination IP/端口 egress policy；
- controlled resolver、DHCP renewal、双设备 fabric 和 worker/CI 生命周期
  仍未完成；
- 不证明 RF、功耗、声学、光学或电气属性。

## 风险与回滚

本 follow-up 只新增复测证据和文档，没有新增运行时代码。回滚源码提交
`28a51f4b86abd39686214cedf94b2214810f6ca2` 不会删除已验证的实现路径，
只会移除本轮 Linux namespace 证据和状态更新。
