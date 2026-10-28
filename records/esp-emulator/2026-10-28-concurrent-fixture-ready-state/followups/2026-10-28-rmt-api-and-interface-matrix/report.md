# ESP Emulator 三设备 UIFlow2 接口矩阵与 RMT API 夹具报告

## 背景

- 来源：用户要求重新覆盖 StopWatch、StickS3、Core2 上当前 UIFlow2 可执行接口。
- 现象或需求：设备间并发测试，失败先保留，再统一定位和修复。
- 目标：区分测试基础设施、模拟器模型、原厂固件缺陷和物理硬件边界。

## 结论

- 状态：`PARTIAL`。可经当前 Device Service 执行的系统、外设、协议、ESP-NOW、
  UI/输入路径均完成；一个新测试接口缺口已修复。
- 根因：`platform/tools/runtime_interfaces.py` 与设备矩阵已定义 RMT
  TX/RX 文件接口，但 Device Service 的 `runtime_env` 白名单遗漏对应 keys。
- 改动范围：放行 `M5SW_RMT_TX_FILE`、`M5SW_RMT_RX_FILE` 和
  `M5SW_RMT_TRACE`；RMT trace 继续只接受字符串 `"1"`，并新增白名单合同测试。

## 证据

### 设备组

| 设备 | Case 数 | 结果 | 说明 |
| --- | ---: | --- | --- |
| StopWatch | 6 | `6/6 PASS` | 外设、振动、Speaker、Mic、M5IOE1、M5PM1 |
| StickS3 | 5 | `5/5 PASS` | 外设、Speaker、Mic、IR TX、IR RX |
| Core2 | 6 | `6/6 PASS` | 外设、Speaker、Mic、INA3221、IMU、AXP192 |

Core2 首轮测试基础设施曾把 18 秒等待拆成多次 10 秒 action；修正驱动时序后，
三个最初黑帧 control 均已保留，并按真实输入 readiness marker 重跑通过。
Core2 IMU 另做三次独立首跑，全部 PASS。

### System 与 shared corrections

- 三台 system runtime：各 `50 PASS + 1 STATE_PASS`；
- 三台 shared corrections：各 `7/7 PASS`；
- candidate fixture hashes 与既有记录一致。

### 通信协议

| 组 | 三台结果 |
| --- | --- |
| Sockets | `23/23` |
| EasySocket | `57 PASS + 1 NOT_APPLICABLE_LISTENER` |
| MQTT | `42/42` |
| Network | `14/14` |
| EzData owned fixture | `17/17` |
| requests2 candidate | `2/2` |
| Modbus async candidate | `50/50` |
| ESP-NOW loopback | `12 PASS + 5 STATE_PASS + 1 CONFIGURED_UNVERIFIED` |
| native ESP-NOW API | `21 PASS + 21 STATE_PASS + 3 CONFIGURED_UNVERIFIED` |

StopWatch 与 StickS3 audio wrapper：player `15/15`、recorder `12/12`。
Core2 stock image 不导出 `audio`，`audio-player` probe 以明确
`ImportError: no module named 'audio'` 结束；同板官方 `M5.Speaker` /
`M5.Mic` 设备组路径仍 PASS。

### UI 与输入

三台均通过 Device Service 注入真实输入并在停止前取得最终帧：

- StopWatch：touch marker；`466x466`；绿色成功像素 `(233,233)`；
- StickS3：BtnA marker；`135x240`；绿色成功像素 `(3,3)`；
- Core2：touch marker；`320x240`；绿色成功像素 `(2,2)`。

Core2 1 秒抓帧 control 仍只有蓝色边框/灰阶文字，5 秒后绿色成功区才出现。
该差异保留为显示刷新采样时序，不外推为绘制 API 失败。

### Stock 固件边界

- HTTP stock：三台均 `15 PASS + 1 FAIL`，失败为
  `requests2.urlencode` 保留字符/UTF-8；
- Modbus stock：三台均 `42 PASS + 8 ERROR`，失败为
  `Loop.sock_recv` 不存在；
- TLS stock：三台均 `3 STATE_PASS + 2 ERROR`，握手报证书过期；
- 以上项目均有独立 candidate lane；本轮只重新执行 requests2 与 Modbus async
  candidate，TLS candidate 为 `NOT RERUN`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | QEMU 与三台基础镜像 SHA256 固定 |
| transport | PASS | 实际 WiFi/SLiRP、Socket/MQTT/Modbus peer、RMT symbols |
| device_response | PASS | UIFlow2 serial marker、QOM、PCM、RMT 和 frame |
| data_behavior | PASS | 输入后绿色标记、peer 请求、PCM 波形和 NEC 解码 |
| visual_or_physical | PARTIAL | 虚拟帧 marker PASS；物理显示、触控与光学 `NOT RUN` |

## 验证边界

全部结果是 `virtual-device validation`。没有证明物理触摸压力、面板刷新率、
SPI 信号完整性、声音、RF、功耗或电气测量。

## 风险与回滚

RMT 白名单只扩大 trusted-local diagnostic file injection，与既有 PCM
文件接口同层；trace 仍为严格 boolean enable。回滚对应 Device Service
commit 会恢复旧的 IR API 不可测状态，不改变已有 QEMU RMT 模型。
