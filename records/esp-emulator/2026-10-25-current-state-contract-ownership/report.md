# ESP Emulator current-state and documentation contract ownership 报告

## 背景

- 来源：项目在多轮 Core2、网络、worker 和固件审查工作后，当前入口积累了
  大量已完成流水、旧阶段措辞和重复执行顺序。
- 需求：完整整理代码和文档，明确“目前工作”和“待做”，并避免后续继续把
  历史结果写回当前入口。
- 目标：建立可检查的权威关系，同时保持原测试断言和固件结论边界不变。

## 结论

整理前的主要问题不是结论数字本身，而是职责混用：

1. `project-status.md` 同时承担当前能力、历史里程碑和详细运行记录；
2. `project-backlog.md` 声称只列待办，却复制大量已完成轮次和 SHA；
3. `workstreams.md` 声称不保存动态事实，却维护第二份 PASS 计数；
4. 文档契约集中在 6436 行单文件中，stale-claim 仍靠大量手写断言；
5. `worker_cross_container` README 仍把已通过能力写成“下一项”。

本次将入口重新分为：

| 页面 | 职责 |
| --- | --- |
| `README.md` | 产品定位、快速开始和导航 |
| `engineering-handoff.md` | 人读交接、代码阅读顺序和当前最小交付 |
| `project-status.md` | 当前能力、风险和下一步，不保存历史流水 |
| `project-backlog.md` | 开放 Task、依赖和验收 |
| `workstreams.md` | 工作流到代码/权威页/Task 的路由 |
| `validation-ledger.md` | 带日期的运行和 evidence 历史 |
| `code-map.md` | 源码、测试、生成物和契约入口 |
| `project-snapshot.md` | 从机器可读源生成的动态计数 |

当前最小调查入口明确为 `RUNTIME-03`：公开 Core2 固件已读到 AXP chip id，
但 address `0x51` 的 RTC-candidate 事务无 ACK。下一步需要补齐 controller
port/MMIO、SCL/SDA、GPIO mux 和板级 bus trace，再重跑 AXP2101/AXP192
变体。该结论只描述当前缺口，不把 AXP chip-id 可读写成启动 PASS。

## 改动

### 文档契约拆分

- 删除单一 6436 行 `test_docs_consistency.py` 内容，保留 6 行兼容入口；
- 新增五个领域模块：
  - `test_docs_index_contract.py`
  - `test_docs_current_state_contract.py`
  - `test_docs_core2_runtime_contract.py`
  - `test_docs_firmware_security_contract.py`
  - `test_docs_network_worker_contract.py`
- 公共路径和测试计数 helper 放入 `_docs_contract_support.py`；
- 测试方法总数保持不变，仍为 `37`。

### 退役说法数据化

- 新增 `stale_doc_claims.json`；
- 迁移 141 条当前入口禁止重新出现的旧说法；
- 目录记录 schema version、用途、权威文档路径；
- 每条 claim 使用稳定 `STALE-NNN` ID、禁止文本和退役原因；
- 测试校验 ID/text 唯一、authority 文件存在、文本不回流当前入口。

### 当前状态和 Backlog 收敛

- `project-status.md` 从历史流水汇总页压缩为当前能力页；
- `project-backlog.md` 任务板移除已完成 PASS 计数；
- `workstreams.md` 改为纯路由，不再复制执行顺序和运行数据；
- 文档 `DOC-01` 完成后从 Backlog 与工作流 Task 索引移除；
- `worker_cross_container` README 改为已通过状态，并保留物理跨主机边界。

### 页面测试稳定性

Node sessions 测试原先在看到 device select 后立即读取 service summary，
会稳定读到 `Loading service status…`。现在等待 `API online` 状态文本后再
断言页面结构。

## 验证

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform tests
ruff check --select E9,F \
  platform/tests/_docs_contract_support.py \
  platform/tests/test_docs_consistency.py \
  platform/tests/test_docs_*_contract.py
git diff --check
npm test --prefix platform/tests
```

结果：

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall，无语法错误 |
| review | `PASS` | 五个领域文档契约 `37/37` |
| data_behavior | `PASS` | stale claim 目录解析、唯一性、authority 存在性和文本回流检查 |
| visual_or_physical | `NOT RUN` | 本次不涉及设备画面、外设或电气行为 |
| delivery | `PASS` | 源码 commit 与公开仓库推送 |

平台完整套件为 `497/497 PASS`；Node 页面 smoke 通过。
GitHub Actions `40201058851` 的 `platform-contracts` 与
`network-namespace-policy` 两个 job 均成功。

## 验证边界

- 没有重新执行 UIFlow2 外设矩阵、Core2 soak、worker namespace/container
  fixture 或 firmware matrix；
- 没有 physical hardware validation；
- 历史 evidence 没有被本次文档整理改写；
- 当前开放的 `RUNTIME-03`、`NET-04`、`CORE2-02`、`FW-01/02/03`、
  `RUNTIME-02/04` 和 `HW-01` 边界保持不变。

## 风险与回滚

- 风险主要是文档导航和测试路径引用断裂；
- 已由相对链接、文档索引、snapshot、模块导入和完整平台测试覆盖；
- 回滚方式为 revert 源码 commit `2175ebb`，不使用强制推送；
- 本次没有 Flash、eFuse、设备状态或外部服务写操作。
