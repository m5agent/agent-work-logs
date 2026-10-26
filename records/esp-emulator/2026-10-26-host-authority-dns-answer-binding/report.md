# ESP Emulator Host authority and exact DNS answer binding report

## 背景

网络 P0 已覆盖 controlled DNS、Host allowlist、TLS、namespace 和 pcap，
但继续审计发现两个边界没有被独立证明：

1. HTTP Host decision 使用 `rsplit(":", 1)` 提取主机，非法端口和逗号拼接
   会被忽略；
2. domain suffix 和 CNAME terminal 已绑定 allowed endpoint，但 exact
   A/AAAA record 使用单独路径，没有同样的 endpoint 绑定。

## 修复前反例

Host policy 只允许 `allowed.lab.test` 时，以下请求都返回 `200`：

```text
allowed.lab.test:not-a-port
allowed.lab.test:443,evil
```

这说明 allowlist 判断的是被截断后的前缀，而不是完整、合法的 Host
authority。该反例先通过最小 HTTP fixture 复现，再写入回归测试。

## 修复

### HTTP Host authority

新增 `normalize_http_authority()`：

- 只接受一个 Host header；
- host 使用严格 ASCII DNS label、single trailing dot 归一化；
- 端口必须为 `1..65535` 的数字；
- 拒绝 userinfo、空白、逗号、反斜杠、未加方括号的 IPv6 和多重冒号；
- 带 policy 的 HTTP 服务只接受 origin-form request target；
- duplicate Host 和 absolute-form request target 返回 `403`。

### Controlled DNS

- exact A/AAAA record 必须由 allowed endpoint 地址/CIDR 覆盖；
- CNAME terminal 沿用同一 exact/domain answer binding；
- IPv4-mapped IPv6 DNS record 直接拒绝；
- exact record names、CNAME aliases/targets、policy hosts 统一使用严格 DNS
  label 校验；
- `dns=controlled` 在 Device Service 合并 implicit endpoints 后仍无
  endpoint 时返回 `invalid_network_policy`。

### API contract

Device Service contract 升到 `1.34.0`，Markdown 和 OpenAPI 同步说明：

- strict `allowed_hosts`；
- controlled DNS 至少需要一个 allowed endpoint；
- exact/CNAME terminal answer binding；
- Host authority 和 request-target 限制。

## 执行

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_network_*.py'

python3 tests/network/dns_cname_chain/run_test.py --out /tmp/dns-evidence.json

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform/tools platform/tests tests
git diff --check
```

Linux namespace TLS：

```text
docker run --privileged ...
  tests/network/tls_allowlist/run_test.py
  --qemu <Linux arm64 QEMU>
  --rom-dir <matching ROM directory>
  --out-dir /out
  --isolation namespace
```

Core2 tool-hash rebind：

```text
run_service_5x.py --attempts 8 --concurrency 8
  --stagger-seconds 0 --hold-seconds 120 --require-psram
```

两批使用同一 `c3eaa35b…` unified firmware 与 `5bec056b…` ELF，分别在独立
Device Service state 和 8 个 QEMU lease 中运行。

## 验证

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| platform contract | `PASS` | `534/534` |
| network policy tests | `PASS` | `73/73` |
| HTTP authority negative controls | `PASS` | 非法端口/逗号/userinfo/duplicate/absolute-form 均 403 |
| DNS exact answer binding | `PASS` | uncovered record 结构化拒绝 |
| Linux namespace TLS/DNS | `PASS` | WiFi、DHCP、allow/NXDOMAIN、TLS 200/403、pcap、cleanup |
| Core2 A/B concurrency | `PASS` | 两批 `8/8`，合计 `16/16` |
| firmware functional | `PARTIAL` | 仅 Core2 unified stress；legacy UIFlow 仍 OPEN |
| physical multi-host | `NOT RUN` | 没有第二个物理 worker 主机 |
| hardware/RF | `NOT RUN` | 没有真机测量 |
| delivery | `PASS` | product `6ecaef5`；CI `40249694316` 两 job 均成功 |

## 验证边界

- Linux namespace 仍是可信主机上的隔离 fixture，不是不可信固件最终 VM；
- 没有物理跨主机 executor/reattach、跨主机幂等或任意 NAT；
- 没有 QEMU guest/controller 内部 side effect 和 worker 未拥有的外部
  side effect fence；
- exact DNS binding 证明当前 controlled resolver 不返回未授权 endpoint，
  不证明外部 DNS/DNSSEC 或 resolver rebinding；
- Core2 结果仍是 virtual-device validation，不证明物理 PSRAM/cache、
  bit-exact Espressif controller/RF 或真机。

## 风险与回滚

没有烧录真机、修改生产网络、写入凭据或迁移持久数据。回滚 product commit
`6ecaef5ddc4323f3c3919edf4ad25670a64c8c8c` 会恢复旧的 Host/exact DNS
语义，并让 Core2 tool-hash rebind 失效；应同时重新建立对应 evidence。
