# StickS3 RTC 定时、混合浅睡和比较器复验

## 运行环境

RTC 控制器和原版回归使用独立 Device Service 1.87，普通 HTTP 重置使用 1.88 候选。两个服务版本均使用 StickS3 原生 ESP32-S3 QEMU 和离线来宾。每组成对比较固定 ROM 和合并 Flash 的 SHA-256。测试分别使用 ESP-IDF v5.5.4 独立探针及原版 All day watch v0.3.8，每次正常停止后均释放租约。[先前 GPIO 浅睡记录](../../) · [ESP-IDF RTC 寄存器定义](https://github.com/espressif/esp-idf/blob/735507283d5b2f9fb363a1901172dbd9e847945d/components/soc/esp32s3/register/soc/rtc_cntl_reg.h)

原生补丁 `0229` 为 ESP32-S3 建立独立的 48 位 RTC 计数器和比较器。来宾运行时使用虚拟时钟。来宾浅睡时冻结数字时钟并以单调宿主时钟推进 RTC。显式宿主暂停同时冻结定时进度，复位取消两个时钟域的 compare 回调。GPIO 与定时共享 RTC 唤醒路径，主比较器 raw 位保持独立。[运行时与 OpenAPI 源码](https://github.com/m5agent/m5stack-esp-emulator/commit/4fc6ab3b9771cf4b9b42fa4dec6c40f7292302fb)

## 纯定时请求

| 固定固件对照 | 观察 |
| --- | --- |
| Device Service 1.87 原生运行时 | ESP-IDF 探针发出第一次 100 ms 请求，随后 CPU0 中断看门狗，未读取睡眠返回。 |
| 第一份定时候选 | 100 ms、220 ms 两轮均返回 `status=0 cause=4`，来宾测得 99,814 µs、231,518 µs，单次启动。 |
| 第二份候选 | 第一次返回 `status=0 cause=4`，来宾测得 94,730 µs，低于已固定的 95,000 µs 下限 270 µs。按原断言记录 `FAIL`。 |
| 最终构建 | 三次冷启动及一次并行对照共八次请求，均返回 `status=0 cause=4`。100 ms 请求测得 97,572–99,465 µs，220 ms 请求测得 225,292–226,223 µs。每轮只有一次上电。 |

[纯定时和组合来源的同会话证据](evidence/sdk-timer-and-combined.summary.json)

## 清醒时的主比较器

同一独立 ESP-IDF 测试镜像在旧运行时的低 32 位和高 16 位读回失败。两份定时候选均读回 `89abcdef` 与 `5aa5`，写入位 16 后读取不保留该写触发位。只写比较值的对照跨过原定时间。运行时主比较器保持未触发。

之后两份候选都通过已触发目标与仅写入的下一目标独立、主比较器 raw 位 10 拉起、睡眠中断 W1C 保持主比较器位 10，以及主 W1C 将位 10 清除。重新触发的未来比较值取代前次目标。第二份候选的原目标为 85,170 tick，新目标为 130,504 tick，实际观测在 130,708 tick。受控来宾保持清醒，主 RTC CPU 中断被遮蔽。第三份候选重复执行全部检查，实际命中新目标 128,119 后在 128,297 tick 观测到中断。该测试覆盖 raw 状态与清除语义，CPU 中断递送留待单独验证。[清醒比较器复验](evidence/awake-compare.summary.json)

## 定时和 GPIO 共同配置

三份候选均在带两个唤醒源的三次请求中依次通过定时、B 键和定时返回。第一次约 120 ms 定时。第二次设置 2 秒定时，独立观察 QMP `suspended` 后通过普通板级 B 键在旧定时之前唤醒。第三次重新设置 3 秒定时，保持 B 释放并越过旧定时剩余窗口，各次运行都取得新的定时原因。来宾 RTC tick 和校准周期按原始值独立计算，匹配报告的 RTC 微秒数。

已激活 B 键拒绝探针在唤醒后继续保持 B 低电平并尝试新一次浅睡。三份候选都报告 `status=259 cause=0x4 sleep_raw=0x0`，清除原因后读回零。旧 1.4 秒拒绝请求也没有在后续 3 秒等待中提前唤醒来宾。[组合及已激活拒绝回执](evidence/sdk-timer-and-combined.summary.json)

## 独立回归与未通过对照

原版 All day watch 在第一份候选和最终构建均用语义 B 键从 `suspended` 唤醒。两次分别观察 65.085 秒和 65.078 秒，只有一次上电，无 IWDT、UART panic 或软件复位。[原版 GPIO 回归](evidence/original-watch-timer-regression.summary.json)

在两份候选的挂起复位对照中，跨过旧阈值后 VM 仍为 `prelaunch`，显式恢复后未按预期完成新启动与新闹钟唤醒；第二份候选在 `prelaunch` 且显式恢复前读到旧 compare 保持为 `0x00000004c1de`，主比较器 raw 从 `0x0` 升至 `0x400`。对应寄存器和事件分别保留。最终构建复位后保持 `prelaunch`，读回 compare、睡眠状态、raw 和唤醒原因均为零。跨过旧阈值未出现 WAKEUP 事件，显式恢复后共计两次启动和两次新启动的定时返回。[复位与重新触发结果](evidence/reset-rearm-candidates.summary.json)

独立暂停对照在进入第二次浅睡后使 VM 停在 `paused` 2,564 ms，期间只有 STOP 事件。恢复后等待 1,999 ms 才观察到定时唤醒，来宾 RTC 测得 2,003,115 µs、原因 4。该对照有意保持 B 释放，从同一组合探针取定时控制证据。[挂起复位对照](evidence/reset-rearm-candidates.summary.json)

Device Service 1.88 候选另外走了普通 `POST /reset` 路径。发起请求时同一来宾处于 `suspended`。HTTP 返回 `reset=true state=running`，来宾进程与 Device Service 会话保持一致。一次服务复位事件之后，取得第二次启动和第二次新定时返回。QMP 用于观测状态和事件，实际复位与继续由 HTTP 重置请求执行。最后正常清理并释放租约。[普通重置 API 回执](evidence/device-service-timer-reset.summary.json)

最终构建的完整原生外设回归为 70 项通过，五组分别为 13、17、13、14、13 项。

本记录覆盖数字模型的 RTC 控制器数据和 guest 时间读回。物理时序、功耗、深睡和浏览器 WASM 留待各自验证。Burner 提交数为零。

公开 `main` 包含原生定时补丁、挂起会话 HTTP 重置、源码绑定原版与夹具证据，以及 Device Service 1.88.0 OpenAPI。51 项文档检查和四项清单校验通过。[公开源码](https://github.com/m5agent/m5stack-esp-emulator/commit/210c7bcca94c9066f7b839778db25519376879df) · [复现指南](https://github.com/m5agent/m5stack-esp-emulator/blob/210c7bcca94c9066f7b839778db25519376879df/tests/firmware/sticks3_rtc_sleep/README.md) · [Device Service 1.88 OpenAPI](https://github.com/m5agent/m5stack-esp-emulator/blob/210c7bcca94c9066f7b839778db25519376879df/docs/device-service.openapi.yaml)

第一次 GitHub Actions 的网络命名空间检查通过。平台检查在 Linux 的旧 loader 测试断言失败，原因是重置前增加一次 QMP `query-status`，旧断言只接受一次 `system_reset`。该失败与来宾证据一并保留。[首次 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44225725219)

最终源码更新了该测试的 QMP mock 预期，仍校验旧 loader 证明失效，并保持 loader 探测和部署在重置期间均未执行。28 项相关检查通过。这次后续提交只改测试，模拟器和 OpenAPI 字节保持一致。[测试合同修正](https://github.com/m5agent/m5stack-esp-emulator/commit/210c7bcca94c9066f7b839778db25519376879df)

最终提交的 GitHub Actions 平台与网络命名空间检查都通过。使用最终冻结发布包另起隔离实例，普通 HTTP 重置再次通过，同一 QEMU 会话取得第二次启动和第二次新定时返回，事件顺序为 RESET、RESUME、SUSPEND、WAKEUP。完成后租约归零并关闭隔离服务。[最终 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44226763039) · [冻结版本复测](evidence/device-service-timer-reset-frozen-188.summary.json)
