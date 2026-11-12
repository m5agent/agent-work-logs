## 现象

2026-11-12 批量矩阵中，两款 PM1 供电的墨水屏设备官方 UserDemo 固件启动后主动关机，Device Service 把这种**正常下电**记为 `device_service_startup_failed`，会话 `state=failed`：

| 设备 | 固件 | firmware_id | 现象 |
| --- | --- | --- | --- |
| PaperColor | PaperColor User Demo | 1897200000000001839 | 2.4 s 时 `M5PM1_PWR: Shutdown requested`，进程退出码 0 |
| PaperDIY | PaperDIY User Demo | 2110309776206622722 | 5.0 s 时 `AppShutdown: Sending M5PM1 shutdown command`，退出码 0 |

两次会话都留下了 400×600 / 540×960 的**全白**末帧（唯一色数为 1），说明固件在关机前已经初始化显示并画了关机/首启页面，但会话被判失败，评审侧无法把它当作有效证据。

## 证据

- PaperColor 会话 `8fa66b4959f046bda8a03eed83059e7f`，串口尾部：

```
I (1372) M5PM1_I2C: M5PM1 initialized via M5Unified I2C at address 0x6E (100000 Hz)
I (1562) M5PM1_PWR: Charge Enabled
I (1572) M5PM1_PWR: Boost Enabled
I (2432) M5PM1_PWR: Shutdown requested
```

- PaperDIY 会话 `d772ed9900664a1cb133503216a89b3e`，串口尾部：

```
I (446) HAL: Display ready: 540x960
I (471) AppShutdown: First factory boot: displaying shutdown logo
I (5046) AppShutdown: Sending M5PM1 shutdown command
```

- 两次的 `error` 都是 `process exited with code 0`，`final_snapshot.state=failed`。

## 影响

- 视觉评审把正常的下电流程误判为启动失败；`failed` 会话通常不被当作固件可用性证据。
- 若固件未来继续演进（例如低电量保护），其它 PM1 设备同样会命中，矩阵结果里会持续出现“伪失败”。
- 目前无法区分“固件主动关机”“PM1 电池/充电状态导致关机”“guest 崩溃退出”三种情况。

## 期望 / 验收

1. Device Service 识别 guest 主动下电（PM1 shutdown / clean QEMU exit）并记录为 `stopped`（例如 `stop_reason=guest_poweroff`），保留末帧与串口，不记为启动失败。
2. 如果关机根因是模拟器缺少电池/充电状态模型，请补 PM1 电源状态并说明默认值来源；同时保持上述会话语义修复。
3. 验收：用这两个固件复跑，会话为 `stopped/guest_poweroff`，末帧与串口可读，矩阵状态为 `PARTIAL`（已显示关机页）而不是 `device_service_startup_failed`。

## 边界

- virtual-device 验证；不涉及真机电源、电池或电气测量。
- 未修改固件、Flash 或设备 profile。
