# StopWatch / StickS3 / Core2 UIFlow2 接口再次复测报告

## 背景

用户要求用最新模拟器并发复测三台设备的 UIFlow2 接口，收集剩余问题并统一
处理能确定修复的部分。复测必须使用互相隔离的 Device Service，不能占用用户
的测试服务。

## 结论

本轮没有发现新的稳定功能回归。三台 stock 固件继续复现既有 SDK/模型边界，
相同固件上的 candidate 路径通过。新增的测试工具问题已修正：

1. Core2 并发 BLE teardown 在完成 GATT/ACK 后，可能与 stock library 的
   disconnect 自动重广告竞争；测试在 `deinit()` 前等待 2 秒，stock 与
   candidate 复核均通过。
2. `ble-client`/`m5ble-client` 需要 service 扮演 BLE peripheral；该角色当前
   只准入 CoreS3/Cardputer-ADV，其余设备现在明确记为
   `NOT_RUN / BLOCKED_FIXTURE`，不再误称为 stock controller 失败。
3. 新增冷启动逐控件 M5UI matrix runner；每类设备使用自身尺寸和 rotation，
   每类控件使用独立 visible session。
4. M5UI candidate 准备器允许 checkout commit 不是 manifest 原 commit 的
   情况，但仅当全部 reviewed source preimage、candidate postimage 和 patch
   正反应用都逐字节匹配；provenance 明确记录 source admission。

## 关键判断

### stock 缺陷

- requests2 `urlencode`：三台 `15 PASS + 1 FAIL`；
- Modbus async：三台 `42 PASS + 8 ERROR`，缺少 `Loop.sock_recv`；
- TLS epoch：三台 `3 STATE_PASS + 2 ERROR`；
- Core2 `m5ble.Server.get_client(0)`：`21 PASS + 1 ERROR`，对 `set` 下标；
- M5UI：`draw_triangle`、`Image.set_scale(1.5)`、`Spinbox.set_step(5)` 各一
  FAIL。

candidate lane：

- requests2 三台各 `2/2 PASS`；
- Modbus async 三台各 `50/50 PASS`；
- TLS candidate firmware 三台各 `5/5 PASS`；
- M5UI candidate 两台各 `4/4 STATE_PASS + 2/2 FRAME_PASS`；
- Core2 M5BLE 叠加 `0021 + 0025` 后 `22/22 PASS`。

### 覆盖结果

| 范围 | 结果 |
| --- | --- |
| system runtime | 三台各 `50 PASS + 1 STATE_PASS` |
| shared corrections | 三台各 `7/7 PASS` |
| board display | StopWatch `468x468`、StickS3 `135x240`、Core2 `320x240` |
| sockets / MQTT / network / EzData | 三台分别 `23/23`、`42/42`、`14/14`、`17/17` |
| EasySocket | 三台 `57 PASS + 1 NOT_APPLICABLE_LISTENER` |
| ESP-NOW | 三台 `12 PASS + 5 STATE_PASS + 1 CONFIGURED_UNVERIFIED` |
| native ESP-NOW | 三台 `21 PASS + 21 STATE_PASS + 3 CONFIGURED_UNVERIFIED` |
| audio | StopWatch/StickS3 player `15/15`、recorder `12/12`；Core2 不导出 |
| M5UI | StopWatch/Core2 各 507 结果、29 READY frame、0 unobserved |
| Core2 stock BLE NUS | settle 后两轮各 `8/8 PASS` |

三台通用 hardware matrix 各为
`115 CALL_OK + 66 API_ASSERTION_PASS + 1 OBSERVED`。设备本地组还覆盖
StopWatch M5IOE1/M5PM1/vibration、StickS3 buttons/PWR/IR TX/RX、Core2
INA3221/IMU/AXP192/Mic/Speaker。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/static | PASS | platform `1428` tests、生成器、compileall、scoped Ruff、JSON、diff |
| transport | PASS（限定） | 实际 network sockets/MQTT/Modbus peers、BLE HCI peer、I2C/IR fixture |
| device_response | PASS（限定） | guest 原库/API 调用、serial markers、QOM、frames、PCM |
| data_behavior | PASS（限定） | exact TCP/UDP/MQTT/Modbus/TLS/BLE payload、sensor reads、frame pixels |
| physical | NOT RUN | 无同固件物理设备、RF、声学、光学、电气或 cache/PSRAM timing |

## 未解决或未覆盖

- StopWatch/StickS3 stock internal-controller GATT；
- BLE pairing/security、RF、共存、bit-exact controller；
- 外部/加密 ESP-NOW 与跨设备 fabric；
- Core2 legacy UIFlow normal-WDT 启动与应用帧；
- 任意参数域、长期稳定性和物理等价性。

## 风险与回滚

改动限于测试 runner、候选源码准备与文档，不改变默认参考固件或设备目录。
可回滚源码提交 `490539ce`；中间提交 `d59651d8` 保留可审计历史。
没有不可逆硬件操作。
