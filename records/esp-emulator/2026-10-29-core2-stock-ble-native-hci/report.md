# Core2 stock UIFlow2 BLE 报告

## 背景

三设备 UIFlow2 全接口复测中，StopWatch/StickS3 未发现可连接
advertisement，Core2 在 `UNIFIED_CORE2_IO_CONFIG_READY` 前 timeout。
Core2 已有 canonical `core2-native-hci` 后端和 stock internal-controller
GATT 证据，因此先审计 protocol runner 的实际 profile 选择。

## 根因

`run_protocols.py` 对 Core2 BLE 仍硬编码 `core2-unified`，并在
`core2-native-hci` 需要 `network.elf_artifact_id` 时没有上传 matching ELF。
因此失败是 harness/profile 选择错误，而不是本次 control 能证明的
stock controller 缺失。

第二个问题是 ACK oracle 额外要求 host-only
`BLE_BUMBLE_CYCLE_PASS 1`。guest 完成路径后会立即返回完成 marker，服务
按设计停止 session/peer；此时 exact notification 已经出现，但 host 的
一秒收尾 marker 可能来不及写。该 marker 不包含额外数据面证据。

## 改动

- Core2 BLE 使用 `core2-native-hci`；
- 新增 `--core2-elf`，要求 callers 显式传入 matching ELF；
- ELF 先上传为 service artifact，再作为 `network.elf_artifact_id`；
- missing ELF fail closed；
- ACK oracle 要求同一 peer log 内同时存在 connection、GATT discovery、
  subscription、exact peer write 和 exact ACK notification；
- 不再把 host-only cycle tail 作为必要条件。

## 执行

固定身份：

- stock base `b228c0e2d877e77a8a352e917ed84f4da8ea92d15b25e28f431a2999620fe3c4`
- matching ELF `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`
- QEMU `9bf74439ddbe7225a64eb437290043729fb032525756adb834565ec412f8c197`

三个独立 Core2 `ble-nus` session 均为 `8/8 PASS`。peer 观察：

```text
BLE_BUMBLE_FOUND name='M5-CORE2-UNIFIED'
BLE_BUMBLE_CONNECTED
BLE_BUMBLE_GATT_DISCOVERED 6e400001-b5a3-f393-e0a9-e50e24dcca9e
BLE_BUMBLE_SUBSCRIBED 6e400003-b5a3-f393-e0a9-e50e24dcca9e
BLE_BUMBLE_WRITE M5_CORE2_UNIFIED
BLE_BUMBLE_NOTIFICATION_OK ACK:M5_CORE2_UNIFIED
```

三个 evidence ZIP SHA256：

1. `8bce94370d3be9a433dea55b785a0070540f65aac10ac9385bcf3f102d38faa1`
2. `a35f1fd7ebfce401ead664a38ff761715cb0f9a5bf776bf842646d100811e060`
3. `66122c83ba2318e4697d1ccb7bbdc9f00119d0d7c995e94eacc50454d8dfb4a36`

所有 runtime PID gone，evidence/history 保留。

## 补充 API 结果

Core2 `m5ble-server`：`21 PASS + 1 ERROR`。已工作的部分包括 advertising
payload/decode、service UUID、peer write/read、client registry、GATT
notification 和 lifecycle。唯一错误：

```text
m5ble.m5ble.Server.get_client
TypeError("'set' object isn't subscriptable")
```

该错误归为 stock SDK/API 缺陷保留，不能把整体 `m5ble` 标为全 PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | source commit CI 两 job |
| transport | PASS | real HCI controller relay 与 BLE peer |
| device_response | PASS | advertisement/connect/GATT/read/write |
| data_behavior | PASS | exact guest payload 与 ACK notification |
| physical/RF | NOT RUN | 无物理 radio/天线/安全配对测试 |

## 验证边界

- 只覆盖 Core2 stock base + matching ELF + `core2-native-hci`；
- StopWatch/StickS3 使用不同 S3 controller/profile，不继承；
- 不证明 WPA/LE Secure Connections、加密 NUS、RF、共存或时序；
- `Server.get_client` 继续保持 stock SDK 缺陷。

## 风险与回滚

改动只修正测试/profile 路由并新增 fail-closed ELF 输入。可 revert
public commit `2e2f4076`；不涉及不可逆硬件操作。
