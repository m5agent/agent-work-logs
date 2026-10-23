# ESP Emulator 文档新鲜度与 Core2 HCI 阶段重整报告

## 背景

项目近期连续完成网络 namespace/egress、FirmwareManifest 文件系统与 eFuse
证据，以及 Core2 native-HCI transport/H2C capture。随后又完成 ELF 符号固定、
GDB repeated lease 失败取证的 QEMU native-HCI 设计。代码推进速度快于周边
文档，出现三个具体问题：

1. 多个入口仍把平台测试写成 `243/243 PASS`，但 CI 实际为
   `Ran 243 tests`、`OK (skipped=2)`；
2. Core2 文档混用了“GDB 诊断桥单 lease PASS”“HCI transport PASS”
   “首个 H2C capture PASS”和“完整 BLE backend”，容易把部分进展误读为完成；
3. docs 页面虽然大多有日期，但只有部分进入新鲜度台账，直接打开历史页或
   专项页时仍可能把旧计划当成当前状态。

目标是建立一份当前工作和待办的可追溯快照，并用自动化契约阻止旧状态重新
写回当前入口。

## 结论

源码 `main` 已推送 `53cefc14e909519baebf12784597c3274f72f1e4`。

### 状态分层

| 工作流 | 已形成边界 | 当前待做 |
| --- | --- | --- |
| 网络 | namespace、controlled DNS、TLS/Host、exact IPv4 egress、pcap、错误密码、radio/AP 恢复、DHCP renewal | `NET-03` 双设备 fabric、`NET-04` worker、`NET-05` 外部 IPv6 |
| Core2 | deterministic TCG/icount、WiFi/DNS/公网、GDB native-VHCI 单 lease、HCI-1 transport、HCI-2 首包 | `HCI-3` C2H guest delivery、`HCI-4` 无 GDB Device Service `5/5`、物理与 bit-exact 边界 |
| 固件 | FirmwareManifest、WebBurner/M5Burner/ESP-IDF、capability mismatch、eFuse 分层、LittleFS/FAT | `FW-01` SPIFFS/权限/许可、`FW-02` 真机 key/eFuse、`FW-03` 跨厂商、`FW-04` 流式上传 |

### Core2 native-HCI

| 阶段 | 状态 | 结论 |
| --- | --- | --- |
| `HCI-1` host transport | `PASS` | H4 framing、bounded queue、overflow、peer lifecycle、QOM counters、clean shutdown |
| `HCI-2` H2C | `PARTIAL` | 不启动 GDB 捕获 stock Reset `01030c00`；完整 sequence 等待 C2H |
| `HCI-3` C2H | `OPEN` | 尚无已提交实现；`vhci_send` 直接注入假设失败 |
| `HCI-4` stability | `OPEN` | 尚无无 GDB Device Service repeated lease `5/5` |

本地 C2H 实验曾进入 guest `vhci_send` 并让函数返回，但 guest 随后报告
`HCI wait for ack returned 19` 和 `OSError: ETIMEDOUT`。该实验没有固化为
源码提交。结论是 `vhci_send` 不是简单 `(H4 buffer, length)` 入口，后续
必须从匹配 ELF、VHCI 运行时结构和真实 controller-to-host 通知/队列确定
ABI，而不是继续猜寄存器参数。

## 改动范围

- `docs/README.md`：增加证据快照、三组 P0 位置和全部 docs 的新鲜度台账；
- `docs/project-status.md`、`docs/workstreams.md`、`docs/project-backlog.md`：
  对齐当前状态、执行顺序和 Core2 HCI 阶段；
- `docs/core2-native-hci-backend.md`：记录已排除的 `vhci_send` 假设和下一
  最小实验；
- `docs/code-map.md`、QEMU 矩阵、unified runtime、UIFlow2 runner README：
  增加 HCI-1/HCI-2 入口并明确 HCI-3/HCI-4 未完成；
- `AGENTS.md`、`platform/README.md`：同步当前维护边界；
- 历史页补充固定日期和替代入口；
- `platform/tests/test_docs_consistency.py`：
  - 每个 `docs/**/*.md` 必须进入新鲜度台账；
  - 每个台账行必须有最近核对日期；
  - `plans/` 页面的相对链接也纳入检查；
  - 禁止 `243/243` 和 `guest VHCI 未接入` 等旧陈述回写；
  - 当前状态必须包含 HCI-1 至 HCI-4 与 `01030c00`。

## 执行与证据

本机：

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
Ran 243 tests in 8.317s
OK

runtime_coverage.py --check       RUNTIME_COVERAGE_OK
peripheral_catalog.py --check     PERIPHERAL_CATALOG_OK
qemu_profiles.py --check          QEMU_PROFILES_OK
compileall                        PASS
git diff --check                  PASS
```

GitHub Actions `40012704195`：

```text
platform-contracts   success
network-namespace-policy   success
Ran 243 tests
OK (skipped=2)
```

说明：macOS 本机完整执行 243 项；Ubuntu CI 的 2 项按环境条件跳过。
文档不再把测试总数写成全部通过数。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall 和平台测试完整导入/执行 |
| review | `PASS` | 文档索引、日期、链接、API、任务和旧状态契约 |
| delivery | `PASS` | 源码提交、远端推送、GitHub Actions 成功 |
| device_response | `NOT RUN` | 本次未启动新设备会话 |
| data_behavior | `NOT RUN` | 本次未改运行数据面 |
| visual_or_physical | `NOT RUN` | 本次未做画面或物理设备验证 |

## 验证边界

- 既有 67/67 case、274/274 check 仍有效，但本次没有重跑；
- C2H、完整 H2C、外部 GATT 和 repeated lease 仍未完成；
- 物理 cache/PSRAM、BT controller/baseband、RF、功耗、声学和光学仍为
  `NOT RUN`；
- 本次是 virtual/static evidence inventory，不产生新的设备功能 PASS。

## 风险与回滚

主要风险是文档门禁更严格：新增 `docs/**/*.md` 必须同时登记新鲜度和复核
日期，历史结论不能重新出现在当前入口。该约束是预期行为。

回滚源码提交 `53cefc14e909519baebf12784597c3274f72f1e4` 可恢复旧文档和
测试门禁，不会改变 QEMU build、固件、Device Service 历史或已有 evidence。
