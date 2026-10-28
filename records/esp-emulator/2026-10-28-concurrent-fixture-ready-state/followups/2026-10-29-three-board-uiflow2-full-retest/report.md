# ESP Emulator UIFlow2 三设备全接口复测报告

## 背景

- 来源：用户要求在 StopWatch、StickS3、Core2 上并发复测所有可执行
  UIFlow2 接口，收集问题后统一处理。
- 目标：验证当前模拟器和原厂 UIFlow2 `v2.5.3` 的系统、协议、UI、音频、
  ESP-NOW、BLE 与已选外设路径；区分固件缺陷、模型边界和测试工具缺陷。
- 方式：三台各用一个隔离 Device Service 并发运行，设备内串行执行；
  session stop 前保存 evidence ZIP，并保留历史。

## 结论

- 状态：`PARTIAL`。运行态和可执行接口覆盖显著扩大，测试工具缺陷已修复，
  但仍保留 stock SDK、Core2 M5UI 和 BLE 控制器边界。
- 根因分类：
  - Core2 M5UI runner 使用错误尺寸和 rotation；
  - Core2 慢速 program 超出旧 45 秒 marker 窗口；
  - BLE peer 身份表只覆盖 CoreS3/Cardputer；
  - radio blocker 对所有设备都写成 ESP32-S3。
- 固件边界：三台 stock HTTP、Modbus async、TLS epoch 缺陷稳定复现；
  hash-pinned requests/Modbus/TLS candidate 路径通过。
- 改动范围：测试 runner、probe、契约测试、当前状态、Backlog、验证台账和
  日期化 evidence；没有修改原厂固件。

## 测试工具修复

### M5UI 设备尺寸与旋转

`build_m5ui_program` 现显式接收并校验 `width`、`height`、`rotation`；
`run_ui_live` 和 documented runner 从 `tests/uiflow2/device_matrix.json`
读取 `api_size/ui_rotation`。`get_display_size` oracle 使用同一尺寸，
不再把 StopWatch `468x468` 或 Core2 rotation 误当固定值。

新增 3 个契约测试覆盖尺寸、非法维度、非法 rotation。

### Core2 program 预算

UI package request 和 marker wait 改用显式 `--program-timeout`，范围
`1..120` 秒，默认 120。最终 Core2 correction 切片实际运行约 107 秒，
仍完成 `SCREEN_LOAD DONE` 和 READY，证明旧 45 秒窗口会错误截断。

### BLE identity

protocol runner 现覆盖 CoreS3、Cardputer-ADV、StopWatch、StickS3、Core2
的广告名和 exact ACK payload，并与
`device_service.UNIFIED_BLE_IDENTITIES` 逐项对齐。新增 3 个测试覆盖映射、
四类 BLE group 编译和 blocker 文案。

## 执行结果

| 域 | StopWatch | StickS3 | Core2 |
| --- | ---: | ---: | ---: |
| System runtime | `50 PASS + 1 STATE_PASS` | 同左 | 同左 |
| Shared corrections | `7/7` | `7/7` | `7/7` |
| Sockets | `23/23` | `23/23` | `23/23` |
| MQTT | `42/42` | `42/42` | `42/42` |
| Network | `14/14` | `14/14` | `14/14` |
| EzData | `17/17` | `17/17` | `17/17` |
| EasySocket | `57 + 1 N/A` | 同左 | 同左 |
| Audio player | `15/15` | `15/15` | module not exported |
| Audio recorder | `12/12` | `12/12` | module not exported |

Stock failure controls：

| 域 | 结果 | 失败点 |
| --- | ---: | --- |
| HTTP | `15 PASS + 1 FAIL` | requests2 URL encoding |
| Modbus | `42 PASS + 8 ERROR` | missing `Loop.sock_recv` |
| TLS | `3 STATE_PASS + 2 ERROR` | certificate epoch |

Candidate controls：requests2 三台 `2/2`、Modbus async 三台 `50/50`、
TLS candidate firmware 三台 `5/5`。

ESP-NOW：

- `espnow` 三台均为
  `12 PASS + 5 STATE_PASS + 1 CONFIGURED_UNVERIFIED`；
- `espnow-native` 三台均为
  `21 PASS + 21 STATE_PASS + 3 CONFIGURED_UNVERIFIED`。

该路径是同 guest controller TX/RX DMA loopback，不是外部 peer/RF。

## M5UI

StopWatch 和 Core2 各执行 28 类、505 个文档方法，分类完全一致：

`407 STATE_PASS + 80 PENDING_FRAME_OR_INPUT +
3 PENDING_FRAME_OBJECT_REMOVAL + 11 DOCUMENTATION_MISMATCH +
1 EXPECTED_UNSUPPORTED + 3 FAIL`

三处 stock 失败为：

- `M5Canvas.draw_triangle` native descriptor；
- `M5Image.set_scale(1.5)` float-to-int；
- `M5Spinbox.set_step(5)` integer step 被放大为 50。

StopWatch candidate source 状态 `4/4`、frame `2/2 PASS`。Core2 candidate
source 状态 `4/4`，但在 rotation=1、screen load 完成并取帧后仍出现横向
条带和错误位置，frame oracle `0/2`。因此 candidate Python 语义修复成立，
Core2 panel window/full-screen refresh 仍需独立修复。

StickS3 当前 stock 镜像不导出 `m5ui`。

## BLE

修复后重跑三台最小 `ble-nus`：

- StopWatch 使用 `M5-STOPWATCH-UNIFIED` 扫描无可连接 advertisement，
  guest 最终报 actual NUS peer write absent；
- StickS3 使用 `M5-STICKS3-UNIFIED`，结果相同；
- Core2 在 `UNIFIED_CORE2_IO_CONFIG_READY` 前超时。

三台 runtime、managed BLE peer 和 companion 均清理，失败 session 保留。
这不关闭 stock internal-controller GATT。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | 1406 项平台回归、compileall、生成器检查 |
| transport | PASS | 三台 guest 串口、网络、协议 peer、frame 和 evidence ZIP |
| device_response | PASS | system/shared、sockets/MQTT/network/EzData、音频、ESP-NOW、已选外设 |
| data_behavior | PARTIAL | M5UI stock/candidate 差异成立；Core2 full-screen frame 未闭环 |
| visual_or_physical | PARTIAL / NOT RUN | 56 个 stock M5UI frame 非黑；Core2 candidate frame FAIL；物理硬件未执行 |

## 验证边界

所有结果都是 virtual-device validation。非黑帧不等于逐控件视觉正确；
ESP-NOW loopback 不证明外部/加密 peer 或 RF；stock BLE 不可用不能由显式
HCI test-firmware 结果替代。Core2 legacy `RUNTIME-03` 没有因本轮 UIFlow2
接口通过而关闭。

## 风险与回滚

本轮只修改测试 runner、契约、文档和 evidence，未修改 QEMU 或固件。
回滚测试工具提交会恢复设备尺寸/旋转和 BLE identity 的旧行为，并重新引入
Core2 45 秒截断及错误 blocker 文案；设备历史与原始 `.work/` 证据不会被
该回滚删除。
