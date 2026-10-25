# ESP Emulator 有界 CIDR、domain-set 与代码/文档重整报告

## 背景

用户要求完整整理 ESP Emulator 的代码和文档，并指出多个页面仍沿用后续
网络、BLE、worker 和固件审查工作之前的结论。审计确认 `AGENTS.md`、
`platform/README.md`、Device Service API、网络方案和若干当前状态页面仍把
CIDR/domain-set 写成不支持。

工作区同时存在上一轮未收口的 CIDR/domain 草稿，尚未有安全的数据模型和
完整测试。本次目标是先闭合该实现，再统一文档和待办边界。

## 结论

### 有界 CIDR

- IPv4 最宽 `/16`，IPv6 最宽 `/48`；
- 拒绝过宽前缀、unspecified、loopback、link-local、multicast、
  IPv4-mapped IPv6 和 QEMU SLiRP synthetic 网段；
- exact loopback/link-local 也由 caller 拒绝；受控 fixture 只能通过
  guest-visible QEMU SLiRP host pseudo-address 映射到 host loopback；
- nftables 直接生成 IPv4/IPv6 地址或 CIDR 规则，继续使用每 session
  dual-stack veth/NAT 和 fail-closed cleanup。

### Domain set

`allowed_domains` 是 DNS suffix 列表，不是任意 DNS answer 授权：

- 只匹配 suffix 本身或 `.suffix` 子域；
- `evilallowy.test` 不匹配 `allowy.test`；
- exact record 优先，然后按最长 suffix 匹配；
- controlled DNS 的每个 suffix 必须有显式 answer；
- 每个 answer 必须被至少一个 allowed endpoint 的地址/CIDR 覆盖；
- HTTP Host 与 DNS 规则使用同一 suffix 边界；
- domain 不替代 IP/端口策略，也不会接受外部 resolver 返回的任意地址。

Device Service 的 managed fixture 将 exact Host/domain answer 绑定到
QEMU SLiRP host pseudo-address，因此 controlled name 必须同时有 managed
HTTP profile 或 exact SLiRP endpoint。

### 文档收口

Device Service API/OpenAPI 升到 `1.29.0`，同步：

- `AGENTS.md` 稳定边界；
- `README.md` 和 `platform/README.md`；
- `project-status.md`、`workstreams.md`、`project-backlog.md` 的边界；
- `network-simulation-plan.md`、`code-map.md`、`docs/README.md`；
- `validation-ledger.md` 和自动生成的 `project-snapshot.md`；
- 过时短语的文档一致性断言，防止“CIDR/domain 不支持”再次回流。

## 执行

Linux policy fixture 在 privileged Docker 的 private network namespace
中执行。允许一个 IPv4 `/30` 内目标和一个 exact IPv6 目标，同时验证：

- 允许端口/IP 可达；
- 同一地址的未允许端口被阻断；
- CIDR 外地址被阻断；
- IPv6 exact target 可达、错误端口/地址被阻断；
- IPv4/IPv6 都经过 worker veth NAT；
- namespace、NAT table、inner/worker/upstream namespace 清理完成。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、OpenAPI YAML、Node tests |
| transport | `PASS` | Linux namespace nftables/veth/NAT fixture |
| device_response | `NOT RUN` | 本轮没有新增 guest firmware policy lifecycle |
| data_behavior | `PASS` | allowed/denied CIDR/address/port 和双栈 NAT |
| visual_or_physical | `NOT RUN` | 没有物理硬件或 RF 验证 |

```text
Linux CIDR/dual-stack fixture     22/22 PASS
platform contracts                411/411 PASS
documentation contracts           22/22 PASS
Node sha256/upload                2/2 PASS
runtime coverage                  PASS
peripheral catalog                PASS
QEMU profiles                     PASS
project snapshot                  PASS
OpenAPI YAML                      PASS
selected Ruff E9/F                PASS
git diff --check                  PASS
GitHub Actions 40145733947        PASS
GitHub Actions 40145813958        PASS (evidence commit)
```

## 验证边界

- `domain-set` 的 DNS/HTTP/binding 路径由单元和契约测试验证；本轮 Linux
  网络 fixture 只把 IPv4 目标改成 CIDR，IPv6 仍为 exact endpoint。
- 没有证明公网 resolver、动态 DNS、任意外部域名或 certificate pinning。
- 没有新增 WPA3/group multicast、RF/PHY、跨主机 executor 或真机结论。
- 当前 namespace policy 仍不是恶意固件 disposable VM。

## 风险与回滚

新增字段是可选 API，不影响 trusted-host 默认路径。安全语义比旧实现更严格：
调用方若过去传 exact host-loopback/link-local endpoint，现在会 fail closed，
应改用受控 QEMU SLiRP synthetic endpoint 或受支持 fixture。

回滚顺序为 `git revert 7da51aa` 后再 revert
`8c125fb580482cb25f38e3a45630654eb94e6dc9`。回滚只影响虚拟网络策略和文档，
不涉及物理设备、凭据或不可逆硬件状态。
