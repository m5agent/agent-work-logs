# ESP Emulator 当前 QEMU 三设备 UIFlow2 接口复测 r4 报告

## 背景

- 来源：用户要求在 StopWatch、StickS3 和 Core2 上再次并行复测可测的
  UIFlow2 接口，并统一收集、处理问题。
- 目标：检查当前 QEMU 是否引入接口回归，核对 stock SDK 缺陷是否保持，
  并验证 hash-pinned candidate 仍可修复相同固件路径。
- 约束：使用互相隔离的 Device Service `/api/v1` 可见会话；不占用用户
  测试服务；不把虚拟设备结论写成物理硬件结论。

## 结论

本轮在源码 `0769ae7c0136f81aa34d85a58588c67fd879fc19` 的文档提交前状态
和 QEMU `dd4b1b34…` 上完成三台设备复测。所有主报告实际加载的 runtime
哈希一致。没有发现由当前模拟器造成的稳定接口回归，也没有需要新增的
模拟器源码修复；结果提交为
`322130288ea4fb2c2aab49b689e232bb2beef7f7`。

现有 stock SDK 缺陷可稳定复现；相同 stock firmware 上加载 hash-pinned
candidate 后全部通过。StopWatch/StickS3 stock internal-controller GATT
仍是模型缺口，BLE client 角色仍未准入。Core2 stock BLE 仅在其
`core2-native-hci` + matching ELF 路径上通过。

## 控制实验

### Core2 radio backend 环境

Core2 网络 runtime 要求显式指定 `M5_CORE2_RADIO_QEMU`。缺少时统一 WiFi
profile 返回 `503 qemu_wifi_backend_unavailable`。补齐环境后，network
在三设备首轮并发中直接 `14/14 PASS`。该 503 保留为基础设施控制，不计为
固件或接口回归。

### TLS candidate UART bootstrap

- StopWatch candidate：默认 `dupterm` 下 `5/5 PASS`；使用 `native`
  bootstrap 时应用已启动，但 API probe 没有取得 UART REPL；
- StickS3 candidate：默认 `dupterm` 下 `boot.py` 触发
  `ESP_ERR_INVALID_STATE`；使用 `native` 后 `5/5 PASS`；
- Core2 candidate：默认路径直接 `5/5 PASS`。

这些差异是固件构建的 UART REPL 所有权，不是 TLS 数据面功能差异。

### M5UI candidate session

candidate M5UI 必须先以 `program_transport=uart-repl` 创建可见 base
session。缺少该声明时拒绝后续 `/program` 是预期准入行为；补齐后
StopWatch/Core2 均完成 `4/4 STATE_PASS + 2/2 FRAME_PASS`。

## 执行结果

| 范围 | StopWatch | StickS3 | Core2 |
| --- | ---: | ---: | ---: |
| System runtime | `50 PASS + 1 STATE_PASS` | 同左 | 同左 |
| Shared corrections | `7/7` | `7/7` | `7/7` |
| Sockets / MQTT / Network / EzData | `23 / 42 / 14 / 17` | 同左 | 同左 |
| EasySocket | `57 PASS + 1 N/A` | 同左 | 同左 |
| ESP-NOW | `12 PASS + 5 STATE_PASS + 1 CONFIGURED_UNVERIFIED` | 同左 | 同左 |
| Native ESP-NOW | `21 PASS + 21 STATE_PASS + 3 CONFIGURED_UNVERIFIED` | 同左 | 同左 |
| Audio player / recorder | `15/15`, `12/12` | 同左 | 模块未导出 |
| Hardware matrix | `115 CALL_OK + 66 API_ASSERTION_PASS + 1 OBSERVED` | 同左 | 同左 |

### Stock 与 candidate

- requests2：stock `15 PASS + 1 FAIL`，candidate 三台各 `2/2`；
- Modbus async：stock `42 PASS + 8 ERROR`，candidate 三台各 `50/50`；
- TLS：stock `3 STATE_PASS + 2 ERROR`，candidate 三台各 `5/5`；
- Core2 M5BLE：stock `21 PASS + 1 ERROR`，candidate `22/22`；
- M5UI：Stock 三失败是 triangle、float scale、integer step；
  candidate 两台均为 4 个状态和 2 个画面 oracle PASS；
- Core2 BLE NUS：`core2-native-hci` + matching ELF 为 `8/8 PASS`。

### 验证层级

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/static | PASS | `1432` platform tests、四个生成器检查、JSON、UTF-8 和 diff |
| transport | PASS（限定） | HTTP/TCP/UDP/MQTT/Modbus/TLS peers、BLE HCI、I2C/IR fixtures |
| device_response | PASS（限定） | guest 原库/API、serial marker、QOM、frame、PCM |
| data_behavior | PASS（限定） | 精确协议 payload、sensor readback、frame pixels |
| visual_or_physical | PARTIAL | 虚拟 frame/PCM 数据面通过；物理声学/光学/电气 NOT RUN |

## 修改范围

模拟器源码没有功能修改。新增了本轮证据页、摘要和当前状态/验证台账入口。
候选修复是既有 hash-pinned source lane，不覆盖 stock 固件结论。

首次文档 CI 仅因本地快照混入其他 agent 未提交的测试与源码行数而失败；
随后从已提交 HEAD 的干净 worktree 重新生成 snapshot，并修正平台测试数
`1432`，干净树全量平台测试 `OK`。该修正不改变功能结论。

## 验证边界

- StopWatch/StickS3 stock controller GATT 未通过，不能继承 Core2 native-HCI；
- 未验证 BLE pairing/security、RF、天线、共存、长期负载和 bit-exact controller；
- ESP-NOW 仅为同 guest controller loopback，不覆盖外部 peer、加密 payload、
  跨设备 fabric、loss/retry 或 RF；
- 未验证 Core2 legacy UIFlow normal-WDT 启动、setup/REPL 和非空应用帧；
- 未执行物理硬件、声学、光学、电气和物理 PSRAM/cache timing。

## 风险与回滚

本轮未执行不可逆硬件操作，也未改变默认参考固件或设备配置。源码仓库可回滚
文档提交 `322130288ea4fb2c2aab49b689e232bb2beef7f7`；测试运行态和完整 raw evidence 位于 ignored `.work/`，
不会进入 Git。
