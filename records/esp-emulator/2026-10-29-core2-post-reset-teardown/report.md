# ESP Emulator Core2 post-reset teardown 报告

## 背景

`CORE2-02` 已有 active-stop 和 session 恢复证据，但没有覆盖 guest 已经执行
`system_reset`、reboot 仍在进行时停止同一 lease 的生命周期。该路径会同时影响
Device Service session 状态、QEMU PID、BLE/HTTP companion、worker lease 和
evidence 获取，不能由普通 active-stop 结果继承。

## 实现

`tests/uiflow2/core2_native_hci/run_service_teardown.py` 新增：

```text
--stop-mode active|after-reset
```

`active` 保持原有默认行为。`after-reset` 的执行顺序为：

1. 等待 `UNIFIED_CORE2_READY`；
2. 捕获 frame、32-node QOM、WiFi/public DNS/HTTP、external NUS GATT、
   serial、pcap 和 evidence ZIP；
3. 通过 guest 执行 `system_reset`；
4. 等待 0.25 秒 reboot-in-flight，验证 session 仍为 `running` 且同一 QEMU
   PID 仍存在；
5. 停止 session；
6. 验证最终状态为 `stopped`/无错误、HTTP 与 BLE companion 终止、BLE/QEMU
   PID 回收、worker lease 归零；
7. 创建下一轮 session。

evidence kind 会区分 post-reset 路径；运行日期在记录时动态生成。

## 兼容性

CLI 默认值和原 runner 的 finish 路径未改变。只有显式传入
`--stop-mode after-reset` 时执行 reset-in-flight 分支。改动是
test/evidence runner 与文档，不改变生产 Device Service API、QEMU 控制器或
guest firmware。

## 执行

在 macOS arm64 上启动本地 Device Service，使用已校验的 Core2 UIFlow2 image、
matching ELF 和 QEMU binary，运行：

```text
run_service_teardown.py --attempts 3 --stop-mode after-reset
```

每次 lease 都完成完整 ready evidence 捕获、guest reset、in-flight 检查、
stop、cleanup 和下一 lease 创建。三次结果均为 `PASS`，每次 `23/23`
checks PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python `compileall`；使用 hash-bound 已构建 QEMU/firmware |
| transport | `PASS` | Device Service HTTP、QEMU serial、WiFi/public HTTP、external NUS GATT |
| device_response | `PASS` | `UNIFIED_CORE2_READY`、native-HCI health `45/45`、guest `system_reset` |
| data_behavior | `PASS` | frame、QOM、network、pcap、evidence 数据均在 stop 前获取 |
| visual_or_physical | `PASS`（仅 virtual frame capture） | frame PNG 存在；physical hardware、RF 和电气验证 `NOT RUN` |

平台回归为 `1535 OK + 10 skipped`。runtime coverage、peripheral catalog、
QEMU profiles、project snapshot、compileall、diff check 和 PR scope check
均通过。PR CI 与合并后 main CI `40837477524` 均为 PASS。

## 验证边界

本记录只证明 trusted-host virtual device 在 guest reset 已开始、reboot 仍在
进行时，可以停止同一 session 并清理 worker-owned runtime。它不证明：

- physical hardware、RF、电气或物理 PSRAM/cache；
- bit-exact Espressif BT controller/baseband；
- guest/controller 内部状态在 stop 后已经完全 quiesce；
- cross-host migration 或恶意固件沙箱；
- active-stop/post-reset 之外更复杂的 teardown。

## 风险与回滚

改动没有不可逆设备操作，也没有修改生产 runtime 契约。可 revert
`86454588beef9180f207dc4eafd52acfe764b4f4`；旧的 `active` runner 路径和
已有 evidence 格式仍可继续使用。
