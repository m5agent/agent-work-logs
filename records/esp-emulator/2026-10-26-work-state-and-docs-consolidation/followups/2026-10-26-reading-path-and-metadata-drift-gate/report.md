# ESP Emulator reading path and metadata drift report

## 背景

用户要求完整整理代码与文档，并指出部分页面仍像旧阶段快照，没有吸收后续
Core2、网络/worker、FirmwareManifest 和安全性工作。审计发现两个具体问题：

1. 当前入口虽然已有职责划分，但根 README 和 QEMU 矩阵仍重复大量 Core2
   排障过程，读者难以先看到整体完成项与待办；
2. `devices/catalog.source.json` 与 `platform/qemu/profiles.json` 都保存
   设备验证日期/状态，容易一处更新、另一处继续显示旧事实。

## 改动

### 文档阅读路径

- `docs/README.md` 新增“五分钟阅读顺序”和事实层级表；
- 明确页首日期表示维护者复核，不表示页内所有 evidence 都在当天重跑；
- `engineering-handoff.md` 与 `project-status.md` 新增网络、Core2、
  FirmwareManifest 三组目标盘点；
- `project-backlog.md` 单列“已完成，不再作为待办”，并说明局部完成不能扩大
  为 WPA3、RF、bit-exact controller、live eFuse 或真机 PASS；
- 根 README 和 QEMU 矩阵保留当前稳定结论，把细节路由到状态、Backlog、
  runtime gap、验证台账和 evidence。

### 设备验证元数据

- `devices/catalog.source.json` 的 catalog 日期推进到 `2026-10-26`；
- Core2 验证日期推进到 `2026-10-26`，摘要包含当前 eight-instance tool-hash
  rebind 与 legacy UIFlow late-loop 边界；
- AtomS3R、CoreS3、StickS3 的记录增加 WPA2-PSK 正确密码和 M2 MIC 错误密码
  拒绝路径；
- `generate_catalog.py` 重建全部派生设备 JSON 和 README；
- `project_snapshot.py --write` 重建 catalog、profile、文档和测试规模快照。

### Catalog/profile 漂移门禁

`platform/tools/qemu_profiles.py` 新增
`catalog_validation_errors(registry, source)`：

- 要求 profile 与 catalog 的 `generated_at` 一致；
- 对 QEMU/esp-emu 设备比较 `validation.date` 和 `validation.status`；
- catalog 缺少对应设备时返回明确错误；
- `--check` 现在自动加载 catalog 并执行上述校验。

`platform/tests/test_qemu_profiles.py` 增加反例，将
`generated_at` 和 Core2 日期改成旧值，确认检查返回两类 structured errors。

## 验证

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform/tools platform/tests tests
git diff --check
```

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| platform contract | `PASS` | `531/531` tests |
| profile contract | `PASS` | `20/20` tests，含漂移反例 |
| generated inventory | `PASS` | coverage/catalog/profile/snapshot checks |
| build | `PASS` | compileall |
| selected Ruff | `NOT RUN` | Python 环境没有安装 `ruff` module |
| firmware/QEMU functional | `NOT RUN` | 本任务只改文档、生成元数据和检查逻辑 |
| device_response/data_behavior | `NOT RUN` | 未启动 guest |
| visual_or_physical | `NOT RUN` | 没有真机、RF、电气或光学测量 |
| delivery | `PASS` | 产品 commit `e6c40e1`；CI `40247778027` 两个 job 均成功 |

完整平台测试已通过；最终记录中的 Ruff 状态不写成 PASS。

## 验证边界

- 本次没有重跑 Core2、网络、FirmwareManifest 或 UIFlow2 功能矩阵；
- 生成目录与快照通过只证明元数据和文档契约一致；
- `RUNTIME-03` 仍需 normal-WDT 非空应用帧和 matching ELF/MAP；
- `CORE2-02` 仍需物理 PSRAM/cache、bit-exact controller、更大规模、持续吞吐
  和其他 teardown；
- `NET-04` 仍需物理跨主机和完整 side-effect ownership；
- live eFuse、生产 key、运行态 ACL、真实云端业务和 hardware validation 均未
  覆盖。

## 风险与回滚

没有烧录、设备写入、凭据变更或持久状态迁移。回滚 product commit
`e6c40e13d4cc3a3aea81ca5f28ff542f7fa44438` 会恢复旧阅读路径和元数据；新增
漂移门禁也会随 commit 撤回。旧 evidence 不应删除或改写。
