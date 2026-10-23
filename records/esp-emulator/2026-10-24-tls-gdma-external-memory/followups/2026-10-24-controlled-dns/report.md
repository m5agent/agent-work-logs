# Linux Namespace Controlled DNS 报告

## 背景

现有 `egress=allowlist` 只控制 HTTPS gateway 的 Host。QEMU `user` 网络
默认仍读取 QEMU 进程的 host resolver，不能让 guest 使用 lab 内置 resolver。
本轮补齐 DNS allow/deny 数据面。

## 实现

1. sandbox 创建 private network namespace；
2. 启用 controlled DNS 时再创建 private mount namespace；
3. 写入临时 `resolv.conf`，仅绑定到该 mount namespace；
4. controlled DNS server 监听 loopback UDP；
5. QEMU 通过正常的 SLiRP DNS 路径查询该 resolver；
6. 允许域名返回 A，其他域名返回 NXDOMAIN；
7. 请求日志、TLS 决策和 pcap 写入 evidence。

宿主机或容器的全局 `resolv.conf` 不被修改。

## 验证

```text
private_namespace             true
no_external_route             true
controlled_dns                true
allowed.lab.test              A
denied.lab.test               NXDOMAIN
UIFlow/NTP background names   NXDOMAIN
TLS allow host                 200
TLS deny host                  403
pcap_written                  true
platform tests                 223/223 PASS
```

## 边界

- 这是 virtual-device validation；
- controlled DNS 只返回允许主机名，不是通用递归公网 DNS；
- allowlist 仍不是目标 IP/端口级通用 egress policy；
- 真机和恶意固件沙箱结论未覆盖。

## 回滚

源码回滚点 `28a51f4b86abd39686214cedf94b2214810f6ca2`。回滚
`6de2f923735937aac19457ccb37469ae03cfb822` 会移除 controlled DNS 和本轮
证据，但不会影响已有 namespace 与 TLS 能力。
