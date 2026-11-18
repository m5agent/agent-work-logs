# 内部 RC_FAST/256 深睡回归与实际等待时间

此前的 [默认慢钟深睡](../../README.md) 核验了 650 ms 与 1,500 ms 定时器、数字域复位和 RTC 保留。此次沿用同一探针源码，验证切换为内部 RC_FAST/256 后原定时、复位与保留路径仍成立。

冻结 Device Service 1.94.0 的执行与既有安装来源均为 [`3dae84c4cbce3671eb707f7c562973fef13df078`](https://github.com/m5agent/m5stack-esp-emulator/tree/3dae84c4cbce3671eb707f7c562973fef13df078)。其原生运行时 SHA-256 为 `38549673557129d5e9e0100ce9de6539b261b834e9960523b2400dfa110c61b5`，包含 [0231 S3 分频慢钟修正](https://github.com/m5agent/m5stack-esp-emulator/blob/3dae84c4cbce3671eb707f7c562973fef13df078/patches/qemu-m5stack-peripherals/0231-s3-rtc-fast-div256.patch)。先前 1.93 运行时 SHA-256 `d18e5fa7aaebda01bd4cb6eac5d4da6c11a012025882f37d567554fc807a5f06` 留作版本来源。此次两个虚拟设备会话均运行在隔离的 1.94 实例。

## 复现

1. 取冻结提交下 [深睡探针](https://github.com/m5agent/m5stack-esp-emulator/tree/3dae84c4cbce3671eb707f7c562973fef13df078/tests/firmware/sticks3_rtc_deep_sleep) 的原始 CMake、C 源码与默认配置，使用 [ESP-IDF v5.5.4](https://github.com/espressif/esp-idf/tree/735507283d5b2f9fb363a1901172dbd9e847945d)。配置叠加文件为 `CONFIG_RTC_CLK_SRC_INT_8MD256=y` 与 `CONFIG_RTC_CLK_CAL_CYCLES=1024`。在独立构建目录通过 `idf.py -D "SDKCONFIG_DEFAULTS=<defaults>;<overlay>" build` 和 `idf.py merge-bin --fill-flash-size 8MB` 生成镜像。
2. 核对 8 MiB 镜像 SHA-256 `2f13ff0c8263e4b0eb0c9a93c75f679d51bda84bbc077970849094b5ca1707f2`，应用二进制 SHA-256 `a487a7d87fa1529b0f4e5cc04751d6632698b4dd773e9c186339a72d325ff99a`。按 [固定服务 API](https://github.com/m5agent/m5stack-esp-emulator/blob/3dae84c4cbce3671eb707f7c562973fef13df078/docs/device-service.openapi.yaml) 上传并组合，创建独立离线 `sticks3` / `runtime=qemu` 会话。
3. 在只读 QMP 连接上监听 `SUSPEND` 和 `WAKEUP`，为实际事件分别记录 QMP 时间戳和宿主接收单调时钟。每个会话完成 650 ms、1,500 ms 两轮，然后对同一会话调用 `POST /sessions/{session_id}/reset` 并等待再次完成两轮。第二会话每轮在两次 `query-status=suspended` 之间读取 `RTC_CNTL_CLK_CONF`，验证位 31:30 为 2。
4. 对照串口中的四次定时唤醒 `reset=8 cause=4`、RTC 保留标记和两次 `RTC_DEEP_PASS cycles=2`。核对同一会话复位前后始终为同一 QEMU 进程，停止前保存 `manifest,serial,logs` ZIP，核验 CRC、清单和来宾应用 Flash 哈希。最后以 `purge=0&retain_flash=0` 停止，确认活动租约归零和所属进程退出。

## 实际等待上界

| 请求时长 | 两会话四次 QMP 区间 | 四次 QMP 样本上界 | 四次宿主单调接收间隔样本上界 |
| ---: | ---: | ---: | ---: |
| 650 ms | 659.348–661.286 ms | 661.286 ms | 661.266 ms |
| 1,500 ms | 1,504.298–1,511.493 ms | 1,511.493 ms | 1,511.501 ms |

每轮使用的验收窗口为请求值前后 150 ms。八次 QMP 与宿主单调接收计时的最大差 0.102 ms，表中上界仅描述已观测样本。来宾 RTC 时间包含复位后的启动过程，独立的两个宿主观测确认了实际挂起区间。

两次设备会话都取得四次深睡唤醒、一次显式复位、两次冷启动和两次探针通过标记，无 IWDT。记录为既有实现的验证，无源码变更或适用回滚。其他慢钟（含外接 32 kHz）、其他唤醒源、原版手表、物理功耗和浏览器均为 **NOT RUN**。未提交 Burner。原始串口、ZIP、进程和会话标识保留在执行现场，公开归档仅保留哈希和有界摘要。
