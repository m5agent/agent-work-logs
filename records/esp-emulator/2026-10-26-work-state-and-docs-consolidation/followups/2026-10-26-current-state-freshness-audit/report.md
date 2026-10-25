# ESP Emulator documentation freshness audit report

## 背景

项目已有当前状态、Backlog、验证台账、工程交接、代码地图、自动快照和大量
专题/用例 README。问题不是缺文档，而是同一事实被多处复制后产生时间差：

- 设备 catalog 仍停在 `2026-10-25`，但最新 Core2 evidence 已是
  `2026-10-26`；
- 自动快照把 catalog 日期显示成整个项目的来源日期；
- README 复制了 exact-time freeze 的地址、虚拟时间和详细调查流水；
- UIFlow2 矩阵仍把更早的 `0008` 全量结果当作最新基线；
- Core2 HCI 页面仍写“最多五实例”，而当前服务容量和证据已到八实例；
- 快照把自身 Markdown 行数计入统计，导致生成页每次写入后行数变化。

目标是建立可机器验证的事实源和幂等生成规则，并把历史 evidence 与当前
能力结论分开。

## 修改

### 快照日期与幂等性

`platform/tools/project_snapshot.py` 现在：

- 保留 `catalog_date`；
- 从 catalog、最新 evidence、docs index、current status、Backlog、
  validation ledger 和 engineering handoff 计算 `fact_date`；
- 用 `fact_date` 检查权威页和委派页的新鲜度；
- 统计 Markdown 文件数时包含所有页面，但行数排除
  `docs/project-snapshot.md`，避免自引用；
- 把旧委派页按项目符号逐条列出，便于逐页复核。

新增契约测试覆盖：

- fact date 覆盖最新 evidence 和 catalog；
- 五个项目入口日期不晚于 fact date；
- 生成页行数不包含自身；
- 旧日期列表顺序和分类边界。

### 文档收敛

- `README.md` 将 Core2 legacy 的长调查流水压缩成稳定结论，精确地址、时间和
  失败 control 只留在状态页/台账；
- `docs/README.md` 解释三类日期的语义，并把快照/GDB 路径标为正确的职责；
- `docs/uiflow2-peripheral-test-matrix.md` 将完整基线切换到 `0036`，
  `0038` 仅记录为 exact-time 诊断和 Core2 定向回归；
- `tests/uiflow2/README.md` 把 canonical `core2-native-hci` 放在
  legacy GDB/VHCI 对照之前；
- `tests/uiflow2/core2_native_hci/README.md` 把 20/30/60/120 轮标为
  progression，当前最大门禁改为 121，剩余并发边界改为大于 8；
- 权威页、测试索引、网络用例、补丁说明和固件 fixture README 的复核日期
  统一到 `2026-10-26`。

## 代码与文档边界

本轮只修改文档生成器、文档契约和 Markdown，不修改：

- Device Service、QEMU、固件、网络策略或 worker；
- session JSON、OpenAPI、evidence ZIP 或 Flash 布局；
- 任何 firmware/ELF/QEMU-bound tool hash。

因此不需要重跑 Core2 并发/长稳 evidence，也不能把本轮平台测试 PASS 继承为
固件功能或硬件 PASS。

## 执行

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check

python3 -m compileall -q platform/tools platform/tests tests
ruff check --select E9,F \
  platform/tools/project_snapshot.py \
  platform/tests/test_docs_index_contract.py \
  platform/tests/test_docs_core2_runtime_contract.py
git diff --check
```

快照幂等性验证：

```bash
python3 platform/tools/project_snapshot.py --write
python3 platform/tools/project_snapshot.py --check
python3 platform/tools/project_snapshot.py --write
python3 platform/tools/project_snapshot.py --check
```

两次均返回 `PROJECT_SNAPSHOT_OK`。

## 验证

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、selected Ruff、snapshot generator 与 diff check |
| documentation contract | `PASS` | platform `510/510`；其中 docs `43/43` |
| generated inventory | `PASS` | coverage/catalog/profile/snapshot checks |
| firmware/QEMU functional | `NOT RUN` | 没有修改或重启 guest runtime |
| device_response/data_behavior | `NOT RUN` | 本轮不是外设或固件功能验证 |
| visual_or_physical | `NOT RUN` | 没有真机、RF、电气或光学测量 |
| delivery | `PASS` | product commit `5f68d70`；CI `40237507431` 两 job PASS |

## 生成事实

- catalog date：`2026-10-25`；
- fact date：`2026-10-26`；
- latest evidence：`2026-10-26`；
- Markdown 页面：`216`；
- 权威页旧日期：`0`；
- 委派页旧日期：`0`；
- 平台测试：`510`。

## 验证边界

- 文档审计只证明入口链接、日期和机器契约一致，不证明每个历史 evidence
  都在当前 runtime 上重新执行；
- `0036` 仍是最后一次完整 UIFlow2 矩阵基线；
- `0038` 之后的 Core2 回归是 `6/6` 定向组，不是完整 `67-case`；
- `RUNTIME-03`、物理 cache/PSRAM、bit-exact controller 和真机仍未关闭；
- 所有虚拟设备相关结论仍只属于 `virtual-device validation`。

## 风险与回滚

没有设备写入、持久迁移或不可逆操作。回滚 product commit
`5f68d70f51f39eef82113f6836843ef5b996ef23` 可恢复到上一版文档与快照生成器；
回滚后仍需运行原平台测试，因为新增的快照日期/幂等契约也会随 commit 撤回。
