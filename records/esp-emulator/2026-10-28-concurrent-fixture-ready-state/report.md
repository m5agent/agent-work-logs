# ESP Emulator 三设备并发复测与 runner 竞态修复报告

## 背景

- 来源：用户要求在 StopWatch、StickS3、Core2 上重新覆盖可执行的 UIFlow2 接口。
- 现象或需求：设备间并发以提高速度，同时收集失败后统一修复。
- 目标：区分固件缺陷、模型缺口和测试基础设施故障，并在最新 QEMU 上重绑结果。

## 结论

- 状态：`PARTIAL`。测试基础设施问题已修复；多项设备功能在同一 runtime 上通过，
  但 stock 固件缺陷、legacy Core2 和物理硬件边界仍未关闭。
- 根因：
  - 固定 controlled HTTP fixture 使用 profile 分配的 host port；多个只需自有
    peer 的会话并发时出现端口冲突。
  - 串口 marker 在 session 状态从 `booting` 更新到 `running` 之前可见；
    hardware runner 立即发送输入会得到 `409 session_not_running`。
  - Core2 bounded drive 需要 18 秒首等待，但 hardware runner 原先拒绝
    10 秒以上的 action delay。
- 改动范围：Device Service network 参数、协议 runner、hardware runner、
  Core2 matrix 等待时间、API/OpenAPI 文档及合同测试。

## 证据

### 代码或配置

- `network.http_fixture=false` 只关闭 profile 固定 listener，保留 WiFi NIC、
  serial、frame、QOM 和 pcap。
- Hardware runner 在 marker action 前轮询 session 至 `running`。
- Host action delay 上限为 30 秒；Core2 特定 case 使用 18 秒首等待。

### 执行

- 环境：macOS arm64、QEMU TCG、隔离 Device Service、UIFlow2 `v2.5.3`。
- 设备：StopWatch、StickS3、Core2。
- 命令：`run_protocols.py`、`run_hardware_guest.py`、
  `run_device_api.py` 和平台 unittest；原始输出保留在本地 ignored storage。
- 结果：
  - 三台 system/shared/稳定协议结果通过；
  - 两个并发 sockets/network 会话通过；
  - 两个并发 unified ESP-NOW loopback 会话通过；
  - StopWatch/StickS3 BtnA hold、Core2 PWR/touch 通过；
  - Core2 peripherals/IMU/AXP192 顺序帧通过；
  - API sweep `95` cases 全 PASS；
  - platform `1364` 项 `OK`、`1` skip。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | QEMU binary 与三台 base firmware SHA256 固定 |
| transport | PASS | 并发 sockets/network、ESP-NOW controller loopback |
| device_response | PASS | system/shared/API/input/audio 真实 guest marker |
| data_behavior | PASS | QOM/frame/PCM/协议 peer 独立 oracle |
| visual_or_physical | PARTIAL | Core2 三帧非黑并核绿色标记；物理显示/触控 NOT RUN |

## 验证边界

物理硬件、RF、声学、光学、电气、触控压力和完整应用启动未执行。Core2 legacy
`RUNTIME-03`、外部/加密 ESP-NOW 、完整 M5UI 文档矩阵仍开放。

## 风险与回滚

改动只扩大测试会话隔离和 bounded action 窗口，不改变 guest 固件、芯片模型或
输入坐标系。回滚源码提交即可恢复固定 HTTP listener 和旧等待上限；已停止会话
和 evidence 不应删除。
