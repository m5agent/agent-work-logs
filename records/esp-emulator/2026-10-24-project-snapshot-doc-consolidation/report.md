# ESP Emulator 项目快照与文档结构收敛报告

## 背景

- 来源：用户要求完整整理代码和文档，并指出多份文档与后续工作脱节；
- 目标：让“当前事实、自动计数、未完成 Task、契约和历史页”各自只有清晰
  的权威入口，并把仍像旧计划的已完成 bring-up 内容标成历史；
- 约束：不改 QEMU 数据面，不把文档检查通过描述成固件、设备或真机 PASS。

## 审核发现

1. `README.md`、`workstreams.md`、`unified-device-runtime.md`、
   `network-simulation-plan.md` 和 `qemu-device-adaptation-matrix.md` 都在
   复制 Core2、网络或固件矩阵的动态计数。任何里程碑都需要手工同步多页，
   容易再次漂移。
2. `workstreams.md` 和 `unified-device-runtime.md` 混有大量历史证据说明，
   使“工作流导航”和“稳定契约”承担了当前状态页的职责。
3. 适配矩阵保留早期五批 bring-up 文案，容易让读者误以为这些设备仍在等待
   首次接入。
4. Backlog `FW-03` 仍写 S3/C6 `6` 台、`18` 样本；`tests/firmware/README.md`
   同样只描述旧快照。合并后的公开样本 evidence 实际已覆盖 `7` 台、`21` 个
   非基线样本：`10 PASS`、`11 PARTIAL`、`0 FAIL`。
5. 原有文档测试能拦截一批已知旧句子，但没有校验“当前项目快照是否与源
   catalog、profile、evidence 和 Backlog 一致”。

## 当前工作与待办快照

当前主路径：

- ESP32-S3/C6 与 Core2 的完整设备验收使用 `runtime=qemu-unified`，同一
  lease/guest 提供 board、WiFi、BLE 和 evidence；
- Core2 新调用使用 `core2-native-hci`，GDB `core2-native-vhci` 只用于诊断；
- Device Service 已具备 lease、烧录、serial/frame/input/QOM/network/evidence、
  durable worker queue、HTTPS/mTLS、credential rotation/drain 和本地 QEMU/QMP
  控制面 re-attach；
- 通用固件入口已覆盖 Manifest、WebBurner/M5Burner/ESP-IDF import、LittleFS/
  FAT/SPIFFS、脱敏静态审查、许可声明策略和公开固件运行时矩阵；
- Tab5 仍是 P4 backend 限制下的完整外设 `partial`；CardputerZero 是独立
  Linux ARM64 后端。

仍需完成：

- `NET-04`：worker 主机自动发现、跨主机 QEMU executor/reattach、
  companion/evidence continuity、跨主机 credential migration 和多机调度；
- `NET-05`：外部 IPv6 及 DNS/route/NAT/cleanup 同一证据链；
- `CORE2-02`：超过当前 120 轮 API 上限、两小时 coexistence/soak，
  之后处理 bit-exact BT controller/baseband 与物理 cache/PSRAM；
- `FW-01/02/03`：运行时资源权限、完整源码级许可/法律审批、真机
  secure boot/Flash Encryption/eFuse、更多设备与 firmware family；
- `RUNTIME-02/03/04`：C6 Zigbee commissioning、Core2 AXP PMIC I2C、
  Core2 for AWS ATECC608；
- `HW-01`：代表设备的同固件 SHA 真机验证；
- `TAB5-01`、`UI-01`、`CZ-01`：P4 backend、高保真外壳和 CardputerZero
  长期回归。

## 改动

- 新增 `platform/tools/project_snapshot.py`：
  - 读取设备 catalog、QEMU profile、peripheral status；
  - 读取 S3/C6 公开固件 historical evidence 与 Core2 扩展 evidence；
  - 解析 `RUNTIME-*` 状态和 Backlog Task 板；
  - 生成确定性的 `docs/project-snapshot.md`；
  - 提供 `--write`、`--json` 和 `--check`。
- `test_docs_consistency.py` 增加快照逐字节一致性检查，并要求快照包含设备数、
  Backlog Task 和 `CORE2-02`。
- README 保留入口、架构能力和边界，删除重复 PASS 计数与第二份执行顺序。
- 工作流页改为稳定代码面、权威状态入口和未完成 Task ID 的导航表。
- 统一运行时契约只保留单 lease、单 guest、单固件、单 evidence bundle 的
  不变量、状态语义、路由和边界，不再复制逐设备证据。
- 网络方案改为模式、测试矩阵和安全边界，具体结果链接状态页与证据台账。
- 适配矩阵改为稳定 SoC/backend/device 映射和 onboarding 规则；早期五批
  bring-up 明确标成历史。
- 修复 `FW-03` 和 firmware evidence 索引的 6/18 旧计数为 7/21。
- 文档导航新增“生成事实”页，并明确快照不替代人工结论和风险边界。

## 执行

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py' -v

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_docs_consistency.py' -v

ruff check platform/tools/project_snapshot.py \
  platform/tests/test_docs_consistency.py
python3 -m py_compile \
  platform/tools/project_snapshot.py \
  platform/tests/test_docs_consistency.py
```

结果：

- 平台套件 `324/324 PASS`；
- document contract `13/13 PASS`；
- runtime coverage、peripheral catalog、QEMU profile、snapshot check 均 PASS；
- Ruff 和 `py_compile` PASS；
- GitHub Actions run `40090485320` 的 `platform-contracts` 与
  `network-namespace-policy` 均 PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compile、Ruff、平台测试和生成物校验 |
| review | `PASS` | 文档职责、链接、API、设备与 Task 契约 |
| data_behavior | `NOT RUN` | 本任务未改 QEMU/controller |
| device_response | `NOT RUN` | 未启动新的 guest 功能测试 |
| visual_or_physical | `NOT RUN` | 未执行物理设备或视觉测量 |
| hardware | `NOT RUN` | 仅代码与文档验证 |

## 自动快照边界

自动快照回答“源文件和已提交 evidence 当前声明了什么”，不替代：

- `project-status.md` 对能力和风险的叙述；
- `validation-ledger.md` 的日期、检查项和 evidence 链；
- `project-backlog.md` 的依赖、验收和未完成判断；
- 对应固件 SHA、ELF、QEMU build 和 session 的实际运行证据。

生成器目前解析 Markdown 的 `### RUNTIME-*`、状态表和
`## 可执行任务板`。文档结构变更必须同步修改生成器与契约测试，避免正则
静默跳过 task。

## 风险与回滚

- 风险：自动快照的解析依赖稳定 Markdown 标题与四列表格；若格式漂移，
  `project_snapshot.py --check` 会使 CI 失败，而不是生成错误 PASS。
- 风险：快照中的平台测试数会随测试增删变化，源码变化后必须运行
  `--write`。
- 未修改运行时、QEMU patch、固件 artifact 或物理设备状态。
- 回滚可整体 revert：
  `a79166b68524948ef18480313e3ff3da98031901`。
