# StickS3 的 RC_FAST/256 RTC 慢钟

ESP32-S3 选择 RC_FAST/256 后，旧 QEMU 的 RTC 慢计数仍以约 31.25 kHz 增长，Timer Group 对同一选源的校准为 68.359 kHz。选源和 timer 唤醒原因均正确，实际挂起却超过两倍请求时间。补丁 0231 让 RTC 计数与 Timer Group 校准使用同一个内部慢钟常数。默认 RC 和外部晶体的选择项保持原定义。[精确补丁](https://github.com/m5agent/m5stack-esp-emulator/blob/3dae84c4cbce3671eb707f7c562973fef13df078/patches/qemu-m5stack-peripherals/0231-s3-rtc-fast-div256.patch)

## 同镜像对照及冻结包复测

在未修改的 ESP-IDF 5.5.4 上构建两份 8 MiB 镜像，两个配置仅切换 RTC 慢钟。使用同一已合成镜像、同一 ROM，通过普通 Device Service 创建网络关闭的原生会话，分别在旧运行时、候选运行时及 1.94 冻结包上取证。

| 慢钟 | 执行环境 | 清醒 RTC 计数频率 | QMP 挂起时间，目标 500 ms | 结果 |
| --- | --- | ---: | ---: | --- |
| 默认 RC | 旧运行时 | 135,971 Hz | 489.011 ms | PASS |
| 默认 RC | 候选运行时 | 135,968 Hz | 491.271 ms | PASS |
| 默认 RC | 1.94 冻结包 | 135,967 Hz | 488.774 ms | PASS |
| RC_FAST/256 | 旧运行时 | 31,242 Hz | 1,076.584 ms | FAIL |
| RC_FAST/256 | 候选运行时 | 68,345 Hz | 485.551 ms | PASS |
| RC_FAST/256 | 1.94 冻结包 | 68,338 Hz | 493.389 ms | PASS |

从原始 RTC tick 与 SYSTIMER 样本重算清醒计数率，从 QMP 的 SUSPEND 和 WAKEUP 时间戳及宿主单调接收时间核对挂起区间。固件回执、ZIP 清单、串口和每个条目的 SHA-256 均核验。SDK 休眠返回的时间会经过唤醒校正，所以用独立的宿主计时验证实际挂起。试验绑定实际运行时及不同阶段的 Device Service 版本。[探针和构建步骤](https://github.com/m5agent/m5stack-esp-emulator/blob/3dae84c4cbce3671eb707f7c562973fef13df078/tests/firmware/sticks3_rtc_slowclk/README.md) · [旧版与候选独立复核](evidence/rtc-slowclk-independent.summary.json) · [最终包及两份 ZIP 摘要](evidence/rtc-frozen-194.summary.json)

## 回归与交付范围

- 默认 RC 深睡探针在同一来宾经历两轮定时唤醒，显式复位后又完成两轮。核对了四次真实 timer 唤醒、深睡复位原因和 RTC 保留状态。
- 在混合浅睡测试中，宿主暂停约 2.6 秒期间未提前唤醒，恢复后返回 timer 唤醒。在另一轮浅睡期间复位，显式继续前只收到 RESET，重新启动后再次进入并完成定时浅睡。
- 原版 All day watch 两种离线操作节奏分别观察 65.103 和 65.115 秒，未发现软件复位或 panic。长按对照取得 suspended、真实语义按键 B、running 和非黑唤醒帧。

Device Service 1.94.0 已完成常驻接口和运行时回读，Reviewer 保持 0.24.0。平台测试执行 2,446 项，2,435 项通过，11 项跳过。隔离来宾与服务均正常退出，临时 Flash 已释放，活动租约为零。RC_FAST/256 定时深睡、外部晶体、其他设备、实体硬件和浏览器来宾为 NOT RUN。未提交 Burner。[Device Service OpenAPI](https://github.com/m5agent/m5stack-esp-emulator/blob/3dae84c4cbce3671eb707f7c562973fef13df078/docs/device-service.openapi.yaml)
