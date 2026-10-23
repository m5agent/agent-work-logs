# ESP Emulator 工作流台账与代码维护边界重整报告

## 背景

项目在 2026-10-23 至 2026-10-24 连续完成 unified runtime、Core2
stock native-VHCI、网络 namespace/DNS/TLS/egress/pcap/DHCP renewal、
FirmwareManifest 静态审查以及 LittleFS/FAT 文件系统清单。主入口虽然做过
一次状态对账，但后续提交又产生了新的时间差：

1. 平台说明仍把任意公网 IP/端口 allowlist 整体列为未实现；
2. 服务路线图仍把 generic allowlist 当作单一待办，未区分已完成的 exact IPv4
   和仍开放的外部 IPv6/CIDR；
3. 固件审查页仍从“文件系统提取”开始列下一步，没有反映 LittleFS/FAT 已通；
4. 代码地图只列少数热路径，没有覆盖全部平台工具，也没有记录明显的单文件
   维护债务。

目标不是再写一份新的状态页，而是建立一份按工作流组织的可检查台账，并让后续
代码/任务变化必须同步文档索引。

## 结论

新增 `docs/workstreams.md`，以 12 条工作流统一记录：

- 当前状态和验证层级；
- 代码/契约入口；
- 验证与 evidence 入口；
- 未完成 Backlog Task ID；
- 当前执行顺序和证据读取规则。

同时：

- 把 `docs/workstreams.md` 加入 README、文档导航和当前状态页；
- 在 Backlog 增加 `SVC-03`，明确 Device Service 的拆分边界与验收；
- 在代码地图登记全部 `platform/tools/*.py`、测试入口和四个组织热点；
- 修正平台 README、服务架构、固件审查工作流和 QEMU 适配矩阵中的过期说明；
- 扩展文档契约测试，自动检查工具清单和 Backlog Task ID 的索引完整性。

## 代码结构判断

本次盘点发现的主要维护成本：

| 位置 | 规模 | 判断 |
| --- | --- | --- |
| `platform/tools/device_service.py` | 约 6700 行 | 会话、存储、runtime、网络、证据和历史职责过多，登记 `SVC-03` |
| `platform/tests/test_device_service.py` | 约 3500 行 | 跟随 service 分拆，不在无语义变化时先做大改名 |
| `tests/uiflow2/run_peripheral_matrix.py` | 约 2900 行 | case registry、注入与断言可拆，设备 probe 保留本地证据 |
| `tests/uiflow2/unified_*/` | 12 个相似外壳 | 可抽 transport/evidence helper，不能用万能 probe 吞掉设备差异 |

这些是维护债务，不是当前功能失败。没有 API/evidence 契约保护时不做跨文件
大重构。

## 改动范围

源码提交：

```text
https://github.com/m5agent/m5stack-esp-emulator/commit/3403287
```

主要改动：

- `docs/workstreams.md`：新增工作流总台账；
- `docs/code-map.md`：完整平台工具、测试入口和组织债务；
- `docs/project-backlog.md`：新增 `SVC-03`；
- `README.md`、`docs/README.md`、`docs/project-status.md`：更新阅读入口和测试快照；
- `platform/README.md`、`docs/simulator-service-architecture.md`：修正 egress 与
  DHCP renewal 状态；
- `docs/firmware-review-and-simulation-workflow.md`：修正 LittleFS/FAT 状态；
- `docs/qemu-device-adaptation-matrix.md`：区分板级验收与全矩阵回归日期；
- `platform/tests/test_docs_consistency.py`：新增工具/Task ID 一致性门禁。

## 执行

环境：

- macOS Apple Silicon；
- Python 3；
- 复用仓内已有 QEMU、Tab5、网络和固件 evidence；
- 不执行物理设备操作。

命令：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
git diff --check
```

结果：

```text
platform tests     236/236 PASS
runtime coverage   PASS
peripheral catalog PASS
QEMU profiles      PASS
catalog generation 14 devices
git diff check     PASS
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python 测试套件完整导入并执行 |
| delivery | `PASS` | 源码提交与远端推送完成 |
| review | `PASS` | 工具、测试、任务和旧状态契约检查通过 |
| device_response | `NOT RUN` | 本次未启动新设备会话 |
| data_behavior | `NOT RUN` | 本次未改运行数据面 |
| visual_or_physical | `NOT RUN` | 本次无画面或物理设备验证 |

## 验证边界

- 本次不新增设备功能 evidence；
- 最新 67/67 case、274/274 check 仍引用既有 evidence；
- 不验证真实 AP 丢失、双设备 fabric、IPv6、Core2 无 GDB 后端或 Tab5 缺失外设；
- 物理硬件、RF、功耗、声学、光学和机械结论仍为 `NOT RUN`。

## 风险与回滚

风险集中在文档门禁过严：新增平台工具或 Backlog Task ID 时必须同步索引。
这是预期维护约束。

回滚源码提交 `3403287` 可恢复旧文档和文档测试，不会改变 runtime、固件、
Device Service 历史或物理设备。`SVC-03` 是后续拆分计划，没有在本次执行。
