# ESP Emulator engineering handoff and documentation freshness 报告

## 背景

- 来源：用户要求完整整理代码、文档、目前工作和待办，并指出部分页面仍是
  后续里程碑之前的描述。
- 现象：仓库已有自动快照、当前状态、Backlog、代码地图和验证台账，但专题页
  与入口页之间缺少统一的人读交接；部分页面还使用“本轮结果”等相对时间措辞。
- 目标：提供一页可交接的总览，同时保持动态事实、当前能力、待办和证据各自
  只有一个权威入口。

## 结论

- 状态：`PASS`（docs/contracts）。
- 关键判断：文档问题主要是职责分散和相对时间措辞，不是缺少更多状态表。
- 改动范围：新增工程交接页；统一根目录、Platform、设备、测试、网络、服务
  架构和固件工作流入口；修正 UIFlow2 全矩阵页面为固定基线；增加文档契约，
  防止交接页复制动态计数或遗漏 Backlog Task。

## 变更

### 权威分层

| 页面 | 职责 |
| --- | --- |
| `docs/engineering-handoff.md` | 人读交接、代码阅读顺序、工作流摘要和 P0 导航 |
| `docs/project-status.md` | 当前能力、风险与验证边界 |
| `docs/project-backlog.md` | 未完成 Task、依赖与验收 |
| `docs/project-snapshot.md` | 机器生成的设备/样本/Task/规模计数 |
| `docs/validation-ledger.md` | 带日期的单次验证记录 |
| `docs/code-map.md` | 源码、测试、证据和维护债 |

交接页明确标注为导航摘要，不维护动态数量。新增测试会检查：

- 页面保留结论、成熟度、代码、工作流、下一步、文档职责和最小验证集；
- 所有 Backlog Task ID 都出现在交接页；
- 交接页持续链接当前状态、Backlog、自动快照、验证台账和代码地图；
- 交接页不复制设备数、矩阵检查数、evidence 数或平台测试数；
- 页面明确物理跨主机和 `NOT RUN` 边界。

### 最新工作回写

交接页已覆盖当前主线，包括：

- controlled DNS A/AAAA/CNAME 与同 guest CNAME lifecycle；
- 有界 IPv4/IPv6 CIDR egress、双栈 veth/NAT 与 cleanup；
- worker control/runtime 双平面、HMAC、HTTPS/mTLS、rotation、discovery、
  restart/reattach、idempotency 和 companion continuity；
- 两个独立 Docker 容器中的 worker-local QEMU/evidence；
- Core2 native-HCI、重连、active-stop、bounded TCG、虚拟 PSRAM 和长时
  active-BLE 功能保持；
- FirmwareManifest/WebBurner、capability/security、SD/NVS、公开矩阵和
  macOS arm64 runtime bundle。

精确实测轮次、SHA 和 evidence 只链接验证台账，不在交接页复制。

### 相对时间修正

`docs/uiflow2-peripheral-test-matrix.md` 的“本轮结果”改为
“基线全矩阵结果（固定证据）”，并明确 `2026-10-24` 干净全量矩阵不是后续
每个里程碑的自动最新结果。较新的 unified、network、Core2 soak 和固件审查
结论应从当前状态/验证台账与具体 evidence 读取。

## 执行

- 环境：macOS Apple Silicon；Python 3；Node.js；GitHub Actions Ubuntu。
- 生成物：运行 `project_snapshot.py --write` 更新文档页数、行数和平台测试数。
- 本地：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
node --test platform/tests/test_firmware_upload.mjs \
  platform/tests/test_sha256.mjs
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
git diff --check
```

- 结果：平台 `429/429`、文档契约 `26/26`、Node `2/2`，其余检查均 PASS。
- CI：run `40155261653`，两个 job 均 PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/static | `PASS` | compileall、OpenAPI YAML、diff check、生成物 check |
| docs contract | `PASS` | 链接、索引、新鲜度、交接页和 Task ID 检查 |
| platform contract | `PASS` | `429/429` 平台测试 |
| browser tooling | `PASS` | Node SHA256/upload `2/2` |
| CI | `PASS` | `40155261653` 两个 job |
| QEMU functional | `NOT RUN` | 本次没有修改运行时实现 |
| hardware/RF/power | `NOT RUN` | 没有真机操作或测量 |

## 验证边界

本记录只证明文档结构、生成物和契约一致，不新增设备功能 PASS。已有 QEMU
证据仍按原记录和提交 SHA 引用；物理跨主机仍不是 cross-container PASS 可以
继承的结论。

## 风险与回滚

风险是新增交接页以后再次被手工写入动态计数。文档契约已把该风险变为测试
失败。回滚可 revert 源码提交 `e914b9f`；不会影响 QEMU、记录中的
firmware/ROM、服务状态或其他工作记录。
