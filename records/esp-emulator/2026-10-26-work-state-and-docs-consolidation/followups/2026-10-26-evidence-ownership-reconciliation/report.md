# ESP Emulator evidence-ownership reconciliation report

## 背景

- 来源：
  [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- 需求：完整整理代码和文档，说明当前工作与待办，并消除近期 Core2 纠错、
  network/worker、固件审查和能力矩阵工作之后仍存在的旧阶段表述。
- 目标：让每个页面只维护一种事实，避免同一组运行数字散落在 README、
  状态页、Backlog、机器 profile、代码地图和测试中。

## 结论

整理后的职责如下：

- `project-status.md`：当前稳定能力、风险、证据层级和不可继承边界；
- `project-backlog.md`：未完成 Task、依赖、下一项最小交付和验收；
- `validation-ledger.md` / evidence：日期化轮次、PASS 比例、资源和哈希；
- `project-snapshot.md`：从 catalog/profile/evidence/Backlog 生成的动态计数；
- `engineering-handoff.md` / `workstreams.md`：代码阅读顺序和工作流路由；
- `code-map.md`：源码、测试和 evidence 的入口索引；
- 日期较早的专题页：保留历史，不反向定义当前能力。

最新 Core2 纠错后的上层口径统一为：普通 partition-read 数据面已经执行，
但 flash 活动后的 interrupt-WDT 仍可复现；精确 `14 PASS / 6 interrupt-WDT`
等结果只保留在验证台账和 evidence，不在 README、状态页、Backlog、交接页、
工作流页、QEMU 矩阵或代码地图复制。

## 改动范围

- 根 README、项目状态、Backlog、工程交接、工作流、QEMU 适配矩阵和代码地图
  删除易漂移的运行比例与批次流水；
- `platform/README` 压缩 Core2 历史 PASS 序列，只保留产品路径、当前边界和
  台账/专题链接；
- `platform/qemu/profiles.json` 的 Core2 blocker 改成长稳、容量、controller
  和物理边界，不再把并发批次通过率放进生成快照；
- `docs/README` 新增事实维护规则，并要求量化证据链接到台账；
- Core2 文档契约禁止 probe 比例重新进入上层页面；
- QEMU profile 契约继续验证机器可读的详细 validation 历史，同时要求
  blocker 保持稳定的用户可见边界；
- 重新生成 `project-snapshot.md`。

本次没有改动运行时代码、QEMU 补丁、Device Service 状态机或固件 artifact。

## 执行环境

- macOS arm64；
- Python `3.13.15`；
- 工作目录：公开 `m5stack-esp-emulator` 仓库；
- 无 QEMU guest、Device Service session、物理设备、RF 或电气测量。

主要命令：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_docs_*.py'

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_qemu_profiles.py'

python3 -m compileall -q platform/tools platform/tests
ruff check platform/tools platform/tests --select E9,F
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
git diff --check
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、Ruff `E9/F` 和 diff check |
| documentation contract | `PASS` | docs `40/40`；snapshot/coverage/catalog/profile |
| platform contract | `PASS` | platform `500/500` |
| QEMU profile contract | `PASS` | `19/19` |
| firmware/QEMU functional | `NOT RUN` | 本轮只整理入口、机器配置与文档 |
| device_response/data_behavior | `NOT RUN` | 未启动 guest |
| visual_or_physical | `NOT RUN` | 无显示、RF、电气或真机 |
| delivery | `PASS` | product commit `1b923f8`；CI `40214948602` 两个 job PASS |

## 验证边界

本轮证明文档契约、机器 profile 结构、项目快照和平台契约一致，不证明新的
固件行为。Core2 legacy UIFlow 非空帧、post-flash interrupt-WDT 根因、
`Core2FactoryTest`、持久吞吐、物理 PSRAM/cache、bit-exact controller、
RF 与真机均未覆盖。

## 风险与回滚

没有不可逆设备操作、烧录、生产配置或持久状态迁移。需要回滚时 revert
`1b923f83d6906545879e16262aaa3b3e10cc7c74`，即可恢复上一版文档和 profile
blocker；该提交不改变运行时行为，因此不会迁移 Flash、session、worker 或
evidence。
