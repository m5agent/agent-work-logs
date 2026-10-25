# ESP Emulator bounded DNS CNAME and code/document reconciliation report

## 背景

- 来源：
  [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- 现象或需求：controlled DNS 只解析 exact A/AAAA 与 domain suffix，CNAME
  query 无答案；同时多份当前文档重复手写测试、设备和 profile 数量，已经出现
  漂移。
- 目标：补齐受 policy 约束的 CNAME resolver 数据面，接入 Device Service/API，
  并把当前事实、动态快照和剩余工作重新分层。

## 结论

Resolver 与 API 改动完成：

- exact-name CNAME alias 最多 8 跳；
- alias、每个 intermediate target 与 terminal 都受 `allowed_hosts` /
  `allowed_domains` 约束；
- A/AAAA response 返回 CNAME chain + terminal address，CNAME query 返回
  chain；
- cycle、uncontrolled terminal、越权 alias、CNAME owner 与 exact/domain
  address 冲突、9 跳 chain 全部 fail-closed；
- Device Service 接受 top-level `network.cname_records`，否则返回结构化
  `invalid_network`；
- OpenAPI 从 `1.29.0` 升到 `1.30.0`。

文档与任务队列同时收敛：

- 平台测试数、设备数、后端数和 profile 数只由自动项目快照生成；
- 当前状态页明确 CNAME resolver `PASS`，同 guest CNAME 生命周期 `NOT RUN`；
- 新增 `NET-07`，其验收要求同一 lease 的 guest DNS、TCP/HTTP、pcap、
  serial 与 cleanup；
- 修订网络中仍写过时动态数量或把已完成能力留在待办中的页面。

## 证据

### 代码或配置

- `platform/tools/network_sandbox.py`：CNAME normalization、chain resolution、
  policy binding、A/AAAA/CNAME encoding 和 isolation evidence；
- `platform/tools/device_service.py`：`parse_dns_cname_records()` 与 sandbox
  DNS config 接线；
- `docs/device-service.openapi.yaml`、`docs/device-service-api.md`：
  `network.cname_records` 与 API `1.30.0`；
- `platform/tests/test_network_sandbox.py`、
  `platform/tests/test_device_service.py`、`test_docs_consistency.py`：
  resolver、service、OpenAPI 和文档一致性门禁。

### 执行

- 环境：macOS arm64、Python 3.13.15、Node 20。
- 命令：

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
ruff check --select E9,F63,F7,F82,I,F401,F841 \
  platform/tools/device_service.py platform/tools/network_sandbox.py \
  platform/tests/test_device_service.py \
  platform/tests/test_docs_consistency.py \
  platform/tests/test_network_sandbox.py \
  tests/network/dns_cname_chain/run_test.py
```

- 结果：平台 `425/425 PASS`；Node `2/2 PASS`；其余 contract/static checks
  全部 PASS。
- GitHub Actions：
  [CI 40152639444](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40152639444)
  在 commit `8710e41` 上两个 job 全成功。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall、Node tests、API YAML、docs consistency |
| transport | `PASS` | 本机 UDP resolver 的 A/AAAA/CNAME/NXDOMAIN 请求响应 |
| device_response | `NOT RUN` | 未启动 guest firmware |
| data_behavior | `PASS` | exact/domain terminal、chain encoding、policy 和负向图均按预期变化 |
| visual_or_physical | `NOT RUN` | 无显示、RF、电气或物理测试 |
| delivery | `PASS` | commit `8710e41`，CI `40152639444` 两 job PASS |

## 验证边界

本次 evidence 是 `resolver-data-plane validation`。它不证明一个真实 guest
固件能查询 CNAME、跟随 terminal A/AAAA 并完成 TCP/HTTP；该门禁由 `NET-07`
跟踪。Linux namespace 下的 guest CNAME 生命周期、public DNS、DNSSEC、
rebinding 防护、RF/PHY、功耗、物理 cache/PSRAM 和硬件均未验证。

## 风险与回滚

没有不可逆设备操作或持久状态迁移。若需回滚，revert
`8710e41bf00d592ad0a5a7b9e5a3d5f32a333f9d` 可移除 CNAME API/resolver
支持、`NET-07`、CNAME evidence 和本轮文档结构收敛；既有 A/AAAA 与 domain
suffix 行为不会被数据迁移阻塞。
