# StickS3 RTC GPIO 浅睡唤醒复验

## 原版和探针

All day watch v0.3.8 的两份历史长按留存均记录 CPU1 IWDT，采样在读取 RTC 睡眠完成标志的代码附近。新一轮使用同一原版下载字节和同一规范化 Flash，通过原生 StickS3 Device Service 会话重放 A 点按、B 点按、B 长按与唤醒动作。GPIO 探针另外用 ESP-IDF 的 `gpio_wakeup_enable`、`esp_sleep_enable_gpio_wakeup`、`esp_light_sleep_start` 和 `esp_sleep_get_wakeup_cause` 验证 GPIO12 低电平及返回原因。[先前的原版留存复核](../2026-11-18-sticks3-watch-retained-watchdog/) · [ESP-IDF RTC 完成标志轮询](https://github.com/espressif/esp-idf/blob/v5.4.1/components/esp_hw_support/port/esp32s3/rtc_sleep.c#L269-L284)

原版长按对照在第一帧后约 4.45 秒按下 B，约 6.73 秒发出释放。快速释放对照的 B 按下和释放间隔约 107 毫秒。GPIO 探针另按会话控制台标记开始等待，再执行 B 键按下和释放。实际输入计划、回执、运行时和 ROM 摘要，以及同会话串口及停止前 ZIP 哈希见证据文件。[原版记录](evidence/all-day-watch-native.summary.json) · [探针对照](evidence/rtc-light-sleep-fixture.summary.json)

复验按 Device Service API 顺序上传原版产物、按 StickS3 合并镜像受理、创建离线 `qemu` 会话并等到首帧，再用同一会话的 `/input` 注入 B 键。每次采样保留 `/frame.png` 与 `/crash`，在停止前读 `/evidence`，以 `purge=0&retain_flash=0` 收尾。[Device Service API](https://github.com/m5agent/m5stack-esp-emulator/blob/7781a8f1a2af4e084dc6e90d1de5d6ac19d553a5/docs/device-service-api.md) · [RTC 模型补丁](https://github.com/m5agent/m5stack-esp-emulator/commit/ed15f0196e1689b0a9f0a9f308d8d672ab2ed83f)

## 原版运行

| 对照 | 实际观测 |
| --- | --- |
| 原生 1.86 基线长按 | 65.109 秒采样窗内，首次记录后端 IWDT stage 0 的采样点为长按后 25.026 秒。来宾虚拟时间距最后喂狗 300.098 毫秒。本次串口无 panic，ROM 上电一次。 |
| 原生 1.86 快速释放 | 65.076 秒采样窗内未观察到 IWDT、panic 或复位。 |
| 寄存器专项诊断候选 | 原版长按仍观察到后端 stage 0。此候选用于定位，记录为独立运行。 |
| 第一份 GPIO 候选 | 观察到 CPU1 IWDT 串口 panic 和一次软件复位。 |
| 第二份 GPIO 候选 | B 键按下后运行时从悬停恢复。原版仍报告 CPU1 IWDT 和一次软件复位。 |
| 第三份 GPIO 候选 | B 键按下后从悬停恢复。65.081 秒窗内只有初次上电，无 stage 0、UART panic 或软件复位。立即唤醒帧与唤醒前相同，停止前 ZIP 中的 135×240 帧随后变化。 |
| 最终 GPIO 运行时 | 同一原版在 B 输入后从悬停恢复。65.098 秒内未观察到后端 stage 0、串口 panic 或软件复位。应用帧在唤醒后变化，会话无新增上电。 |

## GPIO 探针

探针在旧运行时进入 GPIO 睡眠后、任何 B 唤醒输入前发生 CPU0 IWDT。第二份候选在两秒无输入窗内保持悬停，按 B 后报告运行中；直到收尾都无来宾返回。用与探针一一匹配的 ELF 解码三个采样，CPU0 的 PC 在 `panic_handler`，EPC4 在 `rtc_sleep_start`，CPU1 在 IPC 等待。该对照保留 CPU 证据和串口无 panic 行两项观察。

第三份候选在原生非 icount 路径内冻结数字虚拟时钟，保留 RTC 浅睡状态，唤醒时先写入 RTC 的 GPIO 原因及完成状态，再恢复虚拟时钟和 VM。两次探针分别在 2 秒与 5 秒无输入窗中保持 `suspended`，B 按下后变为 `running`。来宾输出 `status=0 cause=7 b_level=0` 及 `RTC_GPIO_SLEEP_PASS`，只记录一次启动。来宾测得的调用内虚拟时间分别为 12261 和 11626 微秒。该时间属于数字模型范围。

最终构建保留相同唤醒路径，并校验 GPIO 拒绝读回与清除。五秒无输入对照在真实 B 键后由来宾报告 `status=0 cause=7 b_level=0 elapsed_us=11754`。独立拒绝探针在首次唤醒后读取仍为低电平的 B，随后立即发出新的浅睡请求。来宾报告 `status=259 cause=0x4 sleep_raw=0x0`，执行拒绝原因清除后读回 `cause=0x0`。全过程只有一次启动。

## 审核可用的语义唤醒

Device Service 1.87.0 候选用同一原版 BIN 和最终 QEMU 构建重新执行长按。进入 `suspended` 后，用 `kind=button`、`control=b`、`action=click` 发一次普通按键请求。回执为 `clock=host`、`hold_seconds=0.12`、`presses=1`、`completion=events_sent`。VM 恢复 `running`，65.088 秒观察窗内无串口 panic、IWDT 或软件复位，停止前取得更新的画面。使用 API 传递输入，实际唤醒由来宾 GPIO 浅睡模型完成。[语义唤醒记录](evidence/device-service-semantic-wake.summary.json) · [输入契约实现](https://github.com/m5agent/m5stack-esp-emulator/commit/018e34048af6a062d01b9bf2960f425e04786414)

独立重启试验把 GPIO 探针保持在浅睡，只终止隔离 Device Service 控制进程。新控制进程采用下一代 worker，并以 `qemu-control-plane` 接管同一会话和同一 QEMU 进程。接管后仍是 `suspended`。B 语义点击随后使其恢复至 `running`，来宾报告 `status=0 cause=7 b_level=0`，且串口只有一次 ROM 启动。正常停止后历史保留、来宾退出、租约归零。该探针以串口判定应用返回。[悬停接管与唤醒记录](evidence/device-service-suspend-reattach.summary.json)

## 证据与范围

每份 ZIP 逐项校验了清单字节、文件摘要及原始串口，绑定所执行设备、来宾与实际运行时。会话保留历史，结束后活动租约归零并释放可变 Flash。固定原版、ROM 与运行时已记录，物理 StickS3、浏览器 WASM、功耗以及其他睡眠和唤醒源暂未验收。旧运行时定时器探针的 CPU0 失败单独保留。测试全程使用离线虚拟会话，Burner 提交数为零。

公开 `main` 已包含 RTC 补丁、可重建探针、四份有界证据和 Device Service 1.87.0 OpenAPI。完整原生外设矩阵通过 70 项。51 项文档检查和四项清单校验通过。本机平台测试 2433 项，2425 项通过，8 项跳过。[公开源码提交](https://github.com/m5agent/m5stack-esp-emulator/commit/d25eae8db848918e9cafebc127a53a0f989941d4) · [RTC 探针复现指南](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/tests/firmware/sticks3_rtc_sleep/README.md) · [Device Service 1.87 OpenAPI](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/docs/device-service.openapi.yaml)
公开提交的 GitHub Actions 平台测试与网络命名空间测试均通过。[同提交 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44219891753)
