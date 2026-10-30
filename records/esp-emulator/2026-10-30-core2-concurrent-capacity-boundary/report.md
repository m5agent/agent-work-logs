# Core2 concurrent capacity boundary report

## 背景

- 来源：`CORE2-02` 继续扩展 Core2 `qemu-unified/core2-native-hci`
  单设备并发容量。
- 现象或需求：验证能否把 Device Service 的默认 `max-per-device`
  从 8 提升到 9，同时确认当前 runtime 的网络重检与 PSRAM 压力门限。
- 目标：至少两批独立九实例零错峰 PASS，且无 panic、GATT timeout、
  HLI error 或输入资产漂移；任何单次 guest panic 都不得被成功批次覆盖。

## 结论

- 状态：`PARTIAL`。
- 根因或关键判断：九实例不是纯粹超出资源预检的结果。三个批次均创建了
  9 个 lease 并观察到真实并发 9；其中第三次 attempt 8 在 NimBLE ACK
  路径出现 `LoadProhibited`。历史逻辑的同一 PC
  `ble_hs_hci_process_ack @ 0x402630cc` 再次出现，说明 HLI response
  ordering / guest preallocation 边界尚未覆盖九路启动 burst。
- 改动范围：默认容量保持 8；runner 拒绝 concurrency 9；网络重检增加
  有界重试；PSRAM/network error 分字段；GATT 和 HTTP timeout 调整；
  120 秒压力 floor 按当前 runtime 重绑；文档、catalog/profile 和
  契约测试同步。

## 证据

### 代码或配置

```text
DEFAULT_MAX_PER_DEVICE = 8
MAX_CONCURRENCY = 8
gatt/notification timeout = 45 seconds (extended exchange)
controlled HTTP timeout = 20 seconds
public HTTP timeout = 25 seconds
network recheck attempts = 3; retry delay = 1 second
120-second sustained floor = 3 sweeps, 2 heartbeats,
                              2 HTTP rechecks, 2 public rechecks
```

### 执行

- 环境：macOS arm64；Python 3.12；Device Service `/api/v1`；
  `runtime=qemu-unified`；`profile=core2-native-hci`；
  `tcg,thread=single,tb-size=128`；`icount shift=5`。
- 九实例输入：
  - firmware `b228ae0f224098e5a256ab87cbfdad5e3671eeea51766f4727cf7ef2070d5093`
  - ELF `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`
  - QEMU `54e7a7f7cd0ff6f5a1d6343c06563388f49c2b0abbca4cafb850876e57ed1254`
- 当前两实例输入：
  - firmware `ae094f4824d15499a5770018393660d1051866743dec52265552b6fc23eb2a23`
  - ELF 同上
  - QEMU 同上
- 命令形态：Device Service create/wait/network/frame/QOM/evidence/
  stop；runner `--attempts 9 --concurrency 9` 和
  `--attempts 2 --concurrency 2`，`--out-dir` 使用独立临时目录。
- 结果：九实例两批 `9/9 PASS`，第三批 `8/9 FAIL`；当前两实例两批
  各 `2/2 PASS`，合计 `4/4`。

### 失败控制

第三次九实例 attempt 8：

```text
first panic: LoadProhibited, PC=0x402630cc, EXCCAUSE=0x1c
symbol: ble_hs_hci_process_ack
secondary panic: StoreProhibited, PC=0x40092e43
peer_gatt_timeout: false
failed before READY/GATT; WiFi and public HTTP had already passed
```

高负载主机上的额外八实例尝试没有计入容量 PASS：部分 guest 已达到
`UNIFIED_CORE2_READY`，但 BLE server 初始化出现 `OSError(116)`；
单实例和两实例控制在同一轮工具哈希下仍正常。该现象保留为宿主争用风险，
不等同于八实例功能 PASS 或代码 FAIL。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall；Device Service 启动；对应 firmware 已生成并由 SHA 绑定 |
| transport | `PASS`（限定两实例） | WiFi DHCP、controlled HTTP、公网 DNS/HTTP、外部 NUS GATT、HLI `45/45` |
| device_response | `PASS`（限定两实例） | 8 MiB QOM、三次 1 MiB PSRAM 连续读回、frame、32-node QOM、pcap、evidence |
| data_behavior | `PARTIAL` | 当前两批 `2x60s` 为 `4/4`；九实例出现可复现 ACK panic，current-load 八实例 cold-start 重绑未 PASS |
| visual_or_physical | `NOT RUN` | 仅有 frame 存在性/PNG 证据，无物理显示、电气、RF 或真机测量 |

## 验证边界

- 九实例容量不通过；两次成功不能替代一次独立的 guest panic。
- 当前高负载宿主下的八实例 cold-start 重绑仍 OPEN。
- 所有结果均为 virtual-device validation。
- 物理 PSRAM/cache timing、bit-exact Espressif BT controller/baseband、
  RF、电气和硬件均未验证。

## 风险与回滚

保持默认八实例是安全选择。回滚时将 `run_service_5x.py`、
`unified_core2/main.py`、
`device_service.py`、测试和生成文档整体 revert 到 PR base
`e3f149c1ffad45ac923e677dea1af599a78c35a6`。本记录未执行任何设备写入、
烧录、擦除或不可逆硬件操作。
