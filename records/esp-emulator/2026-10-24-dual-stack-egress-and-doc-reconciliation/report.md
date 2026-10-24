# ESP Emulator exact IPv6 egress 与代码/文档重整报告

## 背景

- 来源：用户要求完整整理当前代码、文档、在途工作和待做，并指出部分文档没有
  反映后续工作。
- 现象：exact egress 契约和多个专题页仍把外部 IPv6 描述为不支持；Backlog
  仍保留 `NET-05`。同时工作树中已有一份未完成的 IPv6 gateway 改动。
- 目标：完成或明确回退未完成代码，使运行时契约、测试、证据、当前状态、
  Backlog、自动快照和专题文档重新一致。

## 结论

- 状态：`PASS`（virtual-network policy validation）。
- 关键判断：IPv6 不能只靠 nftables 字符串单测；必须实际经过 IPv6 default
  route、neighbor discovery、veth 和 masquerade，并证明允许/拒绝与清理同时成立。
- 改动范围：`network_egress.py`、`network_sandbox.py`、`network_policy.py`、
  平台契约测试、Linux egress fixture、CI、OpenAPI/API 和项目文档。

## 改动

### 运行时

- 接受并规范化 IPv6 endpoint；IPv4-mapped IPv6 统一规范为 IPv4。
- 为 outer worker 增加 `/126` ULA veth 地址、IPv6 default route、
  `default_ipv6_interface` 和 `nodad`。
- nftables NAT 从 `table ip` 升级为 `table inet`，按地址族生成 masquerade。
- 只增加 IPv6 neighbor solicitation/advertisement 作为必要控制面例外。
- fail-closed 检查 IPv6 forwarding；route ownership 校验允许 expected
  gateway default route、connected subnet 和链路本地/组播基础路由，拒绝其他
  external route。
- 清理同时覆盖 inner NAT table、inner namespace、worker namespace 和
  upstream namespace。

### 验证

- 新增独立 worker/upstream namespace fixture，避免以 host-local 目标绕过 NAT。
- IPv4 和 IPv6 各启动 allowed、denied-port、denied-address 服务；只允许
  两个 exact endpoint。
- upstream peer 记录必需等于 worker veth 地址，证明 masquerade 实际发生。
- fixture 连续运行两次，均为 `PASS`。
- GitHub Actions 对同一源码提交执行相同 fixture，`network-namespace-policy`
  job 成功。

### 文档

- 关闭 `NET-05`，从 Backlog 和生成快照移除。
- 重新生成自动项目快照。
- 在 `workstreams.md` 增加“已交付 / 当前在途 / 下一验收门禁”和待做顺序。
- 同步 README、OpenAPI、Device Service API、网络专题、部署、服务架构、
  固件审查、项目状态、验证台账和代码地图。
- 把 Core2 新 `7200s` run 标记为在途；只有后续 evidence 完整才可改 PASS。
- 把 `RUNTIME-03` 的 AXP `0x34`/chip-id `0x4a`、后续 `0x51` 无 ACK、
  BM8563 candidate 和下一步 port/pin/bus trace 写入当前缺口页与 Backlog。

## 执行

- 环境：macOS 测试主机、独立特权 Linux container、GitHub Actions
  `ubuntu-latest`。
- 本地：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform tests
node platform/tests/test_sha256.mjs
node platform/tests/test_firmware_upload.mjs
python3 tests/network/egress_allowlist/run_test.py --out-dir /tmp/m5-egress
```

- 本地双栈 egress 连续两次 `PASS`。
- 平台测试 `336/336 PASS`；Node `2/2 PASS`；catalog/profile/coverage/
  snapshot 全绿。
- GitHub Actions run `40098666896`（source `5db301a`）和 run
  `40098772592`（final source `9981460`）均成功。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall、Node 测试、全部平台契约测试 |
| transport | `PASS` | inner veth、IPv4/IPv6 default route、masquerade 与 nftables 实际数据面 |
| device_response | `NOT RUN` | 不是固件 guest 测试 |
| data_behavior | `PASS` | exact endpoint 200、other port/address timeout、upstream 源地址与 cleanup |
| visual_or_physical | `NOT RUN` | 不涉及画面、RF、电气或物理设备 |
| delivery | `PASS` | 源码与文档 commit 已推送；CI 成功 |

## 验证边界

- 结果只证明 Linux virtual-network policy；不证明固件应用、云服务、
  公网 IPv6 可达性或网络内容安全。
- CIDR、domain-set、IPv6 DNS/AAAA 和恶意固件 disposable VM 仍是独立任务。
- 本记录不断言 Core2 `7200s` artifact-bound soak 已完成。

## 风险与回滚

- 测试使用独立的 worker/upstream namespace 和随机临时 veth/table；正常路径
  在成功或失败后均清理。
- 生产回滚点是 source commit
  `7d069594bd93d7a7d6165420f111f184eee95d0e`；本次改动可通过 revert
  `5db301ad1e0cea1e30c60d58fceaddf925144cf1` 与后续文档记录提交回退。
