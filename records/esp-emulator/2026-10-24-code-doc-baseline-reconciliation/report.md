# ESP Emulator 当前基线、代码地图与验证元数据收口报告

## 背景

项目在 `2026-10-23` 至 `2026-10-24` 连续完成 S3/C6/Core2 unified runtime、
网络 namespace/egress、worker queue/executor/reattach、FirmwareManifest
文件系统与许可策略，以及 Core2 native-HCI 多轮门禁。功能实现能由源码和
evidence 证明，但动态数字与状态被复制到 README、导航页、工作流台账和多个
设备页面，后续提交很容易只更新其中一处。

用户要求完整整理代码和文档，并梳理当前工作与待办。目标是让：

- 当前能力只有一个权威入口；
- 历史结果只进入按日期证据台账；
- 未完成工作只进入 Backlog；
- 设备 catalog 与 QEMU profile 不再各自保留冲突的验证日期/状态；
- 后续 Agent 能直接看到真实代码债务，而不把“文档整理”当成功能完成。

## 结论

文档、契约、回归入口和交付层为 `PASS`。本轮没有新增设备能力，也没有修改
QEMU、固件或 Device Service 运行时数据面。

### 单一事实源

- `docs/project-status.md` 维护动态平台测试数、全矩阵结果、当前能力和风险；
- `docs/validation-ledger.md` 只追加带日期的历史快照；
- `docs/project-backlog.md` 只保留未完成 Task、依赖和验收条件；
- `docs/workstreams.md` 维护工作流、代码/证据入口和下一 Task ID；
- `README.md` 与 `docs/README.md` 不再复制会随每次提交变化的计数。

文档一致性测试现在还会拒绝在 README、导航页或工作流台账重复平台测试总数。

### 设备与 QEMU 元数据

新增 `QEMU profile ↔ device catalog` 交叉校验，要求同一设备的验证日期与状态
一致。校验立即发现两个旧值：

1. AtomS3R QEMU profile 仍为 `2026-10-20`，设备 catalog 和 unified 实现已是
   `2026-10-23`；
2. PaperMono QEMU profile 仍为 `display-input-peripherals-wifi-ble-pass`，
   设备 catalog 与触摸能力已是
   `display-touch-peripherals-wifi-ble-pass`。

两项已修正，今后任何一侧漂移都会让平台测试失败。

同时更新了设备说明：

- Tab5 运行时是 `reference-ready`，但外设仍是 `partial`；
- `backend-required` 仅表示 CardputerZero 使用独立固件族/后端，不表示后端仍
  缺失；CardputerZero 整体完成度仍是 `PARTIAL`；
- 设备生成器会继续生成每个型号的 README/JSON，避免手写档案与源 catalog
  分叉。

### 代码组织

`platform/tools/generate_catalog.py` 的 `backend-required` 说明改为能力分类，
不再暗示“后端尚未实现”。

代码地图移除了容易过期的精确行数，改为数量级，并记录三项主要维护债务：

- `device_service.py` 仍是 lease、存储、runtime、证据和生命周期的编排热区；
- `test_device_service.py` 仍是大型 service 契约测试；
- `test_docs_consistency.py` 同时包含导航、链接、API、网络、Core2 和 evidence
  断言，后续应按职责拆分。

本轮没有为了“整理”执行高风险的跨文件大搬家。`SVC-03` 仍要求先锁定
`/api/v1`、session JSON、evidence ZIP 和 stopped-session 恢复契约，再逐个迁移
边界。

## 当前工作与待办

| 工作流 | 已形成边界 | 仍开放 |
| --- | --- | --- |
| 网络与 Worker | namespace、controlled DNS、TLS/Host、exact IPv4、pcap、双 guest fabric、目录、队列、executor、HMAC、本地 QEMU/QMP reattach | `NET-04` 跨主机与 continuity；`NET-05` IPv6 |
| 固件审查 | Manifest、WebBurner、LittleFS/FAT/SPIFFS、静态审查、SBOM、声明级许可策略 | `FW-01` 运行时权限/完整许可；`FW-02` 真机 key/eFuse；`FW-03` 跨厂商 |
| Core2 | OpenMAC WiFi、公网、native-HCI、HLI/GATT、`HCI-4`、两批 `5×10s`、`3×60s` | `CORE2-02` 多小时 soak、重连、coexistence、bit-exact controller 与物理等价性 |
| Device Service | lease、历史、GC、worker queue/executor、本地 restart reattach | `SVC-01` 跨主机接管；`SVC-02` warm pool/多机；`SVC-03` 编排拆分 |
| 专项设备 | Tab5 可启动/显示/触摸/RS-485；CardputerZero 独立 Linux 子路径 | `TAB5-01`、`CZ-01`、`UI-01` |
| 真机 | 当前只有 virtual-device evidence | `HW-01` 同固件 SHA、同测试计划 |

## 执行

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
Ran 297 tests in 10.455s
OK

python3 platform/tools/runtime_coverage.py --check
RUNTIME_COVERAGE_OK

python3 platform/tools/peripheral_catalog.py --check
PERIPHERAL_CATALOG_OK

python3 platform/tools/qemu_profiles.py --check
QEMU_PROFILES_OK

node platform/tests/test_sha256.mjs
SHA256_OK

node platform/tests/test_firmware_upload.mjs
FIRMWARE_UPLOAD_OK

ruff check platform/tools/generate_catalog.py \
  platform/tests/test_qemu_profiles.py \
  platform/tests/test_docs_consistency.py
All checks passed!

git diff --check
PASS
```

GitHub Actions `40061751714` 对 head
`730123da116ece1acbd97744de419e97596f0232` 全部成功：

- `platform-contracts`：success；
- `network-namespace-policy`：success。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、Python 契约测试、Ruff |
| review | `PASS` | 文档索引、链接、API、动态计数单一事实源和 catalog/profile 交叉校验 |
| delivery | `PASS` | 源码提交、GitHub 推送和 CI |
| transport | `NOT RUN` | 未修改 UART/I2C/SPI/USB 数据面 |
| device_response | `NOT RUN` | 本轮没有启动新的设备 session |
| data_behavior | `NOT RUN` | 未修改运行时数据面 |
| visual_or_physical | `NOT RUN` | 未做画面或物理设备验证 |

## 验证边界

- 既有 UIFlow2 `67/67` cases、`274/274` checks 仍是历史 evidence，本轮未重跑；
- 同推送范围中的 Core2 `3×60s` hold 是既有 virtual-device evidence，本轮未
  重新执行；
- Core2 多小时 soak、bit-exact BT controller/baseband、物理 cache/PSRAM、
  WiFi/BLE coexistence 和真机仍开放；
- 网络结果不是 RF、WPA2/WPA3、功耗或恶意固件 VM 隔离结论；
- Tab5、CardputerZero、视觉保真和真机验证仍未完成。

## 风险与回滚

主要风险是文档契约更严格：后续提交如果重新把动态计数复制到多个入口，或
让设备 catalog 与 QEMU profile 的验证元数据漂移，CI 会失败。

回滚源码提交 `730123da116ece1acbd97744de419e97596f0232` 可恢复旧 README、
文档入口、生成说明和测试；不会修改 QEMU build、固件、Device Service 历史、
网络策略或已有 evidence。本轮没有不可逆硬件操作。
