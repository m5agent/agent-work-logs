# ESP Emulator current-work and documentation consolidation report

## 背景

- 来源：
  [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- 需求：完整整理代码与文档，说明当前已完成工作、正在调查的问题和后续
  TODO；用户指出多份文档仍像旧阶段快照，没有结合近期 Core2 与网络/worker
  工作。
- 目标：把“当前能力”“调查假设”“待办依赖”“日期化证据”和“历史专题”
  分开，并为后续代码拆分建立不会破坏 evidence 的边界。

## 结论

- 根 README、工程交接、当前状态、Backlog、工作流和 QEMU 适配矩阵不再复制
  易漂移的 PASS 比例、轮次、RSS 或 SHA，统一链接验证台账/evidence；
- Backlog 新增立即可做、多机环境、真机/授权、后端阻塞和并行/串行关系；
- `RUNTIME-03` 记录当前调查假设：legacy UIFlow 启动期
  `spi_flash_disable_interrupts_caches_and_other_cpu()`、跨核 IPC 与
  DPORT high-interrupt 交接可能未完整复现；S32C1I 锁在采样时为空闲，
  因此锁泄漏不是首要假设；该判断仍为 `REVIEW/假设`，不是根因；
- Core2 GDB/VHCI lane 统一标记 historical/diagnostic；
- `SVC-03` 明确拆分顺序和 evidence-hash 门禁：代码改动必须配套重跑绑定
  该文件哈希的 evidence；
- 用例 README 的新鲜度规则现在明确：`Status: PASS` 只描述该用例最后一次
  evidence，不是产品总状态。

## 代码审计

生产代码没有零散的 `TODO/FIXME/HACK`。主要结构债务集中在
`platform/tools/device_service.py`：

- 设备规格、请求解析、artifact/firmware store、QEMU/esp-emu session、
  evidence 和 HTTP orchestration 同居一个模块；
- Core2 并发 evidence 绑定 `device_service.py` 当前 tool SHA；
- 因此本轮没有提交仅“看起来更整齐”的文件移动，因为那会让旧 evidence
  与新源码失配。

推荐拆分顺序已经写入 `docs/code-map.md` 和 `docs/project-backlog.md`：
先锁 `/api/v1`、session JSON、evidence ZIP、历史恢复和公开符号，再依次提取
无状态配置/解析、store、session repository、runtime adapter、evidence
collector 和 orchestration facade。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、Node unit/UI smoke、selected Ruff、diff check |
| documentation contract | `PASS` | 39/39 docs tests；snapshot、coverage、catalog、profile checks |
| platform contract | `PASS` | 499/499 platform tests |
| firmware/QEMU functional | `NOT RUN` | 本任务只重组文档与契约，没有启动 QEMU guest |
| device_response/data_behavior | `NOT RUN` | 未执行 guest 功能路径 |
| visual_or_physical | `NOT RUN` | 无显示、RF、电气或真机验证 |
| delivery | `PASS` | 产品 commit `ad1d878`；CI `40210161366` 的 `platform-contracts` 与 `network-namespace-policy` 均成功 |

## 重点文件

- `README.md`
- `docs/engineering-handoff.md`
- `docs/project-status.md`
- `docs/project-backlog.md`
- `docs/workstreams.md`
- `docs/runtime-model-gap-register.md`
- `docs/qemu-device-adaptation-matrix.md`
- `docs/network-simulation-plan.md`
- `docs/code-map.md`
- `tests/uiflow2/README.md`
- `tests/uiflow2/unified_core2/README.md`

## 验证边界

本次是 documentation/contract validation，不是 firmware/QEMU 功能重跑。
`RUNTIME-03` 的 flash-cache/IPC/DPORT 结论仍为工作假设；应用帧、WDT
根因、Core2FactoryTest、物理 PSRAM/cache、bit-exact controller、RF 与真机
均未覆盖。

## 风险与回滚

没有不可逆设备操作、烧录、生产配置或持久状态迁移。需要回滚时 revert
`ad1d878d73af0d8b99e2a47809414f671c432bf3` 即可恢复上一版文档结构和契约；
该提交不改变运行时代码，因此不会迁移 Flash、session、worker 或 evidence。
