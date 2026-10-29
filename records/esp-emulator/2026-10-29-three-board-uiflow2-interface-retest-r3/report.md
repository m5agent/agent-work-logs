# ESP Emulator 最新 QEMU 三设备 UIFlow2 接口复测报告

## 背景

- 来源：用户要求用最新模拟器在 StopWatch、StickS3 和 Core2 上再次并行
  复测可测的 UIFlow2 接口。
- 目标：检查最新 QEMU 是否引入接口回归，收集仍存在的问题，并对可确认的
  测试基础设施问题给出控制证据。
- 约束：使用互相隔离的 Device Service `/api/v1` 可见会话；不占用用户
  测试服务；不把虚拟设备结论写成物理硬件结论。

## 结论

本轮在源码 `66af02cc6061bded00659ee13632f5e3a9a397dc` 构建的 QEMU
`05a43941…` 上完成三台设备复测。所有主报告实际加载的 runtime 哈希一致。
没有发现本次模拟器更新造成的稳定接口回归，也没有需要新增的模拟器源码修复。

现有 stock SDK 缺陷可稳定复现；相同 stock firmware 上加载 hash-pinned
candidate 后全部通过。StopWatch/StickS3 stock internal-controller GATT
仍是模型缺口，BLE client 角色仍未准入。Core2 stock BLE 仅在其
`core2-native-hci` + matching ELF 路径上通过。

## 控制实验

### Core2 network reconnect

首次三设备协议套件并发时，Core2 完成 13 个 network 单步结果后，
`active(False) -> active(True) -> scan` 未看到 fixture AP。保留失败
session 和串口。随后：

1. 隔离重跑 `network` 得到 `14/14 PASS`；
2. 三设备再次并发 `network` 得到三台均 PASS；
3. 同一三设备并发形态又重复三次，均 PASS。

因此该事件归类为一次 transient concurrency startup/reconnect control，
不转写为稳定功能失败；但“任意负载下 reconnect 后首次 scan 必有 AP”
仍不能由本轮证明。

### StickS3 TLS candidate bootstrap

TLS candidate 是可使用 native UART REPL 的完整镜像。首次调用仍使用默认
dupterm bootstrap，`boot.py` 触发 `uart_driver_install` invalid state。
使用 `--uart-repl-bootstrap native` 重跑后为 `5/5 PASS`。第一次失败保留为
测试控制，不计作 TLS 功能失败。

### Bounded post-oracle wait

StopWatch/Core2 部分板级 probe 在完成显示/QOM oracle 后使用无限空闲循环。
为让 Device Service 有界收尾，controlled rerun 只把探针尾部的空闲循环替换为
一次等待并输出完成 marker，oracle 主体和输入/QOM 动作保持不变。最终所有
板级 case PASS，frame 哈希与此前结果一致。

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
  candidate 两台均为 4 个状态和 2 个画面 oracle PASS。

### 验证层级

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/static | PASS | `1432` platform tests、四个生成器检查、JSON、UTF-8、diff |
| transport | PASS（限定） | 实际 HTTP/TCP/UDP/MQTT/Modbus/TLS peers、BLE HCI peer、I2C/IR fixtures |
| device_response | PASS（限定） | guest 原库/API、serial marker、QOM、frame、PCM |
| data_behavior | PASS（限定） | 精确协议 payload、sensor readback、frame pixels |
| visual_or_physical | PARTIAL | 虚拟 frame/PCM 数据面通过；物理声学/光学/电气 NOT RUN |

## 修改范围

模拟器源码没有功能修改。新增了本轮证据页、摘要和当前状态/验证台账入口。
结果提交为 `0769ae7c0136f81aa34d85a58588c67fd879fc19`。

## 验证边界

- StopWatch/StickS3 stock controller GATT 未通过，不能继承 Core2 native-HCI；
- 未验证 BLE pairing/security、RF、天线、共存、长期负载和 bit-exact controller；
- ESP-NOW 仅为同 guest controller loopback，不覆盖外部 peer、加密 payload、
  跨设备 fabric、loss/retry 或 RF；
- 未验证 Core2 legacy UIFlow normal-WDT 启动、setup/REPL 和非空应用帧；
- 未执行物理硬件、声学、光学、电气和物理 PSRAM/cache timing。

## 风险与回滚

本轮未执行不可逆硬件操作，也未改变默认参考固件或设备配置。源码仓库可回滚
文档提交 `0769ae7c`；测试运行态和完整 raw evidence 位于 ignored `.work/`，
不会进入 Git。
