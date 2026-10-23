# ESP Emulator 代码地图、文档与当前队列重整报告

## 背景

项目在短时间内连续完成网络 namespace/egress、WebBurner 浏览器导入、
FirmwareManifest 文件系统与安全证据、Core2 deterministic scheduling、
native-VHCI 服务路径和 QEMU native-HCI 诊断。代码推进后，当前事实仍可
从测试和 evidence 得出，但多个文档入口混入了旧阶段结论：

1. 最新 `HCI-3b` 审计只进入专题页，状态页和工作队列仍写成“继续稳定”；
2. `AGENTS.md` 仍把已经完成的流式上传列为后续工作；
3. Device Center 文档仍要求等待进程级执行器，而 `/api/v1` lease 已交付；
4. Cardputer-ADV CC1101 已通过，但外设矩阵仍写“未来”；
5. DNS/UDP 探针仍写“未来才有 controlled DNS”，实际 Linux namespace
   fixture 已完成 A/NXDOMAIN 验证。

目标是让外部读者和后续 Agent 能从最多五个入口准确回答：

- 现在能做什么；
- 最新证据是什么；
- 哪些失败实验已经排除；
- 下一步最小交付是什么；
- 哪些验证没有执行。

## 结论

源码 `main` 已推送 `72c2b8d59edc0f446fb35809d4c8e73c818dd9f5`。本次结论是
文档、契约和回归入口层的 `PASS`，不新增设备功能 PASS。

### 状态与文档职责

- `docs/project-status.md`：项目级当前能力和证据快照；
- `docs/workstreams.md`：工作流级交付、证据入口和下一步；
- `docs/project-backlog.md`：只保留未完成工作与验收条件；
- `docs/code-map.md`：代码、测试、证据和计划拆分边界；
- `docs/README.md`：分类、新鲜度和禁止重复维护可变事实的规则。

历史调查继续保留自己的日期，不静默改写为“当时已经知道后续结论”。

### Core2 native HCI

| 阶段 | 状态 | 当前边界 |
| --- | --- | --- |
| `HCI-1` transport | `PASS` | H4 framing、bounded queue、overflow、peer lifecycle、counters、clean shutdown |
| `HCI-2` H2C | `PARTIAL` | 无 GDB 捕获 stock Reset `01030c00`；完整命令序列依赖 C2H |
| `HCI-3a` C2H callback | `PASS` | Reset Complete 交付后 guest 继续发命令，targeted `5/5` |
| `HCI-3b` complete sequence | `FAIL` / `OPEN` | 连接和首个 ATT 交互通过；第二个 ATT request 后 ack 12 并 Reset |
| `HCI-4` stability | `OPEN` | 尚无无 GDB Device Service repeated lease `5/5` |

`HCI-3b` 的两个后续审计已经改变实现方向：

- 保存和恢复常用 Xtensa caller-saved 特殊寄存器后，在任意 CPU0 safe point
  注入 callback 仍导致 ack 12 和 `LoadProhibited`；
- 把 firmware 真实 `r_eif_send -> vhci_send` 当成 nested guest RPC 调用，
  触发 `Cache disabled but cached memory region accessed`；
- 两个实验都没有保留在源码中，QEMU 补丁 reverse-check 为 `PASS`。

下一步必须实现 guest-visible controller-to-host 数据/状态队列和 IRQ，让 guest
firmware 自己的 ISR/worker 消费；或实现带明确 transaction 的 in-process
controller。不能继续靠 sleep、CPU pinning、寄存器补丁或 retry。

### 代码组织

当前主要结构：

| 代码面 | 入口 | 当前职责 |
| --- | --- | --- |
| Device Service | `platform/tools/device_service.py`、`serve.py` | lease、固件存储、runtime、证据和生命周期 |
| 固件 | `firmware_manifest.py`、`firmware_analysis.py`、`firmware_filesystems.py`、`firmware_static_review.py` | 导入、能力检查、文件系统和脱敏审查 |
| 网络 | `network_sandbox.py`、`network_egress.py`、`network_policy.py` | namespace、DNS/TLS/IP-port policy 和清理 |
| 设备契约 | `devices/`、`platform/peripherals/`、`platform/qemu/` | 硬件需求、模型覆盖和 runtime profile |
| 回归 | `platform/tests/`、`tests/uiflow2/`、`tests/network/`、`tests/firmware/` | 契约、设备数据面、网络和固件证据 |

`device_service.py` 仍是编排热区。`SVC-03` 的拆分顺序固定为：

1. firmware/artifact store 与 resumable upload；
2. session repository、状态机和历史恢复；
3. QEMU、esp-emu/Tab5、network runtime adapters；
4. serial/frame/QOM/audio/network evidence collector；
5. HTTP handler 与 orchestration facade。

每个变更只迁移一个边界，并先保留现有 API、session JSON、evidence ZIP 和
历史恢复契约。本轮没有为了“整理”做一次无语义的大规模移动。

### 当前执行队列

| 工作流 | 已形成边界 | 下一步 |
| --- | --- | --- |
| 网络 | namespace、controlled DNS、TLS、exact IPv4 egress、pcap、错误密码、radio/AP 恢复、DHCP renewal、Linux policy CI | `NET-03` 双设备 fabric，随后 `NET-04` worker、`NET-05` IPv6 |
| Core2 | deterministic TCG/icount、WiFi/公网、HCI-offload、GDB native-VHCI、HCI-1/HCI-2/HCI-3a | `HCI-3b` IRQ/queue 或 in-process controller，随后 `HCI-4`、`CORE2-02` |
| 固件 | Manifest、WebBurner、chunk upload、capability/security、SBOM、LittleFS/FAT | `FW-01`、`FW-02`、`FW-03` |
| 服务 | 本地 lease、历史、存储 GC、network/evidence | `SVC-01`、`SVC-02`、`SVC-03` |
| 专项 | Tab5 partial、CardputerZero partial、视觉保真 backlog | `TAB5-01`、`CZ-01`、`UI-01` |
| 真机 | 虚拟设备证据为主 | `HW-01` 同固件 SHA、同测试计划 |

## 改动范围

- 更新状态页、工作流页、Backlog 和代码地图中的 Core2 最新边界；
- 更新 native-HCI 设计、unified runtime、network plan 和 platform 入口；
- 更新 Device Center 接入契约和“已接入/仍开放”清单；
- 清理 `AGENTS.md`、DNS/UDP fixture、CC1101 和功能测试日期旧描述；
- 在 `test_docs_consistency.py` 增加最新审计和旧陈述回归检查；
- 18 files changed，173 insertions，64 deletions。

## 执行与证据

本机：

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
Ran 253 tests in 8.880s
OK

PYTHONPATH=platform/tools python3 platform/tests/test_docs_consistency.py -v
Ran 9 tests
OK

runtime_coverage.py --check       RUNTIME_COVERAGE_OK
peripheral_catalog.py --check     PERIPHERAL_CATALOG_OK
qemu_profiles.py --check          QEMU_PROFILES_OK
compileall                        PASS
git diff --check                  PASS
```

GitHub Actions `40027623120`：

```text
platform-contracts          success
network-namespace-policy    success
Ran 253 tests
OK (skipped=2)
SHA256_OK
FIRMWARE_UPLOAD_OK
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall、平台导入和 CI |
| review | `PASS` | 文档索引、日期、链接、API、Task 和旧陈述契约 |
| delivery | `PASS` | 源码提交、远端推送和 CI |
| transport | `NOT RUN` | 没有修改 UART/I2C/SPI/USB 数据面 |
| device_response | `NOT RUN` | 本次没有启动新的设备会话 |
| data_behavior | `NOT RUN` | 没有修改运行时数据面 |
| visual_or_physical | `NOT RUN` | 没有画面或物理设备验证 |

## 验证边界

- 既有 `67/67` cases、`274/274` checks 仍作为历史 evidence，本次没有重跑；
- Core2 `HCI-3b` 仍为诊断 `FAIL`，`HCI-4` 仍开放；
- 物理 cache/PSRAM、BT controller/baseband、RF、功耗、声学和光学仍是
  `NOT RUN`；
- 本项目 PASS 仅表示文档与契约已经和当前代码/evidence 对齐，不表示新固件
  或新设备功能通过。

## 风险与回滚

主要风险是文档门禁更严格：后续修改如果继续把已完成能力写成未来工作，或把
Core2 safe-point/nested-entry 方案写回当前队列，测试会失败。

回滚源码提交 `72c2b8d59edc0f446fb35809d4c8e73c818dd9f5` 可恢复旧文档和
文档测试；不会修改 QEMU build、固件、网络策略、Device Service 历史或已有
evidence。本次没有不可逆硬件操作。
