# ESP Emulator 精确 IPv4 IP/端口 Egress Allowlist 报告

## 背景

Linux namespace 已支持 controlled DNS、TLS Host allowlist、pcap、错误密码和
断线重连，但此前“allowlist”仅限制 Host 和 DNS，不是实际网络目标策略。
待审固件仍可能访问允许 Host 之外的目标，或者用数字 IP 绕过 DNS/Host。

目标是增加内核执行的 exact IPv4 `protocol + address + port` 策略，并保留：

- QEMU SLiRP 的 lab fixture；
- controlled DNS；
- TLS Host decision；
- 外部 IPv4 允许路径；
- pcap 和清理 evidence。

## 实现

### API 与验证

新增 `network.policy.allowed_endpoints`：

```json
{
  "protocol": "tcp",
  "address": "10.0.2.2",
  "port": 18443
}
```

- 最多 64 项，只接受精确 IPv4 地址和 TCP/UDP 端口；
- 拒绝 unspecified、multicast、CIDR、域名和外部 IPv6；
- `egress=allowlist` 要求 `allowed_hosts` 或 `allowed_endpoints`；
- controlled DNS 要求非空 `allowed_hosts`；
- 带 controlled HTTP fixture 的 profile 自动补充 fixture endpoint；
- 没有 HTTP fixture 的 profile 可使用显式 endpoint。

### Linux 执行

新增 `platform/tools/network_egress.py`：

- 生成 nftables input/output default-drop rules；
- established/related connection 放行；
- loopback TCP/UDP 仅放行 DNS、HTTP/TLS、HCI、GDB 等内部端口；
- `10.0.2.2` 转换为 worker loopback socket；
- 其他 IPv4 自动创建 per-session namespace、veth pair、default route 和
  temporary NAT table；
- 检查 `iproute2`、`nftables`、root 和 `net.ipv4.ip_forward`；
- 失败关闭，任务结束时删除 namespace 和 NAT table。

`network_sandbox.py` 现在有 outer gateway 和 inner namespace 两层：

1. worker namespace 创建 veth/NAT；
2. inner namespace 安装 nftables policy；
3. controlled DNS/HTTP/BLE fixtures 与 QEMU 在 inner namespace 运行；
4. outer 进程负责信号、退出码和清理。

## 验证

### 网络策略 fixture

worker-local target 和 denied target 均绑定并监听：

```text
allowed exact IP:port          connected, HTTP 200
same IP, denied port           TimeoutError
same allowed port, other IP    TimeoutError
1.1.1.1:80 via veth/NAT        connected, HTTP 301
denied target requests         0
nftables policy                input/output default drop
cleanup                        namespace and NAT table removed
```

### StickS3 guest

在 nftables exact endpoint 策略下，原 TLS fixture 保持通过：

```text
WiFi/DHCP                       PASS
controlled DNS A/NXDOMAIN       PASS
TLS allowed Host 200            PASS
TLS denied Host 403             PASS
exact 10.0.2.2:18443/tcp        PASS
pcap                             77 packets, 0 malformed
image SHA256                     226f84df...
```

### 平台回归

```text
platform tests                 234/234 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
ruff changed modules           PASS
git diff --check               PASS
```

源码 `main` 已推送：

```text
base    97d9a80e1a1abe6a9870e79d2bc2ca81583e6f7d
result  e14169f4c49d8651444b987172b0ab0135a93e11
```

## 验证边界

- 网络策略 fixture 验证 Linux namespace/nftables/veth/NAT，不是 firmware PASS；
- StickS3 TLS 是 virtual-device validation；
- 没有重跑 67-case UIFlow2 全矩阵；本次不修改外设/QEMU controller；
- 外部 IPv6、CIDR、域名多 IP 和 DHCP renewal 未实现；
- 物理 RF、网络性能、长期 soak 和真机仍为 `NOT RUN`；
- 不是恶意固件 VM sandbox。

## 风险与回滚

Linux worker 必须提供 root/等效网络权限、`iproute2`、`nftables` 和 IPv4
forwarding。任何依赖缺失或 rule 安装失败都会阻止 session 启动。

临时 namespace、veth 和 NAT table 使用随机名称；正常退出有测试覆盖。若
worker 被 `SIGKILL`，运维层仍需 GC 残留 `m5eg-*`/`m5nat_*` 对象。

回滚源码提交 `e14169f4c49d8651444b987172b0ab0135a93e11`
会恢复旧 Host-only allowlist；不会修改已保存的 firmware artifact 或 QEMU
设备数据面。
