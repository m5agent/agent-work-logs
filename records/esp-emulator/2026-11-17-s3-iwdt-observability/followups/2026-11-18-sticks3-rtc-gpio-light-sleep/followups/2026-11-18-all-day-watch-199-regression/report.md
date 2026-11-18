# 原版交互与运行时对照

## 背景

此前同一份 All Day Watch 原版的两次 CPU1 看门狗崩溃指向 RTC 睡眠完成轮询。同一旧运行时的较快输入对照在观察窗口内无 panic。后续 GPIO 修复同一原版已能唤醒。本次复测检查 1.99.0 冻结包是否保留原版行为，测试期间使用同一合成 Flash、关闭额外看门狗跟踪，并禁用客体网卡。[历史崩溃记录](https://github.com/m5agent/m5stack-esp-emulator/blob/a729e24b1e4724b783ab2d59eec689cfdfeb24b3/tests/firmware/crash_diagnostics/watch-retained-rtc-timing-summary.json) · [冻结源代码](https://github.com/m5agent/m5stack-esp-emulator/tree/a729e24b1e4724b783ab2d59eec689cfdfeb24b3)

## 复现

使用摘要给出的固件、归一化 Flash、QEMU 可执行文件和 S3 ROM 的 SHA-256。启动冻结源代码版本的隔离 Device Service，使用独立状态目录并禁用 QEMU 客体网卡。采用 [1.99.0 API 合约](https://github.com/m5agent/m5stack-esp-emulator/blob/a729e24b1e4724b783ab2d59eec689cfdfeb24b3/docs/device-service.openapi.yaml) 的普通接口执行下列步骤。

1. 通过 `POST /api/v1/artifacts` 上传 1,840,512 字节原版 BIN，然后以 `device_id=sticks3`、`kind=merged` 调用 `POST /api/v1/firmware`。复查返回归一化 Flash SHA-256。
2. 以 `runtime=qemu`、`device_id=sticks3` 创建会话。等待首次非黑帧并取样。用 `POST /api/v1/sessions/{id}/input` 依次发送 `kind=key` 的 A `tap`、B `tap`、B `down`、B `up`。每次请求的 `settle_seconds` 依次为 1.0、1.0、0.1、0.05。实测相对首帧的发送时间为 2.336、3.367、4.448、6.734 秒。
3. 用只读 QMP `query-status` 核对客体 `suspended`。经同一个 HTTP 输入接口发送 `{"kind":"button","control":"b","action":"click"}`，再通过 QMP 确认 `running`，取得唤醒帧。
4. 再观察 65 秒，轮询会话崩溃诊断，下载同会话证据 ZIP 并核对 CRC、清单和所有条目哈希。保留证据，释放会话和可变 Flash。

## 同会话结果

- 四个原版输入全部执行。约 20.229 秒后，QMP 观察到自然挂起。
- B 键走服务语义按键入口，按下保持 120 ms，返回主机时钟 `events_sent`。0.439 秒内观察到客体恢复。新的 135 × 240 画面有 32,400 个非黑像素。
- 唤醒画面后 65.117 秒内，14 次诊断采样，串口一次上电、零软件复位、零 panic。串口仍有此前同原版也出现的 SDK 禁用唤醒源告警。取 ZIP 时的后续画面为黑帧，唤醒时的非黑帧单独取样并记录哈希。
- 同一会话的 ZIP、清单、归一化 Flash 与串口哈希一致。停止后活动会话为零，无可变 Flash 保留。

## 边界

单次原版 GPIO 浅睡与唤醒通过。物理硬件、外部 32.768 kHz 慢钟、其他深睡唤醒源和 Burner 均为 `NOT RUN`。此次回归未产生源码改动或补丁。
