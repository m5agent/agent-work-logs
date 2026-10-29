# ESP Emulator SVC-03 runtime boundary and Core2 unified stability 报告

## 背景

- 来源：`SVC-03` 与 PR
  [#46](https://github.com/m5agent/m5stack-esp-emulator/pull/46)。
- 需求：继续缩小 `device_service.py` 的无状态 runtime 职责，并验证拆分后的
  Core2 unified service path。
- 目标：保持 API/evidence/history 契约，修复可由 session readiness 与 guest
  TX settle 解释的 unified 假失败。

## 结论

本里程碑为 `PASS`，覆盖代码边界、platform contracts 和 Core2 unified
virtual-device 功能路径。

`device_service_runtime.py` 接管以下无状态对象：

- `PRIVATE_RUNTIME_ENV`；
- `qemu_runtime_memory()`；
- `runtime_psram_mismatch()`；
- `redacted_runtime_env()`。

`device_service.py` 继续 re-export 相同对象，因此 public import identity 和
现有调用方不变。

复测暴露并修复：

1. profile QOM 注入固定等待 20 秒，短于慢 guest 的 session readiness；
2. unified BLE peer 在 GATT subscription 后只等待 2 秒，guest RX handler
   已执行但 TX path 尚未 settle 时，peer 会进入 notification timeout；
3. reconnect workload 预算未包含新增的 10 秒 unified write settle。

## 证据

### 代码或配置

```text
device_service_runtime.py
  PRIVATE_RUNTIME_ENV
  qemu_runtime_memory
  redacted_runtime_env
  runtime_psram_mismatch

device_service.py
  profile QOM wait = session ready_timeout
  Core2 unified default readiness = 180 s
  unified peer write delay = 10 s

ble_runtime_limits.py
  unified write delay = 10 s
  reconnect cycle budget = 16 s
```

### 执行

- 环境：macOS Apple Silicon；Python 3.12；Device Service `/api/v1`；
  `runtime=qemu-unified`，`profile=core2-native-hci`。
- 固件：`c3eaa35b9c41204cc6337e30b1d81f60bf06eab2d747f3547af5d8b8ba0ea99f`。
- Matching ELF：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`。
- 最终 QEMU：
  `568079f3b9e818ef1cc29b9e7cd1c5c036af19196668a12174ed79ec96c262ed`。
- 相同 10 秒 settle 的旧 QEMU 对照：
  `54e7a7f7cd0ff6f5a1d6343c06563388f49c2b0abbca4cafb850876e57ed1255`。
- 每台 QEMU 三条独立 lease，均无 retry。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | full platform `1581 OK + 1 skip`; compileall |
| transport | PASS | QEMU UART、WiFi、native HCI/HLI 和外部 BLE peer |
| device_response | PASS | WiFi DHCP/HTTP、public DNS/HTTP、NUS ACK |
| data_behavior | PASS | 3,888-byte frame、32-node QOM、HLI `45/45`、pcap |
| visual_or_physical | NOT RUN | virtual frame only; no physical display validation |

最终 QEMU 的每个 lease 均为：

- frame SHA256
  `fa98d48fc9fd2a18e78fbf327374ae1725a473dc7cad7bc81418895ac8c96c33`；
- QOM effective PSRAM `8 MiB`；
- HLI posts/consumed `45/45`，events/ACLs `36/9`；
- HLI/meta queue depth、errors、dropped、TX queue 均为 `0`；
- notification 精确为 `ACK:M5_CORE2_UNIFIED`；
- evidence ZIP、manifest、session binding、stop 和 companion/QEMU cleanup
  PASS。

## 验证边界

这是 virtual-device validation。它不证明物理硬件、RF、天线、BLE
安全/配对、coexistence、电气或物理 cache/PSRAM timing。结论绑定到记录中的
firmware、ELF、QEMU、runner 和 service hashes；不转授其他固件 SHA。

Core2 legacy UIFlow `RUNTIME-03` 仍为 `OPEN`。本记录的 native-HCI
UIFlow2 unified path 不能作为 legacy app startup PASS。

## 风险与回滚

新增 10 秒 write settle 会略增 unified peer 单轮耗时，已同步扩大 reconnect
workload 预算。若需要回滚，可回退 merge commit `20ae4413`；这会同时恢复
runtime helper 文件拆分和 service timing 修复，不涉及持久化数据迁移。
